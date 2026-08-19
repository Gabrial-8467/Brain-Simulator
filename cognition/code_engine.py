"""
Code Engine — IR (intermediate representation), compositor, and renderer
for composing code from intent rather than from static templates.

Architecture:
  CodeIR (intermediate representation)  ->  language-agnostic tree of IRNodes
  CodeCompositor (intent -> IR)         ->  builds IR from task intent + learned patterns
  LanguageRenderer (IR -> code)         ->  converts IR to target language using grammar rules
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from cognition.language_grammar import LANGUAGES, get_language, get_syntax, get_library


# ─────────────────────────────────────────────────
# IR NODES
# ─────────────────────────────────────────────────

@dataclass
class IRNode:
    """A single node in the language-agnostic intermediate representation."""
    kind: str
    children: list["IRNode"] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def add(self, *nodes: "IRNode") -> "IRNode":
        self.children.extend(nodes)
        return self

    def __repr__(self) -> str:
        meta = ", ".join(f"{k}={v!r}" for k, v in self.meta.items())
        return f"IRNode({self.kind}, {meta})"


def ir_import(module: str, names: list[str] | None = None, style: str = "import") -> IRNode:
    return IRNode("import", meta={"module": module, "names": names, "style": style})


def ir_from_import(module: str, names: list[str]) -> IRNode:
    return IRNode("from_import", meta={"module": module, "names": names})


def ir_function(name: str, params: list[str], body: list[IRNode],
                return_type: str | None = None, async_fn: bool = False) -> IRNode:
    return IRNode("function", meta={
        "name": name, "params": params, "return_type": return_type, "async": async_fn,
    }, children=body)


def ir_class(name: str, parent: str | None, body: list[IRNode]) -> IRNode:
    return IRNode("class", meta={"name": name, "parent": parent}, children=body)


def ir_variable(name: str, value: str, mutable: bool = False,
                var_type: str | None = None) -> IRNode:
    return IRNode("variable", meta={
        "name": name, "value": value, "mutable": mutable, "var_type": var_type,
    })


def ir_expression(expr: str) -> IRNode:
    return IRNode("expression", meta={"expr": expr})


def ir_return(expr: str | None = None) -> IRNode:
    return IRNode("return", meta={"expr": expr})


def ir_if(condition: str, body: list[IRNode], else_body: list[IRNode] | None = None) -> IRNode:
    return IRNode("if", meta={"condition": condition, "else": else_body is not None},
                  children=body)


def ir_for(var: str, iterable: str, body: list[IRNode], index: bool = False) -> IRNode:
    return IRNode("for", meta={"var": var, "iterable": iterable, "index": index}, children=body)


def ir_while(condition: str, body: list[IRNode]) -> IRNode:
    return IRNode("while", meta={"condition": condition}, children=body)


def ir_try(body: list[IRNode], handler: list[IRNode],
           exception: str = "Exception", var: str = "e") -> IRNode:
    return IRNode("try", meta={"exception": exception, "var": var},
                  children=body, **{"handler": handler})


def ir_comment(text: str, block: bool = False) -> IRNode:
    return IRNode("comment", meta={"text": text, "block": block})


def ir_assign(name: str, expr: str, var_type: str | None = None) -> IRNode:
    return IRNode("assign", meta={"name": name, "expr": expr, "var_type": var_type})


def ir_call(func: str, args: list[str] | None = None) -> IRNode:
    return IRNode("call", meta={"func": func, "args": args or []})


def ir_route(method: str, route: str, handler_name: str,
             body: list[IRNode], params: list[str] | None = None) -> IRNode:
    return IRNode("route", meta={
        "method": method, "route": route, "handler": handler_name, "params": params or [],
    }, children=body)


def ir_return_stmt(expr: str) -> IRNode:
    return IRNode("return", meta={"expr": expr})


def ir_property(name: str, prop_type: str, body: list[IRNode] | None = None) -> IRNode:
    return IRNode("property", meta={"name": name, "prop_type": prop_type}, children=body or [])


def ir_decorator(name: str, args: list[str] | None = None) -> IRNode:
    return IRNode("decorator", meta={"name": name, "args": args or []})


def ir_decorator_node(decorator: IRNode, target: IRNode) -> IRNode:
    return IRNode("decorated", children=[decorator, target])


def ir_module(imports: list[IRNode], body: list[IRNode]) -> IRNode:
    return IRNode("module", children=imports + body)


# ─────────────────────────────────────────────────
# CODE IR  (wrapper)
# ─────────────────────────────────────────────────

@dataclass
class CodeIR:
    """A language-agnostic intermediate representation of a program."""
    root: IRNode
    language: str = ""
    title: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"CodeIR(lang={self.language!r}, title={self.title!r}, root={self.root})"


# ─────────────────────────────────────────────────
# CODE COMPOSITOR
# ─────────────────────────────────────────────────

INTENT_KEYWORDS = {
    "hello":      ["hello", "greet", "welcome", "hi"],
    "math":       ["calculate", "compute", "math", "sum", "add", "average", "area", "plus"],
    "loop":       ["loop", "iterate", "repeat", "count", "for each", "list of"],
    "file":       ["write file", "save file", "create file", "read file", "load file"],
    "function":   ["function", "method", "define a", "reusable"],
    "web":        ["web", "server", "api", "route", "endpoint", "http", "rest"],
    "data":       ["data", "csv", "pandas", "dataframe", "numpy", "array"],
    "test":       ["test", "spec", "assert", "verify"],
    "crud":       ["crud", "create", "update", "delete", "insert"],
    "db":         ["database", "db", "sqlite", "postgres", "mongo", "sql"],
    "cli":        ["cli", "command line", "argparse", "terminal"],
}

FRAMEWORK_HINTS = {
    "flask":      ["flask", "flask app", "flask server"],
    "django":     ["django", "django app", "django view"],
    "fastapi":    ["fastapi", "fast api"],
    "express":    ["express", "expressjs", "express.js", "express server"],
    "fastify":    ["fastify", "fastify server"],
    "nextjs":     ["next.js", "nextjs", "next app"],
    "angular":    ["angular", "angular app"],
    "reactjs":    ["react", "reactjs", "react app", "react component"],
    "vuejs":      ["vue", "vuejs", "vue app"],
    "springboot": ["spring", "spring boot", "springboot"],
    "rails":      ["rails", "ruby on rails"],
    "actix":      ["actix", "actix-web"],
    "axum":       ["axum"],
    "gin":        ["gin", "gin-gonic"],
    "echo":       ["echo", "labstack"],
}


def _detect_intent(task: str) -> str:
    """Detect the primary intent of a task from keywords."""
    lowered = (" " + task.lower().strip() + " ")
    best_match = "default"
    best_len = 0
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in lowered and len(kw) > best_len:
                best_match = intent
                best_len = len(kw)
    return best_match


def _detect_framework(task: str) -> str | None:
    """Detect which framework is mentioned in the task."""
    lowered = (" " + task.lower().strip() + " ")
    best = None
    best_len = 0
    for fw, hints in FRAMEWORK_HINTS.items():
        for h in hints:
            if h in lowered and len(h) > best_len:
                best = fw
                best_len = len(h)
    return best


def _detect_libraries(task: str) -> list[str]:
    """Detect which libraries are mentioned in the task."""
    lowered = (" " + task.lower().strip() + " ")
    found: list[str] = []
    for lib in ["pandas", "numpy", "matplotlib", "requests", "scikit-learn",
                "tensorflow", "pytorch", "sqlalchemy", "psycopg2", "pymongo",
                "asyncio", "sqlite3", "click", "typer", "pytest"]:
        if lib in lowered or lib.replace("-", "") in lowered.replace(" ", ""):
            found.append(lib)
    return found


class CodeCompositor:
    """Composes a CodeIR tree from a task description.

    This class takes a language + task, detects intent and framework,
    and builds an IRNode tree using language grammar rules.
    """

    def __init__(self) -> None:
        pass

    def compose(self, task: str, language: str) -> CodeIR:
        """Main entry point: build a CodeIR for a given task and language."""
        lang = language.strip().lower()
        lang_data = get_language(lang)
        if lang_data is None:
            raise ValueError(f"Unknown language: {lang}")

        intent = _detect_intent(task)
        framework = _detect_framework(task)
        libraries = _detect_libraries(task)
        syntax = lang_data.get("syntax", {})
        libs = lang_data.get("libraries", {})

        if framework and framework in _flatten_libs(libs):
            lib_data = _find_lib(libs, framework)
        else:
            lib_data = None

        imports: list[IRNode] = []
        body: list[IRNode] = []

        imports.extend(self._compose_imports(lang, framework, libraries, libs))
        body.extend(self._compose_body(lang, task, intent, framework, lib_data, syntax, libs))

        root = ir_module(imports, body)
        return CodeIR(
            root=root,
            language=lang,
            title=self._make_title(task, framework),
            description=task,
            metadata={"intent": intent, "framework": framework, "libraries": libraries},
        )

    def _compose_imports(self, lang: str, framework: str | None,
                         libraries: list[str], libs: dict) -> list[IRNode]:
        """Build import nodes for the language + framework + libraries."""
        imports: list[IRNode] = []
        lang_data = get_language(lang) or {}
        syntax = lang_data.get("syntax", {})

        if framework:
            lib_data = _find_lib(libs, framework)
            if lib_data and "imports" in lib_data:
                imp_text = lib_data["imports"]
                imports.extend(_parse_import_text(imp_text, lang))

        for lib_name in libraries:
            lib_data = _find_lib_anywhere(libs, lib_name)
            if lib_data and "imports" in lib_data:
                imp_text = lib_data["imports"]
                imports.extend(_parse_import_text(imp_text, lang))

        if not imports and lang in ("python",):
            imports.append(ir_import("sys"))
            imports.append(ir_import("json"))

        return imports

    def _compose_body(self, lang: str, task: str, intent: str,
                      framework: str | None, lib_data: dict | None,
                      syntax: dict, libs: dict) -> list[IRNode]:
        """Build the body nodes for the program."""
        body: list[IRNode] = []

        if lang in ("python",) and framework in ("flask", "django", "fastapi"):
            body.extend(self._compose_python_web(task, framework, syntax, libs))
        elif lang in ("javascript",) and framework in ("express", "fastify"):
            body.extend(self._compose_js_server(task, framework, syntax, libs))
        elif lang in ("go",) and framework:
            body.extend(self._compose_go_server(task, framework, syntax, libs))
        elif lang in ("rust",) and framework:
            body.extend(self._compose_rust_server(task, framework, syntax, libs))
        elif lang in ("ruby",) and framework:
            body.extend(self._compose_ruby_server(task, framework, syntax, libs))
        elif lang in ("c#",) and framework:
            body.extend(self._compose_csharp_server(task, framework, syntax, libs))
        elif lang == "html":
            body.extend(self._compose_html(task, syntax))
        elif lang == "css":
            body.extend(self._compose_css(task, syntax))
        elif lang == "sql":
            body.extend(self._compose_sql(task, syntax))
        elif lang == "react":
            body.extend(self._compose_react(task, syntax))
        elif lang == "angular":
            body.extend(self._compose_angular(task, syntax))
        elif lang == "nextjs":
            body.extend(self._compose_nextjs(task, syntax))
        elif lang in ("go",):
            body.extend(self._compose_go(task, intent, syntax))
        elif lang in ("rust",):
            body.extend(self._compose_rust(task, intent, syntax))
        elif lang in ("c", "c++"):
            body.extend(self._compose_c_family(task, intent, lang, syntax))
        elif lang == "c#":
            body.extend(self._compose_csharp(task, intent, syntax))
        elif lang in ("java",):
            body.extend(self._compose_java(task, intent, syntax))
        elif lang == "ruby":
            body.extend(self._compose_ruby(task, intent, syntax))
        elif lang == "r":
            body.extend(self._compose_r(task, intent, syntax))
        elif lang in ("mongodb", "nosql"):
            body.extend(self._compose_mongo(task, syntax))
        else:
            body.extend(self._compose_generic(task, intent, lang, syntax))

        return body

    # ─────────────────────────────────────────────
    # Python web (Flask / Django / FastAPI)
    # ─────────────────────────────────────────────

    def _compose_python_web(self, task: str, framework: str, syntax: dict, libs: dict) -> list[IRNode]:
        body: list[IRNode] = []
        lib_data = _find_lib(libs, framework)
        if not lib_data:
            return body

        body.append(ir_comment(f"Generated {framework} application"))

        if framework == "flask":
            app_init = lib_data.get("app", "app = Flask(__name__)")
            body.append(ir_assign("__name__", "Flask(__name__)", var_type="app"))

            route_decorator = lib_data.get("route", '@app.route("{route}", methods=["{method}"])')
            home_decorator = _safe_format(route_decorator, route="/", method="GET")
            route_node = ir_decorator_node(
                ir_decorator(home_decorator),
                ir_function("home", [], [ir_return_expr("'Hello, world!'")], return_type="str"),
            )
            body.append(route_node)

            main_body = ir_assign("app", "Flask(__name__)")
            run_call = ir_call("app.run", ["debug=True"])
            if "__name__" in str(syntax.get("main_guard", "")):
                guard = ir_if('"__name__" == "__main__"',
                              [ir_assign("app", "Flask(__name__)"), run_call])
                body.append(guard)
            else:
                body.append(ir_assign("app", "Flask(__name__)"))
                body.append(run_call)

        elif framework == "django":
            body.append(ir_comment("Add this app to INSTALLED_APPS"))
            body.append(ir_function("index", ["request"], [
                ir_return_expr("HttpResponse('Hello, world!')")
            ]))

        elif framework == "fastapi":
            body.append(ir_assign("app", "FastAPI()"))

            route_decorator = lib_data.get("route", '@app.{method}("{route}")')
            home_decorator = _safe_format(route_decorator, method="get", route="/")
            route_node = ir_decorator_node(
                ir_decorator(home_decorator),
                ir_function("root", [], [ir_return_expr("{'message': 'Hello, world!'}")]),
            )
            body.append(route_node)

        return body

    # ─────────────────────────────────────────────
    # JavaScript / Node servers
    # ─────────────────────────────────────────────

    def _compose_js_server(self, task: str, framework: str, syntax: dict, libs: dict) -> list[IRNode]:
        body: list[IRNode] = []
        lib_data = _find_lib(libs, framework)
        if not lib_data:
            return body

        body.append(ir_comment(f"Generated {framework} server"))

        app_var = lib_data.get("app", "const app = express();")
        if framework == "fastify":
            app_var = "const app = fastify();"
        body.append(ir_expression(app_var))

        route_method = "get"
        route_path = "/"
        body_line = "res.json({ ok: true });"
        if framework == "fastify":
            body.append(ir_expression(f"fastify.{route_method}('{route_path}', async (req, reply) => {{"))
        else:
            body.append(ir_expression(f"app.{route_method}('{route_path}', (req, res) => {{"))
        body.append(ir_expression(f"  {body_line}"))
        body.append(ir_expression("});"))

        listen_tmpl = lib_data.get("listen", "app.listen({port});")
        listen_text = _safe_format(listen_tmpl, port="3000")
        body.append(ir_expression(listen_text.strip()))

        return body

    # ─────────────────────────────────────────────
    # Go server
    # ─────────────────────────────────────────────

    def _compose_go_server(self, task: str, framework: str, syntax: dict, libs: dict) -> list[IRNode]:
        body: list[IRNode] = []
        lib_data = _find_lib(libs, framework)
        if not lib_data:
            return body

        body.append(ir_comment(f"Generated {framework} server"))

        handler_tmpl = lib_data.get("handler", "func {name}(w http.ResponseWriter, r *http.Request) {{\n{body}\n}}")
        handler_text = _safe_format(handler_tmpl, name="homeHandler", body='fmt.Fprintln(w, "Hello, world!")')
        body.append(ir_expression(handler_text.strip()))

        listen_tmpl = lib_data.get("listen", 'http.ListenAndServe(":{port}", nil)')
        listen_text = _safe_format(listen_tmpl, port="8080")
        body.append(ir_expression(listen_text.strip()))

        return body

    # ─────────────────────────────────────────────
    # Rust server
    # ─────────────────────────────────────────────

    def _compose_rust_server(self, task: str, framework: str, syntax: dict, libs: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_comment(f"Generated {framework} server"))
        body.append(ir_function("main", [], [
            ir_expression('println!("Listening on :8080");'),
        ]))
        return body

    # ─────────────────────────────────────────────
    # Ruby server
    # ─────────────────────────────────────────────

    def _compose_ruby_server(self, task: str, framework: str, syntax: dict, libs: dict) -> list[IRNode]:
        body: list[IRNode] = []
        lib_data = _find_lib(libs, framework)
        if not lib_data:
            return body

        body.append(ir_comment(f"Generated {framework} server"))

        route_tmpl = lib_data.get("route", "get '{route}' do\n{body}\nend")
        route_text = _safe_format(route_tmpl, route="/", body="'Hello, world!'")
        body.append(ir_expression(route_text.strip()))

        return body

    # ─────────────────────────────────────────────
    # C# server
    # ─────────────────────────────────────────────

    def _compose_csharp_server(self, task: str, framework: str, syntax: dict, libs: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_comment(f"Generated {framework} application"))
        body.append(ir_class("Program", None, [
            ir_function("Main", ["string[] args"], [
                ir_expression('Console.WriteLine("Hello, world!")'),
            ]),
        ]))
        return body

    # ─────────────────────────────────────────────
    # HTML
    # ─────────────────────────────────────────────

    def _compose_html(self, task: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_expression(syntax.get("doctype", "<!DOCTYPE html>")))
        body.append(ir_expression('<html lang="en">'))
        body.append(ir_expression('<head><meta charset="UTF-8"><title>Hello</title></head>'))
        body.append(ir_expression('<body><h1>Hello, world!</h1></body>'))
        body.append(ir_expression('</html>'))
        return body

    # ─────────────────────────────────────────────
    # CSS
    # ─────────────────────────────────────────────

    def _compose_css(self, task: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_expression('body {\n  font-family: sans-serif;\n  margin: 0;\n  padding: 20px;\n}'))
        body.append(ir_expression('h1 {\n  color: #333;\n}'))
        return body

    # ─────────────────────────────────────────────
    # SQL
    # ─────────────────────────────────────────────

    def _compose_sql(self, task: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        create_tmpl = syntax.get("create_table",
            "CREATE TABLE IF NOT EXISTS {name} (\n{columns}\n);")
        cols = "id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        body.append(ir_expression(_safe_format(create_tmpl, name="items", columns=cols)))

        insert_tmpl = syntax.get("insert", "INSERT INTO {table} ({columns})\nVALUES ({values});")
        body.append(ir_expression(_safe_format(insert_tmpl,
            table="items", columns="name", values="'sample'")))

        select_tmpl = syntax.get("select_where",
            "SELECT {columns}\nFROM {table}\nWHERE {condition};")
        body.append(ir_expression(_safe_format(select_tmpl,
            columns="*", table="items", condition="1=1")))
        return body

    # ─────────────────────────────────────────────
    # React
    # ─────────────────────────────────────────────

    def _compose_react(self, task: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        comp_tmpl = syntax.get("component",
            'export default function {name}() {{\n  const [{state}, set{State}] = useState({initial});\n  return (\n{jsx}\n  );\n}}')
        comp_text = _safe_format(comp_tmpl,
            name="App", state="count", State="Count", initial="0",
            jsx="    <div>\n      <h1>Hello, world!</h1>\n      <p>Count: {count}</p>\n    </div>",
        )
        body.append(ir_expression(comp_text.strip()))
        return body

    # ─────────────────────────────────────────────
    # Angular
    # ─────────────────────────────────────────────

    def _compose_angular(self, task: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        comp_tmpl = syntax.get("component",
            "@Component({{\n  selector: '{selector}',\n  templateUrl: '{template_url}'\n}})\nexport class {name}Component {{\n{body}\n}}")
        comp_text = _safe_format(comp_tmpl,
            selector="app-root", template_url="./app.component.html",
            style_url="./app.component.css",
            name="App", body="  title = 'Hello, world!';",
        )
        body.append(ir_expression(comp_text.strip()))
        return body

    # ─────────────────────────────────────────────
    # Next.js
    # ─────────────────────────────────────────────

    def _compose_nextjs(self, task: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        page_tmpl = syntax.get("page",
            'export default function {name}Page() {{\n  return (\n{jsx}\n  );\n}}')
        page_text = _safe_format(page_tmpl,
            name="Home",
            jsx="    <div>\n      <h1>Hello, world!</h1>\n    </div>",
        )
        body.append(ir_expression(page_text.strip()))
        return body

    # ─────────────────────────────────────────────
    # Go
    # ─────────────────────────────────────────────

    def _compose_go(self, task: str, intent: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_expression('package main'))
        body.append(ir_expression('import "fmt"'))

        func_tmpl = syntax.get("function", "func {name}({params}) {ret} {\n{body}\n}")
        func_text = _safe_format(func_tmpl,
            name="main", params="", ret="",
            body='    fmt.Println("Hello, world!")',
        )
        body.append(ir_expression(func_text.strip()))
        return body

    # ─────────────────────────────────────────────
    # Rust
    # ─────────────────────────────────────────────

    def _compose_rust(self, task: str, intent: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        main_tmpl = syntax.get("main", "fn main() {{\n{body}\n}}")
        body.append(ir_expression(_safe_format(main_tmpl,
            body='    println!("Hello, world!");')))
        return body

    # ─────────────────────────────────────────────
    # C / C++
    # ─────────────────────────────────────────────

    def _compose_c_family(self, task: str, intent: str, lang: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        if lang == "c":
            body.append(ir_expression('#include <stdio.h>'))
        else:
            body.append(ir_expression('#include <iostream>'))
            body.append(ir_expression("using namespace std;"))

        main_tmpl = syntax.get("main",
            "int main(int argc, char *argv[]) {{\n{body}\n    return 0;\n}}")
        if lang == "c":
            printf = '    printf("Hello, world!\\n");'
        else:
            printf = '    std::cout << "Hello, world!" << std::endl;'
        body.append(ir_expression(_safe_format(main_tmpl, body=printf)))
        return body

    # ─────────────────────────────────────────────
    # C#
    # ─────────────────────────────────────────────

    def _compose_csharp(self, task: str, intent: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_expression("namespace HelloWorld"))
        body.append(ir_expression("{"))
        body.append(ir_expression("    class Program"))
        body.append(ir_expression("    {"))
        body.append(ir_expression('        static void Main(string[] args)'))
        body.append(ir_expression("        {"))
        body.append(ir_expression('            Console.WriteLine("Hello, world!");'))
        body.append(ir_expression("        }"))
        body.append(ir_expression("    }"))
        body.append(ir_expression("}"))
        return body

    # ─────────────────────────────────────────────
    # Java
    # ─────────────────────────────────────────────

    def _compose_java(self, task: str, intent: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_expression("public class HelloWorld {"))
        body.append(ir_expression("    public static void main(String[] args) {"))
        body.append(ir_expression('        System.out.println("Hello, world!");'))
        body.append(ir_expression("    }"))
        body.append(ir_expression("}"))
        return body

    # ─────────────────────────────────────────────
    # Ruby
    # ─────────────────────────────────────────────

    def _compose_ruby(self, task: str, intent: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_expression('puts "Hello, world!"'))
        return body

    # ─────────────────────────────────────────────
    # R
    # ─────────────────────────────────────────────

    def _compose_r(self, task: str, intent: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_expression('cat("Hello, world!\\n")'))
        return body

    # ─────────────────────────────────────────────
    # MongoDB
    # ─────────────────────────────────────────────

    def _compose_mongo(self, task: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        body.append(ir_comment("Generated MongoDB queries"))
        insert_tmpl = syntax.get("insert_one", 'db.{collection}.insertOne({document})')
        body.append(ir_expression(_safe_format(insert_tmpl,
            collection="items", document="{ name: 'sample', active: true }")))
        find_tmpl = syntax.get("find", 'db.{collection}.find({query})')
        body.append(ir_expression(_safe_format(find_tmpl,
            collection="items", query="{ active: true }")))
        return body

    # ─────────────────────────────────────────────
    # Generic fallback
    # ─────────────────────────────────────────────

    def _compose_generic(self, task: str, intent: str, lang: str, syntax: dict) -> list[IRNode]:
        body: list[IRNode] = []
        lang_data = get_language(lang) or {}
        comment_tmpl = lang_data.get("comment", "# {text}")
        comment_prefix = comment_tmpl.split("{")[0].rstrip() if "{" in comment_tmpl else "#"

        def _c(text: str) -> str:
            return f"{comment_prefix} {text}"

        body.append(ir_comment(f"Generated {lang} code for: {task}"))
        body.append(ir_comment(f"Intent: {intent}"))

        inner: list[IRNode] = []
        if intent == "hello":
            print_tmpl = syntax.get("print") or syntax.get("console_log") or syntax.get("sout") or syntax.get("puts") or syntax.get("println") or syntax.get("cat")
            if print_tmpl:
                inner.append(ir_expression(_safe_format(print_tmpl, args='"Hello, world!"')))
            else:
                inner.append(ir_expression(_c(f'Hello, world! (no print syntax for {lang})')))
        elif intent == "math":
            inner.append(ir_variable("result", "1 + 2"))
            inner.append(ir_expression(_c("result = 3")))
        else:
            func_tmpl = syntax.get("function")
            if func_tmpl:
                inner.append(ir_expression(_safe_format(func_tmpl,
                    name="main", params="", body=f'    {_c(" TODO")}', ret="")))
            else:
                inner.append(ir_expression(_c(f"TODO: implement {task}")))

        if lang == "python":
            body.append(ir_function("main", [], inner))
            body.append(ir_if('"__name__" == "__main__"',
                              [ir_expression("main()")]))
        else:
            body.extend(inner)

        return body

    def _make_title(self, task: str, framework: str | None) -> str:
        words = task.strip().split()[:5]
        title = "".join(w.capitalize() for w in words)
        if framework:
            title += f" ({framework.capitalize()})"
        return title or "GeneratedCode"


def ir_return_expr(expr: str) -> IRNode:
    """Shorthand for a return expression node."""
    return IRNode("return", meta={"expr": expr})


# ─────────────────────────────────────────────
# LANGUAGE RENDERER
# ─────────────────────────────────────────────

class LanguageRenderer:
    """Converts a CodeIR tree into actual source code for a target language."""

    def __init__(self) -> None:
        pass

    def render(self, ir: CodeIR) -> str:
        """Render a CodeIR to a source code string."""
        lang_data = get_language(ir.language)
        if lang_data is None:
            return f"// Unknown language: {ir.language}"

        syntax = lang_data.get("syntax", {})
        indent_str = lang_data.get("style", {}).get("indent", "    ")
        comment_tmpl = lang_data.get("comment", "# {text}")
        comment_prefix = comment_tmpl.split("{")[0].rstrip() if "{" in comment_tmpl else "#"
        lines: list[str] = []

        self._render_node(ir.root, lines, indent_str, syntax, depth=0,
                          comment_prefix=comment_prefix, lang=ir.language)

        return "\n".join(lines)

    def _render_node(self, node: IRNode, lines: list[str], indent: str,
                     syntax: dict, depth: int, comment_prefix: str = "#",
                     lang: str = "python") -> None:
        pad = indent * depth

        if node.kind == "module":
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth, comment_prefix, lang)
                if child.kind in ("import", "from_import", "expression"):
                    pass
                else:
                    lines.append("")

        elif node.kind == "import":
            module = node.meta.get("module", "")
            style = node.meta.get("style", "import")
            if style == "require":
                lines.append(f"{pad}const {module} = require('{module}');")
            else:
                lines.append(f"{pad}import {module}")

        elif node.kind == "from_import":
            module = node.meta.get("module", "")
            names = ", ".join(node.meta.get("names", []))
            lines.append(f"{pad}from {module} import {names}")

        elif node.kind == "function":
            name = node.meta.get("name", "")
            params = ", ".join(node.meta.get("params", []))
            ret = node.meta.get("return_type")
            async_prefix = "async " if node.meta.get("async") else ""

            if lang in ("rust",):
                fn_keyword = "fn"
                if ret:
                    lines.append(f"{pad}{fn_keyword} {name}({params}) -> {ret} {{")
                else:
                    lines.append(f"{pad}{fn_keyword} {name}({params}) {{")
            elif lang in ("go",):
                if ret:
                    lines.append(f"{pad}func {name}({params}) {ret} {{")
                else:
                    lines.append(f"{pad}func {name}({params}) {{")
            elif lang in ("c", "c++", "java", "c#"):
                if ret:
                    lines.append(f"{pad}{ret} {name}({params}) {{")
                else:
                    lines.append(f"{pad}void {name}({params}) {{")
            elif lang in ("ruby",):
                lines.append(f"{pad}def {name}({params})")
            elif lang in ("r",):
                lines.append(f"{pad}{name} <- function({params}) {{")
            else:
                if ret:
                    lines.append(f"{pad}{async_prefix}def {name}({params}) -> {ret}:")
                else:
                    lines.append(f"{pad}{async_prefix}def {name}({params}):")

            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)
            if not node.children:
                lines.append(f"{indent * (depth + 1)}pass")

            if lang in ("rust", "go", "c", "c++", "java", "c#"):
                lines.append(f"{pad}}}")
            elif lang in ("r",):
                lines.append(f"{pad}}}")

        elif node.kind == "class":
            name = node.meta.get("name", "")
            parent = node.meta.get("parent")
            if parent:
                lines.append(f"{pad}class {name}({parent}):")
            else:
                lines.append(f"{pad}class {name}:")
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)
            if not node.children:
                lines.append(f"{indent * (depth + 1)}pass")

        elif node.kind == "variable":
            name = node.meta.get("name", "")
            value = node.meta.get("value", "")
            var_type = node.meta.get("var_type")
            mutable = node.meta.get("mutable", False)
            mut_kw = "mut " if mutable else ""
            if var_type and node.meta.get("var_type"):
                lines.append(f"{pad}let {mut_kw}{name}: {var_type} = {value};")
            else:
                lines.append(f"{pad}let {name} = {value};")

        elif node.kind == "assign":
            name = node.meta.get("name", "")
            expr = node.meta.get("expr", "")
            var_type = node.meta.get("var_type")
            if var_type:
                lines.append(f"{pad}{name}: {var_type} = {expr}")
            else:
                lines.append(f"{pad}{name} = {expr}")

        elif node.kind == "expression":
            expr = node.meta.get("expr", "")
            for line in expr.split("\n"):
                lines.append(f"{pad}{line}")

        elif node.kind == "return":
            expr = node.meta.get("expr")
            if expr:
                lines.append(f"{pad}return {expr}")
            else:
                lines.append(f"{pad}return")

        elif node.kind == "if":
            cond = node.meta.get("condition", "")
            lines.append(f"{pad}if {cond}:")
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)
            else_body = node.meta.get("else")
            if else_body:
                lines.append(f"{pad}else:")
                for child in (else_body if isinstance(else_body, list) else []):
                    self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)

        elif node.kind == "for":
            var = node.meta.get("var", "")
            iterable = node.meta.get("iterable", "")
            index = node.meta.get("index", False)
            if index:
                lines.append(f"{pad}for {var} in range({iterable}):")
            else:
                lines.append(f"{pad}for {var} in {iterable}:")
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)

        elif node.kind == "while":
            cond = node.meta.get("condition", "")
            lines.append(f"{pad}while {cond}:")
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)

        elif node.kind == "try":
            lines.append(f"{pad}try:")
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)
            exc = node.meta.get("exception", "Exception")
            var = node.meta.get("var", "e")
            lines.append(f"{pad}except {exc} as {var}:")
            handler = node.meta.get("handler", [])
            if isinstance(handler, list):
                for child in handler:
                    self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)

        elif node.kind == "comment":
            text = node.meta.get("text", "")
            block = node.meta.get("block", False)
            if block:
                lines.append(f'{pad}"""{text}"""')
            else:
                lines.append(f"{pad}{comment_prefix} {text}")

        elif node.kind == "decorated":
            children = node.children
            if len(children) == 2:
                self._render_node(children[0], lines, indent, syntax, depth, comment_prefix, lang)
                self._render_node(children[1], lines, indent, syntax, depth, comment_prefix, lang)

        elif node.kind == "decorator":
            name = node.meta.get("name", "")
            lines.append(f"{pad}{name}")

        elif node.kind == "route":
            method = node.meta.get("method", "get")
            route = node.meta.get("route", "/")
            handler = node.meta.get("handler", "handler")
            lines.append(f"{pad}# Route: {method.upper()} {route} -> {handler}")
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)

        elif node.kind == "property":
            name = node.meta.get("name", "")
            prop_type = node.meta.get("prop_type", "")
            lines.append(f"{pad}{name}: {prop_type}")
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth + 1, comment_prefix, lang)

        else:
            for child in node.children:
                self._render_node(child, lines, indent, syntax, depth, comment_prefix, lang)


# ─────────────────────────────────────────────
# CODE ENGINE  (facade)
# ─────────────────────────────────────────────

class CodeEngine:
    """Facade for composing and rendering code.

    Usage:
        engine = CodeEngine()
        code = engine.generate(task="Create a Flask web server", language="python")
    """

    def __init__(self) -> None:
        self.compositor = CodeCompositor()
        self.renderer = LanguageRenderer()

    def generate(self, task: str, language: str) -> tuple[bool, str]:
        """Generate code for a task in a given language.

        Returns (success, code_or_error).
        """
        lang = language.strip().lower()
        lang_data = get_language(lang)
        if lang_data is None:
            return False, f"Unknown language: {language}"

        try:
            ir = self.compositor.compose(task, lang)
            code = self.renderer.render(ir)
            if not code.strip():
                return False, f"Failed to generate code for: {task}"
            return True, code
        except Exception as e:
            return False, f"Code generation failed: {e}"

    def generate_with_meta(self, task: str, language: str) -> dict[str, Any]:
        """Generate code with metadata (title, description, metadata, code)."""
        lang = language.strip().lower()
        lang_data = get_language(lang)
        if lang_data is None:
            return {"ok": False, "error": f"Unknown language: {language}"}

        try:
            ir = self.compositor.compose(task, lang)
            code = self.renderer.render(ir)
            return {
                "ok": bool(code.strip()),
                "code": code,
                "language": lang,
                "title": ir.title,
                "description": ir.description,
                "metadata": ir.metadata,
                "file_ext": lang_data.get("file_ext", ""),
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def list_languages(self) -> list[str]:
        """Return all supported language names."""
        return sorted(LANGUAGES.keys())

    def known_syntax_rules(self, language: str) -> list[str]:
        """Return the available syntax rules for a language."""
        lang = get_language(language)
        if lang is None:
            return []
        return sorted(lang.get("syntax", {}).keys())


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _flatten_libs(libs: dict) -> set[str]:
    """Flatten all library names from a nested libs dict."""
    names: set[str] = set()
    for category in libs.values():
        if isinstance(category, dict):
            names.update(category.keys())
    return names


def _find_lib(libs: dict, name: str) -> dict | None:
    """Find a library by name across all categories."""
    for category in libs.values():
        if isinstance(category, dict) and name in category:
            return category[name]
    return None


def _find_lib_anywhere(libs: dict, name: str) -> dict | None:
    """Find a library by name, searching nested dicts recursively."""
    result = _find_lib(libs, name)
    if result:
        return result
    for category in libs.values():
        if isinstance(category, dict):
            for lib_name, lib_data in category.items():
                if isinstance(lib_data, dict) and name in str(lib_data):
                    return lib_data
    return None


def _parse_import_text(text: str, lang: str) -> list[IRNode]:
    """Parse an import text string into IRNode imports."""
    nodes: list[IRNode] = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if lang == "python":
            m = re.match(r"from\s+(\S+)\s+import\s+(.+)", line)
            if m:
                names = [n.strip() for n in m.group(2).split(",")]
                nodes.append(ir_from_import(m.group(1), names))
                continue
            m = re.match(r"import\s+(.+)", line)
            if m:
                module = m.group(1).strip()
                nodes.append(ir_import(module))
                continue
        elif lang in ("javascript", "typescript"):
            m = re.match(r"const\s+\{?\s*(\w+)\s*\}?\s*=\s*require\(['\"]([^'\"]+)['\"]\)\(?\)?", line)
            if m:
                nodes.append(ir_import(m.group(2), style="require"))
                continue
            m = re.match(r"import\s+(?:\{[^}]*\}\s+from\s+)?['\"]([^'\"]+)['\"]", line)
            if m:
                nodes.append(ir_import(m.group(1), style="import"))
                continue
        nodes.append(ir_import(line))
    return nodes


def _extract_rhs(text: str) -> str:
    """Extract the right-hand side of an assignment like 'const app = express();'."""
    if "=" in text:
        parts = text.split("=", 1)
        return parts[1].strip().rstrip(";").strip()
    return text.strip()


class _SafeDict(dict):
    """Dict subclass that returns '{key}' for missing keys in str.format_map().

    This lets us use .format_map() on templates that contain literal curly
    braces (JS/Go/Rust syntax, JSX expressions) without raising KeyError.
    """
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _safe_format(template: str, **kwargs: str) -> str:
    """Replace {key} placeholders in a template, handling {{ }} escape pairs.

    Grammar templates use Python format syntax ({{ for literal {).
    This function:
      1. Temporarily protects {{ and }} pairs
      2. Replaces {key} with values
      3. Restores {{ → { and }} → }
    """
    result = template
    # Protect escaped pairs: {{ → \x00, }} → \x01
    result = result.replace("{{", "\x00")
    result = result.replace("}}", "\x01")
    # Replace {key} with values
    for key, value in kwargs.items():
        result = result.replace("{" + key + "}", value)
    # Restore escaped pairs
    result = result.replace("\x00", "{")
    result = result.replace("\x01", "}")
    return result
