import re
from collections import Counter

LANGUAGE_ALIASES = {
    "py": "python", "python3": "python", "python2": "python",
    "js": "javascript", "node": "javascript", "nodejs": "javascript", "javascripts": "javascript",
    "ts": "typescript",
    "cpp": "c++", "cplusplus": "c++",
    "csharp": "c#",
    "golang": "go",
    "sh": "shell", "bash": "shell", "shellscript": "shell",
}

LANGUAGES = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby",
    "php", "swift", "kotlin", "html", "css", "sql", "bash", "shell", "lua", "dart",
    "r", "matlab", "scala", "perl", "haskell", "elixir", "cobol",
]

CONCEPT_KEYWORDS = [
    "react", "django", "flask", "node", "pandas", "numpy", "api", "oop", "function",
    "algorithm", "code", "coding", "programming", "variable", "loop", "class", "import",
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been",
    "to", "of", "in", "on", "for", "with", "about", "from", "as", "at", "by", "it",
    "its", "this", "that", "these", "those", "you", "your", "i", "we", "they", "he",
    "she", "them", "his", "her", "their", "our", "my", "me", "us", "what", "which",
    "how", "why", "when", "where", "who", "can", "could", "will", "would", "should",
    "do", "does", "did", "has", "have", "had", "not", "no", "yes", "just", "so", "if",
    "then", "than", "too", "very", "also", "any", "all", "each", "some", "such",
    "more", "most", "other", "only", "own", "same", "use", "used", "using", "get",
    "got", "make", "like", "want", "need", "one", "two", "new", "now", "the",
}

MAX_SNIPPETS_PER_LANGUAGE = 20


def normalize_language(name):
    key = (name or "").strip().lower()
    return LANGUAGE_ALIASES.get(key, key)


def _lang_pattern(lang):
    if re.fullmatch(r"[a-zA-Z0-9]+", lang):
        return r"(?<!\w)" + re.escape(lang) + r"(?!\w)"
    return re.escape(lang)


def detect_language(text):
    if not text:
        return None
    lowered = text.lower()
    for lang in sorted(LANGUAGES, key=len, reverse=True):
        if re.search(_lang_pattern(lang), lowered):
            return normalize_language(lang)
    for kw in sorted(CONCEPT_KEYWORDS, key=len, reverse=True):
        if kw in lowered:
            return kw
    return None


def _reference_comments(snippets):
    comments = []
    for snippet in snippets[:2]:
        clean = snippet.replace("\n", " ")
        if clean:
            comments.append(f"# Reference learned: {clean[:140]}")
    return "\n".join(comments) + "\n" if comments else ""


PY_TEMPLATES = {
    "hello": "def main():\n    print(\"Hello, world!\")\n\nif __name__ == \"__main__\":\n    main()\n",
    "math": "def main():\n    numbers = [1, 2, 3, 4, 5]\n    total = sum(numbers)\n    print(f\"Result: {total}\")\n\nif __name__ == \"__main__\":\n    main()\n",
    "loop": "def main():\n    items = [\"alpha\", \"bravo\", \"charlie\"]\n    for item in items:\n        print(item)\n\nif __name__ == \"__main__\":\n    main()\n",
    "file": "def main():\n    with open(\"output.txt\", \"w\") as f:\n        f.write(\"Hello from generated code!\\n\")\n\nif __name__ == \"__main__\":\n    main()\n",
    "function": "def compute(a, b):\n    return a + b\n\ndef main():\n    result = compute(3, 4)\n    print(f\"Result: {result}\")\n\nif __name__ == \"__main__\":\n    main()\n",
    "default": "def main():\n    task = {task!r}\n    print(f\"Executing task: {task}\")\n\nif __name__ == \"__main__\":\n    main()\n",
}

JS_TEMPLATES = {
    "hello": "console.log('Hello, world!');",
    "math": "const numbers = [1, 2, 3, 4, 5];\nconst total = numbers.reduce((s, n) => s + n, 0);\nconsole.log(`Result: ${total}`);",
    "loop": "const items = ['alpha', 'bravo', 'charlie'];\nfor (const item of items) { console.log(item); }",
    "default": "// Generated JavaScript for the task.\nconsole.log('Task complete');",
}

SHELL_TEMPLATES = {
    "hello": 'echo "Hello, world!"',
    "math": 'echo "Result: $((1 + 2 + 3))"',
    "loop": 'for i in alpha bravo charlie; do echo "$i"; done',
    "default": "# Generated shell script for the task.\necho \"Task complete\"",
}

TASK_INTENTS = [
    ("hello", ["hello", "greet", "welcome", "good morning"]),
    ("math", ["calculate", "compute", "math", "sum", "add", "average", "area", "plus"]),
    ("loop", ["loop", "iterate", "repeat", "count", "for each", "list of"]),
    ("file", ["write file", "save file", "create file", "read file", "load file"]),
    ("function", ["function", "method", "define a", "reusable"]),
]


def _detect_intent(task):
    lowered = " " + task.lower().strip() + " "
    for name, keywords in TASK_INTENTS:
        for kw in keywords:
            if kw in lowered:
                return name
    return "default"


class LanguageCortex:
    """The brain's language-learning center.

    Tracks which programming languages the brain has learned (from learning
    experiences ingested through perception), can summarize text, and can only
    generate code for languages it has actually learned.
    """

    def __init__(self):
        self.languages = {}

    def knows(self, language):
        return normalize_language(language) in self.languages

    def known_languages(self):
        return sorted(self.languages.keys())

    def learn(self, language, content, source="learning"):
        lang = normalize_language(language)
        entry = self.languages.setdefault(lang, {"snippets": [], "source": source, "entries": 0})
        entry["entries"] = int(entry.get("entries", 0)) + 1
        if source and entry["source"] == "learning":
            entry["source"] = source
        snippet = (content or "").strip()
        if snippet and (not entry["snippets"] or entry["snippets"][-1] != snippet):
            entry["snippets"].append(snippet[:500])
            entry["snippets"] = entry["snippets"][-MAX_SNIPPETS_PER_LANGUAGE:]
        return lang

    def ingest_event(self, content, source="learning"):
        lang = detect_language(content)
        if lang:
            return self.learn(lang, content, source)
        return None

    def summarize(self, text, max_sentences=4):
        """Deterministic extractive summarization owned by the brain."""
        if not text or not text.strip():
            return ""
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.strip()) >= 20]
        if not sentences:
            sentences = [text.strip()]

        words = re.findall(r"[a-zA-Z]+", text.lower())
        freq = Counter(w for w in words if w not in STOPWORDS and len(w) > 1)
        max_freq = max(freq.values()) if freq else 1

        scored = []
        for s in sentences:
            sw = re.findall(r"[a-zA-Z]+", s.lower())
            if not sw:
                continue
            score = sum(freq[w] / max_freq for w in sw if w in freq) / len(sw)
            scored.append((score, len(s), s))
        scored.sort(key=lambda t: (-t[0], t[1]))
        top = [t[2] for t in scored[:max_sentences]]

        ordered = [s for s in sentences if s in top]
        return " ".join(ordered) if ordered else sentences[0][:400]

    def generate_code(self, task, language):
        """Generate code ONLY for a language the brain has learned."""
        lang = normalize_language(language)
        if not self.knows(lang):
            return False, f"I have not learned {language} yet. Ask me to learn it from the internet first."
        code = self._build_code(task, lang)
        return True, code

    def _build_code(self, task, lang):
        intent = _detect_intent(task)
        ref = _reference_comments(self.languages.get(lang, {}).get("snippets", []))
        if lang == "python":
            body = PY_TEMPLATES.get(intent, PY_TEMPLATES["default"].format(task=task))
        elif lang == "javascript":
            body = JS_TEMPLATES.get(intent, JS_TEMPLATES["default"])
        elif lang in ("shell", "bash"):
            body = SHELL_TEMPLATES.get(intent, SHELL_TEMPLATES["default"])
        else:
            body = (
                f"# Generated {lang} code for task: {task}\n"
                f"# Learned: {int(self.languages.get(lang, {}).get('entries', 0))} examples\n"
                f"print('Generated {lang} stub.')"
            )
        return ref + body

    def to_state(self):
        return {
            lang: {
                "source": entry.get("source", "learning"),
                "entries": int(entry.get("entries", 0)),
                "snippets": list(entry.get("snippets", [])),
            }
            for lang, entry in self.languages.items()
        }

    def load_state(self, state):
        if not isinstance(state, dict):
            return
        self.languages = {
            lang: {
                "source": entry.get("source", "learning") if isinstance(entry, dict) else "learning",
                "entries": int(entry.get("entries", 0)) if isinstance(entry, dict) else 0,
                "snippets": list(entry.get("snippets", [])) if isinstance(entry, dict) else [],
            }
            for lang, entry in state.items()
        }
