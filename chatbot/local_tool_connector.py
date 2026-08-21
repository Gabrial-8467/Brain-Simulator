import re
from typing import Any, Dict, List, Optional


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9]*", (text or "").lower()))


class ToolConnector:
    def __init__(self):
        # self.tools maps tool_name -> tool_info dict
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        patterns: List[str]
    ) -> None:
        """
        Registers a tool that Aashu can execute.
        
        name: Unique identifier of the tool.
        description: Readable description of what the tool does.
        parameters: JSON Schema dictionary describing expected arguments.
        patterns: Regex or keyword patterns that trigger this tool when matched.
        """
        compiled = []
        for pat in patterns:
            try:
                # Compile case-insensitive pattern matching
                compiled.append(re.compile(pat, re.IGNORECASE))
            except re.error:
                # Fallback to literal if regex compiling fails
                compiled.append(re.compile(re.escape(pat), re.IGNORECASE))
        
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "patterns": patterns,
            "compiled_patterns": compiled,
            "_desc_tokens": _tokens(description),
        }

    def deregister_tool(self, name: str) -> bool:
        if name in self.tools:
            del self.tools[name]
            return True
        return False

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
                "patterns": t["patterns"]
            }
            for t in self.tools.values()
        ]

    def _extract_args(self, tool, match, cleaned_text) -> Dict[str, Any]:
        args = {}
        properties = tool["parameters"].get("properties", {})
        param_names = list(properties.keys())

        # Named groups map directly to parameters by group name.
        named = match.groupdict() if match is not None else {}
        if any(v is not None for v in named.values()):
            for key, val in named.items():
                if val is not None:
                    args[key] = self._cast_arg(key, val, properties.get(key, {}))
            return self._fill_required(args, tool, cleaned_text)

        groups = match.groups() if match is not None else ()
        if groups:
            # Map regex capture groups to tool parameters in order
            for idx, val in enumerate(groups):
                if val is None:
                    continue
                if idx < len(param_names):
                    args[param_names[idx]] = self._cast_arg(param_names[idx], val.strip(), properties.get(param_names[idx], {}))
                else:
                    args[f"arg_{idx}"] = val.strip()
        else:
            # Fallback: if match exists but no groups, put cleaned_text in first param
            if param_names:
                args[param_names[0]] = self._cast_arg(param_names[0], cleaned_text, properties.get(param_names[0], {}))

        return self._fill_required(args, tool, cleaned_text)

    @staticmethod
    def _fill_required(args, tool, cleaned_text):
        # Validate required parameters are present (fallback to whole cleaned_text if missing)
        required = tool["parameters"].get("required", [])
        for req in required:
            if req not in args:
                args[req] = cleaned_text
        return args

    @staticmethod
    def _cast_arg(name: str, value: str, prop: Dict[str, Any]) -> Any:
        """Cast captured strings to typed values when the parameter expects a number."""
        value = value.strip()
        if not value.isdigit():
            return value
        desc = str(prop.get("description", "")).lower()
        name_hint = name.lower()
        numeric_hint = any(h in desc or h in name_hint for h in (
            "second", "minute", "hour", "amount", "percentage", "percent",
            "number", "count", "quantity", "index", "id",
        ))
        if numeric_hint and prop.get("type") == "integer":
            return int(value)
        return value

    def resolve(self, text: str, min_confidence: float = 0.2) -> Optional[Dict[str, Any]]:
        """Best-match tool resolution.

        Scores every registered tool by:
        - exact regex pattern hits (strongest signal, confidence 1.0)
        - description keyword overlap with the query (weak signal)
        Returns the highest-confidence tool call or None.
        """
        if not text:
            return None

        cleaned_text = text.strip()
        query_tokens = _tokens(cleaned_text)

        best = None
        for name, tool in self.tools.items():
            pattern_hits = 0
            matched_args = {}
            matched = False
            matched_span = 0
            for pattern in tool["compiled_patterns"]:
                match = pattern.search(cleaned_text)
                if match:
                    pattern_hits += 1
                    matched = True
                    span = match.end() - match.start()
                    # The most specific (longest) matching pattern owns the args.
                    if span >= matched_span:
                        matched_span = span
                        matched_args = self._extract_args(tool, match, cleaned_text)

            if matched:
                confidence = 1.0
                args = matched_args
            else:
                # Weak signal: shared tokens between the query and the tool description
                if not query_tokens or not tool.get("_desc_tokens"):
                    continue
                overlap = len(query_tokens & tool["_desc_tokens"])
                if overlap == 0:
                    continue
                confidence = min(0.5, 0.1 * overlap)
                args = self._extract_args(tool, re.match(r".*", cleaned_text), cleaned_text)

            if confidence < min_confidence:
                continue

            if best is None:
                best = {
                    "name": name,
                    "arguments": args,
                    "confidence": round(confidence, 2),
                    "_span": matched_span,
                }
                continue

            # Prefer higher confidence; on ties, prefer the most specific (longest) match
            if confidence > best["confidence"] or (
                confidence == best["confidence"] and matched_span > best["_span"]
            ):
                best = {
                    "name": name,
                    "arguments": args,
                    "confidence": round(confidence, 2),
                    "_span": matched_span,
                }

        if best is not None:
            best.pop("_span", None)
        return best

    def match_thought(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Matches focal thought text against registered tool trigger patterns.
        If a pattern matches, returns a structured tool call dictionary.
        """
        result = self.resolve(text)
        if result is None:
            return None
        return {
            "name": result["name"],
            "arguments": result["arguments"],
        }
