import re
from typing import Any, Dict, List, Optional

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
            "compiled_patterns": compiled
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

    def match_thought(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Matches focal thought text against registered tool trigger patterns.
        If a pattern matches, returns a structured tool call dictionary.
        """
        if not text:
            return None

        cleaned_text = text.strip()

        for name, tool in self.tools.items():
            for pattern in tool["compiled_patterns"]:
                match = pattern.search(cleaned_text)
                if match:
                    args = {}
                    param_names = list(tool["parameters"].get("properties", {}).keys())
                    
                    groups = match.groups()
                    if groups:
                        # Map regex capture groups to tool parameters in order
                        for idx, val in enumerate(groups):
                            if idx < len(param_names):
                                args[param_names[idx]] = val.strip()
                            else:
                                args[f"arg_{idx}"] = val.strip()
                    else:
                        # Fallback: if match exists but no groups, put cleaned_text in first param
                        if param_names:
                            args[param_names[0]] = cleaned_text

                    # Validate required parameters are present (fallback to whole cleaned_text if missing)
                    required = tool["parameters"].get("required", [])
                    for req in required:
                        if req not in args:
                            args[req] = cleaned_text

                    return {
                        "name": name,
                        "arguments": args
                    }
        return None
