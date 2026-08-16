import re
from collections import Counter

LANGUAGE_ALIASES = {
    "py": "python", "python3": "python", "python2": "python",
    "js": "javascript", "javascripts": "javascript", "node.js": "nodejs",
    "ts": "typescript",
    "react": "reactjs", "react.js": "reactjs",
    "vue": "vuejs", "vue.js": "vuejs",
    "next": "nextjs", "next.js": "nextjs",
    "node": "nodejs",
    "expressjs": "express", "express.js": "express",
    "fastifyjs": "fastify", "fastify.js": "fastify",
    "nest": "nestjs",
    "cpp": "c++", "cplusplus": "c++",
    "csharp": "c#",
    "golang": "go",
    "sh": "shell", "bash": "shell", "shellscript": "shell",
    "mongodb": "nosql", "mongo": "nosql", "couchdb": "nosql", "redis": "nosql",
    "mysql": "sql", "postgresql": "sql", "postgres": "sql", "sqlite": "sql",
    "beautifulsoup4": "beautifulsoup", "bs4": "beautifulsoup",
    "sklearn": "scikit-learn", "tf": "tensorflow",
}

LANGUAGES = [
    # Core languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "html", "css", "sql", "bash", "shell",
    "lua", "dart", "r", "matlab", "scala", "perl", "haskell", "elixir", "cobol",
    # JavaScript ecosystem (frameworks, runtimes, libraries)
    "nodejs", "reactjs", "angular", "vuejs", "nextjs", "svelte", "electron",
    "express", "fastify", "nestjs", "jest", "threejs",
    # Bare-name aliases so detection normalizes them to their dialect
    "react", "vue", "node",
    # Python ecosystem (libraries and frameworks)
    "django", "flask", "fastapi", "pandas", "numpy", "matplotlib", "requests",
    "beautifulsoup", "selenium", "scikit-learn", "tensorflow", "pytorch",
    # Query and data stores
    "nosql", "mongo", "mongodb",
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
    explicit = re.search(r"(?:programming language|language of)\s+([a-z0-9_#+]+)", lowered)
    if explicit:
        name = explicit.group(1).strip()
        matched = normalize_language(name)
        if matched in {normalize_language(l) for l in LANGUAGES}:
            return matched
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

JSX_TEMPLATES = {
    "hello": (
        "export default function App() {\n"
        "  return <h1>Hello, world!</h1>;\n"
        "}\n"
    ),
    "math": (
        "export default function App() {\n"
        "  const numbers = [1, 2, 3, 4, 5];\n"
        "  const total = numbers.reduce((s, n) => s + n, 0);\n"
        "  return <p>Result: {total}</p>;\n"
        "}\n"
    ),
    "default": (
        "export default function App() {\n"
        "  return <div>Generated React component.</div>;\n"
        "}\n"
    ),
}

TS_TEMPLATES = {
    "hello": (
        "function greet(name: string): string {\n"
        "  return `Hello, ${name}!`;\n"
        "}\n"
        "console.log(greet('world'));\n"
    ),
    "math": (
        "const numbers: number[] = [1, 2, 3, 4, 5];\n"
        "const total = numbers.reduce((s, n) => s + n, 0);\n"
        "console.log(`Result: ${total}`);\n"
    ),
    "default": (
        "interface Task { name: string; done: boolean }\n"
        "const task: Task = { name: 'sample', done: false };\n"
        "console.log(task);\n"
    ),
}

VUE_TEMPLATES = {
    "hello": (
        "<template>\n  <h1>Hello, world!</h1>\n</template>\n"
        "<script>\nexport default { name: 'App' };\n</script>\n"
    ),
    "default": (
        "<template>\n  <p>{{ message }}</p>\n</template>\n"
        "<script>\nexport default {\n"
        "  data() { return { message: 'Generated Vue component' }; },\n"
        "};\n</script>\n"
    ),
}

NODE_TEMPLATES = {
    "hello": (
        "const http = require('http');\n"
        "http.createServer((req, res) => {\n"
        "  res.end('Hello, world!');\n"
        "}).listen(3000);\n"
    ),
    "default": (
        "// Generated Node.js script.\n"
        "const http = require('http');\n"
        "http.createServer((req, res) => {\n"
        "  res.end('ok');\n"
        "}).listen(3000);\n"
    ),
}

SERVER_TEMPLATES = {
    "hello": (
        "const express = require('express');\n"
        "const app = express();\n"
        "app.get('/', (req, res) => res.send('Hello, world!'));\n"
        "app.listen(3000, () => console.log('Listening on :3000'));\n"
    ),
    "default": (
        "// Generated API server.\n"
        "const express = require('express');\n"
        "const app = express();\n"
        "app.get('/', (req, res) => res.json({ ok: true }));\n"
        "app.listen(3000);\n"
    ),
}

PYTHON_WEB_TEMPLATES = {
    "flask": (
        "from flask import Flask\n"
        "app = Flask(__name__)\n"
        "@app.route('/')\n"
        "def home():\n"
        "    return 'Hello, world!'\n"
        "if __name__ == '__main__':\n"
        "    app.run(debug=True)\n"
    ),
    "django": (
        "# Add this app to INSTALLED_APPS and run 'python manage.py migrate'.\n"
        "from django.http import HttpResponse\n"
        "def index(request):\n"
        "    return HttpResponse('Hello, world!')\n"
    ),
    "fastapi": (
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.get('/')\n"
        "def root():\n"
        "    return {'message': 'Hello, world!'}\n"
    ),
}

PYTHON_LIB_TEMPLATES = {
    "pandas": (
        "import pandas as pd\n"
        "df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})\n"
        "print(df.describe())\n"
    ),
    "numpy": (
        "import numpy as np\n"
        "a = np.array([1, 2, 3, 4, 5])\n"
        "print(np.sum(a))\n"
    ),
    "matplotlib": (
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "x = np.linspace(0, 10, 100)\n"
        "plt.plot(x, np.sin(x))\n"
        "plt.show()\n"
    ),
    "requests": (
        "import requests\n"
        "r = requests.get('https://api.example.com')\n"
        "print(r.status_code)\n"
    ),
    "beautifulsoup": (
        "from bs4 import BeautifulSoup\n"
        "soup = BeautifulSoup(html, 'html.parser')\n"
        "print(soup.get_text())\n"
    ),
    "selenium": (
        "from selenium import webdriver\n"
        "browser = webdriver.Chrome()\n"
        "browser.get('https://example.com')\n"
        "browser.quit()\n"
    ),
    "scikit-learn": (
        "from sklearn.ensemble import RandomForestClassifier\n"
        "model = RandomForestClassifier()\n"
        "print(model)\n"
    ),
    "tensorflow": (
        "import tensorflow as tf\n"
        "model = tf.keras.Sequential([tf.keras.layers.Dense(1)])\n"
        "print(model.summary())\n"
    ),
    "pytorch": (
        "import torch\n"
        "x = torch.tensor([1.0, 2.0, 3.0])\n"
        "print(x.mean())\n"
    ),
}

NOSQL_TEMPLATES = {
    "hello": "db.users.insertOne({ hello: 'world' })\n",
    "default": (
        "// Generated NoSQL (MongoDB) queries.\n"
        "db.users.insertOne({ name: 'sample', active: true });\n"
        "db.users.find({ active: true });\n"
    ),
}

COMMENT_STYLE = {
    "python": "#", "ruby": "#", "shell": "#", "bash": "#", "perl": "#", "elixir": "#",
    "javascript": "//", "typescript": "//", "nodejs": "//", "reactjs": "//", "angular": "//",
    "vuejs": "//", "nextjs": "//", "svelte": "//", "electron": "//", "express": "//",
    "fastify": "//", "nestjs": "//", "jest": "//", "threejs": "//",
    "java": "//", "c++": "//", "c#": "//", "go": "//", "rust": "//", "swift": "//",
    "kotlin": "//", "scala": "//", "dart": "//", "php": "//",
    "sql": "--", "nosql": "//", "lua": "--", "haskell": "--", "r": "#", "matlab": "%",
    "cobol": "*", "html": "<!-- ", "css": "/* ",
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
        elif lang == "reactjs":
            body = JSX_TEMPLATES.get(intent, JSX_TEMPLATES["default"])
        elif lang in ("angular", "typescript"):
            body = TS_TEMPLATES.get(intent, TS_TEMPLATES["default"])
        elif lang == "vuejs":
            body = VUE_TEMPLATES.get(intent, VUE_TEMPLATES["default"])
        elif lang == "nextjs":
            body = JSX_TEMPLATES["default"].replace(
                "Generated React component.", "Generated Next.js page."
            )
        elif lang == "nodejs":
            body = NODE_TEMPLATES.get(intent, NODE_TEMPLATES["default"])
        elif lang in ("express", "fastify", "nestjs"):
            body = SERVER_TEMPLATES.get(intent, SERVER_TEMPLATES["default"])
        elif lang in ("django", "flask", "fastapi"):
            body = PYTHON_WEB_TEMPLATES.get(lang, PYTHON_WEB_TEMPLATES["flask"])
        elif lang in PYTHON_LIB_TEMPLATES:
            body = PYTHON_LIB_TEMPLATES[lang]
        elif lang == "nosql":
            body = NOSQL_TEMPLATES.get(intent, NOSQL_TEMPLATES["default"])
        else:
            comment = COMMENT_STYLE.get(lang, "#")
            if lang == "html":
                comment = "<!--"
                close = "-->"
            elif lang == "css":
                comment = "/*"
                close = "*/"
            else:
                close = ""
            body = (
                f"{comment} Generated {lang} code for task: {task}{close}\n"
                f"{comment} Learned: {int(self.languages.get(lang, {}).get('entries', 0))} examples{close}\n"
                f"{comment} Minimal {lang} stub.{close}"
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
