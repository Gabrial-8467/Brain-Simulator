import re

PY_TASKS = {
    "hello": ("greet", ["hello", "greet", "welcome", "hi ", "good morning"]),
    "math": ("compute a calculation", ["calculate", "compute", "math", "sum", "add", "average", "area", "add ", "plus"]),
    "loop": ("iterate over items", ["loop", "iterate", "repeat", "count", "for each", "list of"]),
    "file_write": ("write data to a file", ["write file", "save file", "create file", "write to file"]),
    "file_read": ("read data from a file", ["read file", "load file", "read from file"]),
    "function": ("define a reusable function", ["function", "method", "define a", "reusable"]),
    "fibonacci": ("print the fibonacci sequence", ["fibonacci", "fib"]),
    "sort": ("sort a collection", ["sort", "sorted", "order"]),
}

DEFAULT_PY = '''def main():
    task = {task!r}
    print(f"Executing task: {task}")

if __name__ == "__main__":
    main()
'''

PY_TEMPLATES = {
    "hello": '''def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
''',
    "math": '''def main():
    numbers = [1, 2, 3, 4, 5]
    total = sum(numbers)
    print(f"Result: {total}")

if __name__ == "__main__":
    main()
''',
    "loop": '''def main():
    items = ["alpha", "bravo", "charlie"]
    for item in items:
        print(item)

if __name__ == "__main__":
    main()
''',
    "file_write": '''def main():
    with open("output.txt", "w") as f:
        f.write("Hello from generated code!\\n")

if __name__ == "__main__":
    main()
''',
    "file_read": '''def main():
    with open("output.txt", "r") as f:
        content = f.read()
    print(content)

if __name__ == "__main__":
    main()
''',
    "function": '''def compute(a, b):
    return a + b

def main():
    result = compute(3, 4)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
''',
    "fibonacci": '''def main():
    a, b = 0, 1
    for _ in range(10):
        print(a)
        a, b = b, a + b

if __name__ == "__main__":
    main()
''',
    "sort": '''def main():
    items = [5, 2, 8, 1, 9]
    items.sort()
    print(items)

if __name__ == "__main__":
    main()
''',
}

JS_TEMPLATES = {
    "hello": "console.log('Hello, world!');",
    "math": "const numbers = [1, 2, 3, 4, 5];\nconst total = numbers.reduce((s, n) => s + n, 0);\nconsole.log(`Result: ${total}`);",
    "loop": "const items = ['alpha', 'bravo', 'charlie'];\nfor (const item of items) { console.log(item); }",
    "default": "// Generated JavaScript for the task.\nconsole.log('Task complete');",
}

SHELL_TEMPLATES = {
    "hello": 'echo "Hello, world!"',
    "math": "echo \"Result: $((1 + 2 + 3))\"",
    "loop": "for i in alpha bravo charlie; do echo \"$i\"; done",
    "default": "# Generated shell script for the task.\necho \"Task complete\"",
}


def detect_intent(task):
    lowered = " " + task.lower().strip() + " "
    for name, (_, keywords) in PY_TASKS.items():
        for kw in keywords:
            if kw in lowered:
                return name
    return "default"


def _reference_comments(knowledge, language):
    comments = []
    if not knowledge:
        return ""
    for item in knowledge[:2]:
        content = (item.get("content") or "").strip().replace("\n", " ")
        if content:
            comments.append(f"# Reference learned: {content[:140]}")
    return "\n".join(comments) + "\n" if comments else ""


class AashuCodeGenerator:
    """Deterministic code generator driven by Aashu's learned knowledge.
    Emits safe, runnable template code matching the task intent and language;
    learned snippets are attached as reference comments so learning steers output."""

    def generate(self, task, language="python", knowledge=None):
        lang = (language or "python").strip().lower()
        intent = detect_intent(task)
        ref = _reference_comments(knowledge, lang)

        if lang in ("python", "py"):
            body = PY_TEMPLATES.get(intent, DEFAULT_PY.format(task=task))
        elif lang in ("javascript", "js", "node", "typescript"):
            body = JS_TEMPLATES.get(intent, JS_TEMPLATES["default"])
        elif lang in ("bash", "shell", "sh"):
            body = SHELL_TEMPLATES.get(intent, SHELL_TEMPLATES["default"])
        else:
            body = (
                f"# Generated {lang} code for task: {task}\n"
                f"# Aashu code generator supports python, javascript and shell templates.\n"
                f"print('Aashu offline code generator active.')"
            )
        return ref + body
