"""
Language Grammar Library — syntax rules, patterns, and library knowledge
for every language Aashu can learn and generate code in.

Each language entry is a dict with:
  - "syntax": composable syntax rules (function, class, import, etc.)
  - "libraries": categorized library knowledge (web, db, data, etc.)
  - "patterns": common code patterns (CRUD, middleware, etc.)
  - "style": naming conventions, indentation, etc.
  - "file_ext": primary file extension
  - "comment": comment syntax
  - "aliases": alternative names for the language

Syntax rules use placeholders that the CodeRenderer fills:
  {name}, {params}, {body}, {ret}, {expr}, {var}, {iterable},
  {condition}, {message}, {module}, {path}, {table}, {query},
  {fields}, {value}, {parent}, {child}, {handler}, {data},
  {method}, {route}, {content}, {title}, {desc}, {args}, {kwargs}
"""

from __future__ import annotations
from typing import Any

LANGUAGES: dict[str, dict[str, Any]] = {}

# ─────────────────────────────────────────────────
# PYTHON
# ─────────────────────────────────────────────────
LANGUAGES["python"] = {
    "file_ext": ".py",
    "comment": "# {text}",
    "comment_block": '"""{text}"""',
    "aliases": ["py", "python3"],
    "style": {"indent": "    ", "naming": "snake_case", "class_naming": "PascalCase"},
    "syntax": {
        "function": "def {name}({params}):\n{body}",
        "async_function": "async def {name}({params}):\n{body}",
        "function_ret": "def {name}({params}) -> {ret}:\n{body}",
        "return": "return {expr}",
        "class": "class {name}({parent}):\n{body}",
        "class_simple": "class {name}:\n{body}",
        "init": "def __init__(self{params}):\n{body}",
        "import": "import {module}",
        "from_import": "from {module} import {names}",
        "import_as": "import {module} as {alias}",
        "if": "if {condition}:\n{body}",
        "if_else": "if {condition}:\n{body}\nelse:\n{else_body}",
        "elif": "elif {condition}:\n{body}",
        "for": "for {var} in {iterable}:\n{body}",
        "for_range": "for {var} in range({args}):\n{body}",
        "while": "while {condition}:\n{body}",
        "try_except": "try:\n{body}\nexcept {exception} as {var}:\n{handler}",
        "try_finally": "try:\n{body}\nfinally:\n{handler}",
        "with": "with {expression} as {var}:\n{body}",
        "lambda": "lambda {params}: {expr}",
        "list_comp": "[{expr} for {var} in {iterable}]",
        "f_string": 'f"{template}"',
        "print": "print({args})",
        "raise": "raise {exception}({message})",
        "assert": "assert {condition}, {message}",
        "yield": "yield {expr}",
        "decorator": "@{name}\n",
        "main_guard": 'if __name__ == "__main__":\n    {body}',
        "docstring": '"""{text}"""',
        "none": "None", "true": "True", "false": "False",
        "and": "and", "or": "or", "not": "not {expr}",
        "in": "{item} in {collection}",
        "is_none": "{expr} is None", "is_not_none": "{expr} is not None",
        "type_hint": "{name}: {type}",
    },
    "libraries": {
        "web": {
            "flask": {
                "imports": "from flask import Flask, request, jsonify",
                "app": "app = Flask(__name__)",
                "route": '@app.route("{route}", methods=["{method}"])',
                "get_json": "request.get_json()",
                "jsonify": "jsonify({data})",
                "error_handler": '@app.errorhandler({code})\ndef {name}(error):\n    return jsonify({{"error": str(error)}}), {code}',
            },
            "fastapi": {
                "imports": "from fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel",
                "app": "app = FastAPI()",
                "route": '@app.{method}("{route}")',
                "path_param": "{name}: {type}",
                "query_param": "{name}: {type} = {default}",
                "body_model": "class {name}(BaseModel):\n{fields}",
                "http_exception": "raise HTTPException(status_code={code}, detail={message})",
            },
            "django": {
                "imports": "from django.http import JsonResponse\nfrom django.views.decorators.http import require_http_methods",
                "route": '@require_http_methods(["{method}"])',
                "json_response": "JsonResponse({data})",
                "json_safe": "JsonResponse({data}, safe=False)",
            },
        },
        "data": {
            "pandas": {
                "imports": "import pandas as pd",
                "read_csv": 'pd.read_csv("{path}")',
                "dataframe": "pd.DataFrame({data})",
                "filter": '{df}[{df}["{col}"].{condition}]',
                "groupby": '{df}.groupby("{col}").{agg}()',
                "to_csv": '{df}.to_csv("{path}", index=False)',
            },
            "numpy": {
                "imports": "import numpy as np",
                "array": "np.array({data})",
                "zeros": "np.zeros(({rows}, {cols}))",
                "random_normal": "np.random.normal({mean}, {std}, ({size},))",
                "dot": "np.dot({a}, {b})",
                "mean": "np.mean({arr})",
            },
            "matplotlib": {
                "imports": "import matplotlib.pyplot as plt",
                "plot": "plt.plot({x}, {y})",
                "scatter": "plt.scatter({x}, {y})",
                "hist": "plt.hist({data}, bins={bins})",
                "title": 'plt.title("{title}")',
                "show": "plt.show()",
                "savefig": 'plt.savefig("{path}")',
            },
        },
        "ml": {
            "scikit-learn": {
                "imports": "from sklearn.model_selection import train_test_split\nfrom sklearn.metrics import accuracy_score",
                "split": "X_train, X_test, y_train, y_test = train_test_split({X}, {y}, test_size={test_size})",
                "fit": "{model}.fit({X_train}, {y_train})",
                "predict": "{model}.predict({X_test})",
            },
            "tensorflow": {
                "imports": "import tensorflow as tf\nfrom tensorflow import keras",
                "sequential": "tf.keras.models.Sequential([{layers}])",
                "dense": 'tf.keras.layers.Dense({units}, activation="{activation}")',
                "compile": '{model}.compile(optimizer="{optimizer}", loss="{loss}")',
            },
            "pytorch": {
                "imports": "import torch\nimport torch.nn as nn\nimport torch.optim as optim",
                "linear": "nn.Linear({in_features}, {out_features})",
                "relu": "nn.ReLU()",
                "mse_loss": "nn.MSELoss()",
                "adam": "optim.Adam({model}.parameters(), lr={lr})",
            },
        },
        "db": {
            "sqlite3": {
                "imports": "import sqlite3",
                "connect": 'conn = sqlite3.connect("{db_path}")',
                "execute": 'cursor.execute("{query}", {params})',
                "fetchall": "results = cursor.fetchall()",
                "fetchone": "result = cursor.fetchone()",
                "commit": "conn.commit()",
            },
            "psycopg2": {
                "imports": "import psycopg2",
                "connect": 'conn = psycopg2.connect("{conn_string}")',
                "execute": 'cursor.execute("{query}", {params})',
            },
            "sqlalchemy": {
                "imports": "from sqlalchemy import create_engine, Column, Integer, String\nfrom sqlalchemy.orm import declarative_base, Session",
                "engine": 'engine = create_engine("{conn_string}")',
                "base": "Base = declarative_base()",
                "model": 'class {name}(Base):\n    __tablename__ = "{table}"\n{fields}',
            },
            "pymongo": {
                "imports": "from pymongo import MongoClient",
                "connect": 'client = MongoClient("{conn_string}")',
                "db": 'db = client["{db_name}"]',
                "collection": 'collection = db["{collection_name}"]',
                "insert_one": "collection.insert_one({document})",
                "find": "collection.find({query})",
                "find_one": "collection.find_one({query})",
                "update_one": 'collection.update_one({query}, {{"$set": {update}}})',
                "delete_one": "collection.delete_one({query})",
            },
        },
        "http": {
            "requests": {
                "imports": "import requests",
                "get": 'requests.get("{url}")',
                "post": 'requests.post("{url}", json={data})',
                "put": 'requests.put("{url}", json={data})',
                "delete": 'requests.delete("{url}")',
            },
            "httpx": {
                "imports": "import httpx",
                "get": 'httpx.get("{url}")',
                "post": 'httpx.post("{url}", json={data})',
            },
        },
        "cli": {
            "argparse": {
                "imports": "import argparse",
                "parser": 'parser = argparse.ArgumentParser(description="{desc}")',
                "add_arg": 'parser.add_argument("{name}", help="{help}")',
                "add_arg_typed": 'parser.add_argument("{name}", type={type}, help="{help}")',
                "add_arg_flag": 'parser.add_argument("--{name}", action="store_true", help="{help}")',
                "parse": "args = parser.parse_args()",
            },
            "click": {
                "imports": "import click",
                "command": '@click.command()\n@click.option("{name}", help="{help}")\ndef {func}({name}):\n{body}',
            },
            "typer": {
                "imports": "import typer",
                "app": "app = typer.Typer()",
                "command": '@app.command()\ndef {func}({params}):\n{body}',
                "run": 'if __name__ == "__main__":\n    app()',
            },
        },
        "testing": {
            "pytest": {
                "imports": "import pytest",
                "test": "def test_{name}():\n{body}",
                "fixture": "@pytest.fixture\ndef {name}():\n{body}",
                "parametrize": '@pytest.mark.parametrize("{name}", [{values}])\ndef test_{func}({name}):\n{body}',
            },
        },
        "async": {
            "asyncio": {
                "imports": "import asyncio",
                "coroutine": "async def {name}({params}):\n{body}",
                "await": "await {expr}",
                "gather": "await asyncio.gather({tasks})",
                "run": "asyncio.run({coroutine})",
            },
        },
        "io": {
            "json": {
                "imports": "import json",
                "dumps": "json.dumps({data}, indent=2)",
                "loads": "json.loads({string})",
                "dump_file": "json.dump({data}, {file}, indent=2)",
                "load_file": "json.load({file})",
            },
            "csv": {"imports": "import csv", "reader": "csv.reader({file})", "writer": "csv.writer({file})"},
            "pathlib": {
                "imports": "from pathlib import Path",
                "path": 'Path("{path}")',
                "read_text": 'Path("{path}").read_text()',
                "write_text": 'Path("{path}").write_text({content})',
                "exists": 'Path("{path}").exists()',
            },
        },
        "datetime": {
            "datetime": {
                "imports": "from datetime import datetime, timedelta",
                "now": "datetime.now()",
                "strftime": '{dt}.strftime("%{fmt}")',
                "timedelta": "timedelta({args})",
            },
        },
        "logging": {
            "logging": {
                "imports": "import logging",
                "get_logger": "logging.getLogger(__name__)",
                "basic_config": 'logging.basicConfig(level=logging.{level})',
            },
        },
    },
    "patterns": {
        "crud_rest": {"structure": ["imports", "app_init", "routes", "main"]},
        "cli_tool": {"structure": ["imports", "args", "logic", "main_guard"]},
        "data_pipeline": {"structure": ["imports", "load", "transform", "analyze", "output"]},
        "web_scraper": {"structure": ["imports", "fetch", "parse", "extract", "save"]},
        "test_suite": {"structure": ["imports", "fixtures", "tests"]},
    },
}

# ─────────────────────────────────────────────────
# JAVASCRIPT / NODE.JS
# ─────────────────────────────────────────────────
LANGUAGES["javascript"] = {
    "file_ext": ".js",
    "comment": "// {text}",
    "comment_block": "/* {text} */",
    "aliases": ["js", "node", "nodejs"],
    "style": {"indent": "  ", "naming": "camelCase", "class_naming": "PascalCase"},
    "syntax": {
        "function": "function {name}({params}) {\n{body}\n}",
        "async_function": "async function {name}({params}) {\n{body}\n}",
        "arrow": "const {name} = ({params}) => {\n{body}\n}",
        "arrow_expr": "({params}) => {expr}",
        "return": "return {expr};",
        "class": "class {name} extends {parent} {\n{body}\n}",
        "class_simple": "class {name} {\n{body}\n}",
        "constructor": "constructor({params}) {\n{body}\n}",
        "import": "import {name} from '{path}';",
        "import_named": "import {{ {names} }} from '{path}';",
        "require": "const {name} = require('{module}');",
        "if": "if ({condition}) {\n{body}\n}",
        "if_else": "if ({condition}) {\n{body}\n} else {\n{else_body}\n}",
        "for": "for (const {var} of {iterable}) {\n{body}\n}",
        "for_index": "for (let {var} = 0; {var} < {limit}; {var}++) {\n{body}\n}",
        "while": "while ({condition}) {\n{body}\n}",
        "try_catch": "try {\n{body}\n} catch ({var}) {\n{handler}\n}",
        "try_finally": "try {\n{body}\n} finally {\n{handler}\n}",
        "const": "const {name} = {value};",
        "let": "let {name} = {value};",
        "async_await": "await {expr};",
        "module_export": "module.exports = {name};",
        "export_default": "export default {name};",
        "console_log": "console.log({args});",
        "throw": "throw new Error({message});",
        "template_literal": "`{template}`",
        "promise": "new Promise((resolve, reject) => {\n{body}\n})",
    },
    "libraries": {
        "web": {
            "express": {
                "imports": "const express = require('express');",
                "app": "const app = express();",
                "route": "app.{method}('{route}', (req, res) => {\n{body}\n});",
                "get_param": "req.params.{name}",
                "get_query": "req.query.{name}",
                "get_body": "req.body",
                "json_response": "res.json({data});",
                "send": "res.send({data});",
                "status": "res.status({code}).json({data});",
                "listen": "app.listen({port}, () => console.log('Listening on ' + {port}));",
            },
            "fastify": {
                "imports": "const fastify = require('fastify')();",
                "route": "fastify.{method}('{route}', async (req, reply) => {\n{body}\n});",
                "json_response": "return {data};",
                "listen": "fastify.listen({port});",
            },
        },
        "db": {
            "sqlite3": {
                "imports": "const Database = require('better-sqlite3');",
                "connect": 'const db = new Database("{db_path}");',
                "execute": 'db.prepare("{query}").run({params});',
                "fetchall": 'db.prepare("{query}").all();',
                "fetchone": 'db.prepare("{query}").get({params});',
            },
            "pg": {
                "imports": "const {{ Pool }} = require('pg');",
                "connect": 'const pool = new Pool({{ connectionString: "{conn_string}" }});',
                "query": "await pool.query('{query}', [{params}]);",
            },
            "mongodb": {
                "imports": "const {{ MongoClient }} = require('mongodb');",
                "connect": 'const client = new MongoClient("{conn_string}");',
                "db": 'const db = client.db("{db_name}");',
                "collection": 'const col = db.collection("{collection_name}");',
                "insert_one": "await col.insertOne({document});",
                "find": "await col.find({query}).toArray();",
                "find_one": "await col.findOne({query});",
                "update_one": "await col.updateOne({query}, {{ $set: {update} }});",
                "delete_one": "await col.deleteOne({query});",
            },
        },
        "testing": {
            "jest": {
                "imports": "const { {names} } = require('{module}');",
                "test": "test('{description}', () => {\n{body}\n});",
                "describe": "describe('{name}', () => {\n{body}\n});",
                "expect_equal": "expect({actual}).toBe({expected});",
                "expect_truthy": "expect({value}).toBeTruthy();",
            },
        },
        "http": {
            "axios": {
                "imports": "const axios = require('axios');",
                "get": "await axios.get('{url}');",
                "post": "await axios.post('{url}', {data});",
            },
            "node_fetch": {
                "imports": "const fetch = require('node-fetch');",
                "get": "const res = await fetch('{url}');\nconst data = await res.json();",
            },
        },
    },
    "patterns": {
        "crud_rest": {"structure": ["requires", "app_init", "routes", "listen"]},
        "cli_tool": {"structure": ["requires", "args", "logic"]},
        "worker": {"structure": ["requires", "setup", "task_loop"]},
    },
}

# ─────────────────────────────────────────────────
# TYPESCRIPT
# ─────────────────────────────────────────────────
LANGUAGES["typescript"] = {
    "file_ext": ".ts",
    "comment": "// {text}",
    "comment_block": "/* {text} */",
    "aliases": ["ts"],
    "style": {"indent": "  ", "naming": "camelCase", "class_naming": "PascalCase"},
    "syntax": {
        "function": "function {name}({params}): {ret} {\n{body}\n}",
        "async_function": "async function {name}({params}): Promise<{ret}> {\n{body}\n}",
        "arrow": "const {name} = ({params}): {ret} => {\n{body}\n}",
        "return": "return {expr};",
        "class": "class {name} extends {parent} {\n{body}\n}",
        "class_simple": "class {name} {\n{body}\n}",
        "interface": "interface {name} {\n{fields}\n}",
        "type_alias": "type {name} = {definition};",
        "import": "import {name} from '{path}';",
        "import_named": "import {{ {names} }} from '{path}';",
        "import_type": "import type {{ {names} }} from '{path}';",
        "export": "export {name} = {value};",
        "export_default": "export default {name};",
        "export_interface": "export interface {name} {\n{fields}\n}",
        "const": "const {name}: {type} = {value};",
        "let": "let {name}: {type} = {value};",
        "if": "if ({condition}) {\n{body}\n}",
        "if_else": "if ({condition}) {\n{body}\n} else {\n{else_body}\n}",
        "for": "for (const {var} of {iterable}) {\n{body}\n}",
        "while": "while ({condition}) {\n{body}\n}",
        "try_catch": "try {\n{body}\n} catch ({var}: {type}) {\n{handler}\n}",
        "enum": "enum {name} {\n{values}\n}",
        "generics": "{name}<{type_params}>",
        "nullable": "{type} | null",
        "optional_prop": "{name}?: {type}",
    },
    "libraries": {
        "web": {
            "express": {
                "imports": "import express, {{ Request, Response }} from 'express';",
                "app": "const app = express();",
                "route": "app.{method}('{route}', (req: Request, res: Response) => {\n{body}\n});",
                "json_response": "res.json({data});",
            },
            "nextjs": {
                "imports": "import {{ NextApiRequest, NextApiResponse }} from 'next';",
                "handler": "export default async function handler(req: NextApiRequest, res: NextApiResponse) {\n{body}\n}",
                "page": "export default function {name}() {\n  return (\n{jsx}\n  );\n}",
            },
        },
        "react": {
            "imports": "import React from 'react';",
            "component": "export default function {name}({{ {props} }}: {{ {prop_types} }}) {\n  return (\n{jsx}\n  );\n}",
            "hook_state": "const [{state}, set{State}] = useState<{type}>({initial});",
            "hook_effect": "useEffect(() => {\n{body}\n}, [{deps}]);",
        },
    },
}

# ─────────────────────────────────────────────────
# REACT (JSX-specific)
# ─────────────────────────────────────────────────
LANGUAGES["react"] = {
    "file_ext": ".jsx",
    "comment": "// {text}",
    "aliases": ["reactjs", "react.js"],
    "style": {"indent": "  ", "naming": "camelCase", "class_naming": "PascalCase"},
    "syntax": {
        "component": "export default function {name}() {\n  const [{state}, set{State}] = useState({initial});\n  return (\n{jsx}\n  );\n}",
        "component_props": "export default function {name}({ {props} }) {\n  return (\n{jsx}\n  );\n}",
        "hook_state": "const [{state}, set{State}] = useState({initial});",
        "hook_effect": "useEffect(() => {\n{body}\n}, [{deps}]);",
        "hook_context": "const {name} = createContext({initial});",
        "hook_ref": "const {name} = useRef({initial});",
        "hook_memo": "const {name} = useMemo(() => {{ {body} }}, [{deps}]);",
        "handler": "const handle{Event} = ({params}) => {\n{body}\n};",
        "jsx_element": "<{tag} {attrs}>{children}</{tag}>",
        "jsx_self_close": "<{tag} {attrs} />",
        "jsx_expression": "{{{expr}}}",
        "conditional_render": "{{{condition} && <{component} />}}",
        "conditional_ternary": "{{{condition} ? <{a} /> : <{b} />}}",
        "map_list": "{{{list}.map(({item}) => (\n  <{component} key={{{{item}.id}}}} />\n))}}",
        "import": "import {name} from '{path}';",
        "import_react": "import React, {{ {names} }} from 'react';",
    },
}

# ─────────────────────────────────────────────────
# ANGULAR
# ─────────────────────────────────────────────────
LANGUAGES["angular"] = {
    "file_ext": ".ts",
    "comment": "// {text}",
    "aliases": ["angularjs"],
    "style": {"indent": "  ", "naming": "camelCase", "class_naming": "PascalCase"},
    "syntax": {
        "component": '@Component({{\n  selector: \'{selector}\',\n  templateUrl: \'{template_url}\',\n  styleUrls: [\'{style_url}\']\n}})\nexport class {name}Component implements OnInit {\n{body}\n}',
        "service": '@Injectable({{\n  providedIn: \'root\'\n}})\nexport class {name}Service {\n{body}\n}',
        "pipe": '@Pipe({{\n  name: \'{name}\'\n}})\nexport class {Name}Pipe implements PipeTransform {\n  transform({params}): {ret} {\n{body}\n  }\n}',
        "module": '@NgModule({{\n  declarations: [{declarations}],\n  imports: [{imports}],\n  providers: [{providers}],\n  bootstrap: [{bootstrap}]\n}})\nexport class {name}Module {{ }}',
        "routing": "const routes: Routes = [\n{routes}\n];",
        "route": "{{ path: '{path}', component: {component} }}",
        "http_get": "this.http.get<{type}>('{url}');",
        "http_post": "this.http.post<{type}>('{url}', {data});",
        "observable": "this.{service}.{method}().subscribe({{ next: ({param}) => {{ {body} }} }});",
    },
}

# ─────────────────────────────────────────────────
# NEXT.JS
# ─────────────────────────────────────────────────
LANGUAGES["nextjs"] = {
    "file_ext": ".tsx",
    "comment": "// {text}",
    "aliases": ["next", "next.js"],
    "style": {"indent": "  ", "naming": "camelCase", "class_naming": "PascalCase"},
    "syntax": {
        "page": "export default function {name}Page() {{\n  return (\n{jsx}\n  );\n}}",
        "layout": "export default function Layout({{ children }}: {{ children: React.ReactNode }}) {{\n  return <div>{{children}}</div>;\n}}",
        "server_component": "export default async function {name}() {{\n  const data = await fetchData();\n  return (\n{jsx}\n  );\n}}",
        "api_route": "import {{ NextResponse }} from 'next/server';\n\nexport async function {method}(req: Request) {{\n{body}\n  return NextResponse.json({{ data }});\n}}",
        "get_params": "const {name} = params.{name};",
        "use_client": "'use client';",
        "use_server": "'use server';",
    },
}

# ─────────────────────────────────────────────────
# HTML
# ─────────────────────────────────────────────────
LANGUAGES["html"] = {
    "file_ext": ".html",
    "comment": "<!-- {text} -->",
    "aliases": [],
    "style": {"indent": "  ", "naming": "kebab-case"},
    "syntax": {
        "doctype": "<!DOCTYPE html>",
        "html": '<html lang="{lang}">\n{head}\n{body}\n</html>',
        "head": "<head>\n  <meta charset=\"UTF-8\">\n  <title>{title}</title>\n{extra}\n</head>",
        "body": "<body>\n{content}\n</body>",
        "div": '<div class="{classes}">{content}</div>',
        "heading": "<h{level}>{text}</h{level}>",
        "paragraph": "<p>{text}</p>",
        "link": '<a href="{url}">{text}</a>',
        "image": '<img src="{src}" alt="{alt}">',
        "form": '<form action="{action}" method="{method}">\n{fields}\n  <button type="submit">{button}</button>\n</form>',
        "input": '<input type="{type}" name="{name}" placeholder="{placeholder}">',
        "table": "<table>\n{header}\n{rows}\n</table>",
        "table_row": "<tr>{cells}</tr>",
        "table_cell": "<td>{content}</td>",
        "table_header": "<th>{content}</th>",
        "script": '<script src="{src}"></script>',
        "style": "<style>\n{css}\n</style>",
        "meta_viewport": '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "link_css": '<link rel="stylesheet" href="{url}">',
    },
}

# ─────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────
LANGUAGES["css"] = {
    "file_ext": ".css",
    "comment": "/* {text} */",
    "aliases": [],
    "style": {"indent": "  ", "naming": "kebab-case"},
    "syntax": {
        "selector": "{selector} {\n{properties}\n}",
        "property": "{name}: {value};",
        "flexbox": "display: flex;\njustify-content: {justify};\nalign-items: {align};",
        "grid": "display: grid;\ngrid-template-columns: {columns};\ngap: {gap};",
        "responsive": "@media (max-width: {width}) {\n{rules}\n}",
        "animation": "@keyframes {name} {\n{frames}\n}",
        "transition": "transition: {property} {duration} {easing};",
        "position": "position: {type};\n{coordinates}",
        "typography": "font-family: {font};\nfont-size: {size};\nfont-weight: {weight};\nline-height: {height};",
        "color": "color: {fg};\nbackground-color: {bg};",
        "spacing": "margin: {margin};\npadding: {padding};",
        "border": "border: {width} {style} {color};\nborder-radius: {radius};",
        "shadow": "box-shadow: {x} {y} {blur} {spread} {color};",
    },
}

# ─────────────────────────────────────────────────
# GO
# ─────────────────────────────────────────────────
LANGUAGES["go"] = {
    "file_ext": ".go",
    "comment": "// {text}",
    "comment_block": "/* {text} */",
    "aliases": ["golang"],
    "style": {"indent": "\t", "naming": "camelCase", "export_naming": "PascalCase"},
    "syntax": {
        "package": "package {name}",
        "import": "import (\n\t\"{path}\"\n)",
        "function": "func {name}({params}) {ret} {\n{body}\n}",
        "method": "func ({receiver} *{type}) {name}({params}) {ret} {\n{body}\n}",
        "struct": "type {name} struct {\n{fields}\n}",
        "interface": "type {name} interface {\n{methods}\n}",
        "return": "return {expr}",
        "if": "if {condition} {\n{body}\n}",
        "if_else": "if {condition} {\n{body}\n} else {\n{else_body}\n}",
        "if_err": "if err != nil {\n{handler}\n}",
        "for": "for {var} := range {iterable} {\n{body}\n}",
        "for_index": "for {var} := 0; {var} < {limit}; {var}++ {\n{body}\n}",
        "while": "for {condition} {\n{body}\n}",
        "switch": "switch {expression} {\ncase {value}:\n{body}\ndefault:\n{default_body}\n}",
        "defer": "defer {expr}",
        "go_routine": "go {name}({args})",
        "channel_send": "{channel} <- {value}",
        "channel_receive": "<- {channel}",
        "make_channel": "make(chan {type}, {buffer})",
        "error_check": "if err != nil {\n\treturn {error}\n}",
        "constants": "const (\n{values}\n)",
        "variables": "var (\n{values}\n)",
        "short_var": "{name} := {value}",
        "anon_function": "func({params}) {\n{body}\n}",
        "map_literal": "map[{key_type}]{val_type}{{\n{entries}\n}}",
        "slice_literal": "[]{type}{{\n{values}\n}}",
        "print": "fmt.Println({args})",
        "printf": "fmt.Printf(\"{format}\", {args})",
        "main": "func main() {\n{body}\n}",
        "json_tag": "`json:\"{name}\"`",
    },
    "libraries": {
        "web": {
            "net/http": {
                "imports": '"net/http"',
                "mux": 'http.HandleFunc("{route}", {handler})',
                "handler": "func {name}(w http.ResponseWriter, r *http.Request) {\n{body}\n}",
                "json_response": "json.NewEncoder(w).Encode({data})",
                "listen": 'http.ListenAndServe(":{port}", nil)',
            },
            "gin": {
                "imports": '"github.com/gin-gonic/gin"',
                "route": 'r.{method}("{route}", func(c *gin.Context) {{\n{body}\n}})',
                "json": "c.JSON({code}, {data})",
                "bind_json": "c.ShouldBindJSON(&{var})",
            },
            "echo": {
                "imports": '"github.com/labstack/echo/v4"',
                "route": 'e.{method}("{route}", func(c echo.Context) error {{\n{body}\n}})',
                "json": "return c.JSON({code}, {data})",
            },
        },
        "db": {
            "database/sql": {
                "imports": '"database/sql"\n_ "github.com/lib/pq"',
                "open": 'db, err := sql.Open("postgres", "{conn}")',
                "query": 'rows, err := db.Query("{query}", {args})',
                "query_row": 'err := db.QueryRow("{query}", {args}).Scan({vars})',
                "exec": '_, err := db.Exec("{query}", {args})',
            },
            "gorm": {
                "imports": '"gorm.io/gorm"\n"gorm.io/driver/postgres"',
                "open": 'db, err := gorm.Open(postgres.Open("{conn}"), &gorm.Config{{}})',
                "model": "type {name} struct {\n\tgorm.Model\n{fields}\n}",
                "find": 'db.Find(&{var})',
                "where": 'db.Where("{condition}", {args}).Find(&{var})',
                "create": 'db.Create(&{var})',
                "save": 'db.Save(&{var})',
                "delete": 'db.Delete(&{var})',
            },
        },
        "testing": {
            "testing": {
                "imports": '"testing"',
                "test": "func Test{Name}(t *testing.T) {\n{body}\n}",
                "assert": 'if {actual} != {{expected}} {{\n\tt.Errorf("got %v, want %v", {actual}, {expected})\n}}',
            },
        },
    },
}

# ─────────────────────────────────────────────────
# RUST
# ─────────────────────────────────────────────────
LANGUAGES["rust"] = {
    "file_ext": ".rs",
    "comment": "// {text}",
    "comment_block": "/* {text} */",
    "aliases": ["rs"],
    "style": {"indent": "    ", "naming": "snake_case", "type_naming": "PascalCase"},
    "syntax": {
        "function": "fn {name}({params}) -> {ret} {\n{body}\n}",
        "function_no_ret": "fn {name}({params}) {\n{body}\n}",
        "async_function": "async fn {name}({params}) -> {ret} {\n{body}\n}",
        "struct": "struct {name} {{\n{fields}\n}}",
        "struct_impl": "impl {name} {{\n{methods}\n}}",
        "impl_trait": "impl {trait} for {type} {{\n{methods}\n}}",
        "enum": "enum {name} {{\n{variants}\n}}",
        "trait": "trait {name} {{\n{methods}\n}}",
        "return": "Ok({expr})",
        "return_err": "Err({error})",
        "if": "if {condition} {{\n{body}\n}}",
        "if_else": "if {condition} {{\n{body}\n}} else {{\n{else_body}\n}}",
        "if_let": "if let Some({var}) = {expr} {{\n{body}\n}}",
        "for": "for {var} in {iterable} {{\n{body}\n}}",
        "while": "while {condition} {{\n{body}\n}}",
        "loop": "loop {{\n{body}\n}}",
        "match": "match {expression} {{\n{arms}\n}}",
        "match_arm": "{pattern} => {{ {result} }}",
        "let": "let {name}: {type} = {value};",
        "let_mut": "let mut {name}: {type} = {value};",
        "let_const": "const {name}: {type} = {value};",
        "use": "use {path};",
        "use_all": "use {path}::*;",
        "mod": "mod {name};",
        "pub": "pub {item}",
        "impl_self": "impl Self {{\n{methods}\n}}",
        "new": "fn new({params}) -> Self {{\n{body}\n}}",
        "vec": "vec![{values}]",
        "hashmap": "HashMap::from([({key}, {value})])",
        "option_some": "Some({expr})",
        "option_none": "None",
        "result_ok": "Ok({expr})",
        "result_err": "Err({error})",
        "println": "println!(\"{format}\", {args})",
        "format": "format!(\"{template}\")",
        "clone": "{expr}.clone()",
        "unwrap": "{expr}.unwrap()",
        "expect": "{expr}.expect(\"{message}\")",
        "main": "fn main() {{\n{body}\n}}",
        "test": "#[test]\nfn {name}() {{\n{body}\n}}",
        "derive": "#[derive({traits})]",
        "lifetime": "&'a {type}",
        "reference": "&{expr}",
        "mutable_ref": "&mut {expr}",
    },
    "libraries": {
        "web": {
            "actix-web": {
                "imports": "use actix_web::{{web, App, HttpServer, HttpResponse}};",
                "route": '#[actix_web::{{main}}]\nasync fn main() -> std::io::Result<()> {{\n    HttpServer::new(|| App::new().route("{route}", web::{method}.to({handler})))\n        .bind("{addr}")?\n        .run()\n        .await\n}}',
                "handler": "async fn {name}({params}) -> HttpResponse {{\n{body}\n}}",
                "json_response": "HttpResponse::Ok().json({data})",
            },
            "axum": {
                "imports": "use axum::{{routing::{get, post}, Router, Json}};",
                "route": 'Router::new().route("{route}", {method}.to({handler}))',
                "handler": "async fn {name}({params}) -> Json<{type}> {{\n{body}\n}}",
            },
        },
        "db": {
            "sqlx": {
                "imports": "use sqlx::{{sqlite::SqlitePoolOptions, FromRow}};",
                "pool": 'SqlitePoolOptions::new().connect("{url}").await?',
                "query": "sqlx::query_as::<_, {type}>(\"{query}\")\n    .fetch_all(&pool)\n    .await?",
            },
            "rusqlite": {
                "imports": "use rusqlite::{{Connection, params}};",
                "open": 'Connection::open("{db_path}")?',
                "query": "conn.prepare(\"{query}\")?.query_map(params![{args}], |row| {{\n    Ok({{ {fields} }})\n}})?;",
            },
        },
        "cli": {
            "clap": {
                "imports": "use clap::Parser;",
                "args": "#[derive(Parser)]\nstruct Args {{\n{fields}\n}}",
                "arg_field": "/// {help}\n#[arg(short, long)]\n{name}: {type}",
            },
        },
        "testing": {
            "built_in": {
                "test": "#[test]\nfn {name}() {{\n{body}\n}}",
                "assert_eq": "assert_eq!({actual}, {expected});",
                "assert": "assert!({condition});",
                "should_panic": "#[should_panic]\nfn {name}() {{\n{body}\n}}",
            },
        },
    },
}

# ─────────────────────────────────────────────────
# C
# ─────────────────────────────────────────────────
LANGUAGES["c"] = {
    "file_ext": ".c",
    "comment": "// {text}",
    "comment_block": "/* {text} */",
    "aliases": [],
    "style": {"indent": "    ", "naming": "snake_case"},
    "syntax": {
        "include": '#include <{header}>',
        "include_local": '#include "{header}"',
        "function": "{ret} {name}({params}) {{\n{body}\n}}",
        "function_pointer": "{ret} (*{name})({params})",
        "struct": "struct {name} {{\n{fields}\n}};",
        "enum": "enum {name} {{\n{values}\n}};",
        "typedef_struct": "typedef struct {name} {{\n{fields}\n}} {alias};",
        "return": "return {expr};",
        "if": "if ({condition}) {{\n{body}\n}}",
        "if_else": "if ({condition}) {{\n{body}\n}} else {{\n{else_body}\n}}",
        "for": "for (int {var} = 0; {var} < {limit}; {var}++) {{\n{body}\n}}",
        "while": "while ({condition}) {{\n{body}\n}}",
        "do_while": "do {{\n{body}\n}} while ({condition});",
        "switch": "switch ({expression}) {{\ncase {value}:\n{body}\n    break;\ndefault:\n{default_body}\n}}",
        "malloc": "({type}*)malloc({size} * sizeof({type}))",
        "calloc": "({type}*)calloc({count}, sizeof({type}))",
        "free": "free({ptr});",
        "printf": 'printf("{format}", {args});',
        "scanf": 'scanf("{format}", {args});',
        "main": "int main(int argc, char *argv[]) {{\n{body}\n    return 0;\n}}",
        "define": "#define {name} {value}",
        "ifdef": "#ifdef {name}\n{body}\n#endif",
        "pragma": "#pragma once",
        "null": "NULL",
        "sizeof": "sizeof({type})",
    },
}

# ─────────────────────────────────────────────────
# C++
# ─────────────────────────────────────────────────
LANGUAGES["c++"] = {
    "file_ext": ".cpp",
    "comment": "// {text}",
    "comment_block": "/* {text} */",
    "aliases": ["cpp", "cplusplus"],
    "style": {"indent": "    ", "naming": "snake_case", "type_naming": "PascalCase"},
    "syntax": {
        "include": '#include <{header}>',
        "include_local": '#include "{header}"',
        "using": "using namespace {name};",
        "function": "{ret} {name}({params}) {{\n{body}\n}}",
        "class": "class {name} {{\npublic:\n{public}\nprivate:\n{private}\n}};",
        "class_simple": "class {name} {{\n{body}\n}};",
        "constructor": "{name}({params}) {{\n{body}\n}}",
        "destructor": "~{name}() {{\n{body}\n}}",
        "struct": "struct {name} {{\n{fields}\n}};",
        "namespace": "namespace {name} {{\n{body}\n}}",
        "return": "return {expr};",
        "if": "if ({condition}) {{\n{body}\n}}",
        "if_else": "if ({condition}) {{\n{body}\n}} else {{\n{else_body}\n}}",
        "for": "for (int {var} = 0; {var} < {limit}; {var}++) {{\n{body}\n}}",
        "for_each": "for (const auto& {var} : {iterable}) {{\n{body}\n}}",
        "while": "while ({condition}) {{\n{body}\n}}",
        "try_catch": "try {{\n{body}\n}} catch ({exception} const& {var}) {{\n{handler}\n}}",
        "template": "template <typename {type}>",
        "smart_ptr": "std::unique_ptr<{type}>",
        "shared_ptr": "std::shared_ptr<{type}>",
        "vector": "std::vector<{type}>",
        "map": "std::map<{key_type}, {val_type}>",
        "string": "std::string",
        "cout": 'std::cout << {expr} << std::endl;',
        "auto": "auto {name} = {value};",
        "main": "int main(int argc, char* argv[]) {{\n{body}\n    return 0;\n}}",
        "constexpr": "constexpr {type} {name} = {value};",
    },
}

# ─────────────────────────────────────────────────
# C#
# ─────────────────────────────────────────────────
LANGUAGES["c#"] = {
    "file_ext": ".cs",
    "comment": "// {text}",
    "comment_block": "/* {text} */",
    "aliases": ["csharp", "csharp"],
    "style": {"indent": "    ", "naming": "camelCase", "type_naming": "PascalCase"},
    "syntax": {
        "namespace": "namespace {name}\n{{\n{body}\n}}",
        "using": "using {namespace};",
        "class": "public class {name} {{\n{body}\n}}",
        "class_inherit": "public class {name} : {parent} {{\n{body}\n}}",
        "interface": "public interface {name} {{\n{methods}\n}}",
        "struct": "public struct {name} {{\n{fields}\n}}",
        "enum": "public enum {name} {{\n{values}\n}}",
        "method": "public {ret} {name}({params}) {{\n{body}\n}}",
        "async_method": "public async Task<{ret}> {name}({params}) {{\n{body}\n}}",
        "static_method": "public static {ret} {name}({params}) {{\n{body}\n}}",
        "constructor": "public {name}({params}) {{\n{body}\n}}",
        "property": "public {type} {name} {{ get; set; }}",
        "property_init": "public {type} {name} {{ get; set; }} = {default};",
        "return": "return {expr};",
        "return_void": "return;",
        "if": "if ({condition}) {{\n{body}\n}}",
        "if_else": "if ({condition}) {{\n{body}\n}} else {{\n{else_body}\n}}",
        "for": "for (int {var} = 0; {var} < {limit}; {var}++) {{\n{body}\n}}",
        "foreach": "foreach (var {var} in {iterable}) {{\n{body}\n}}",
        "while": "while ({condition}) {{\n{body}\n}}",
        "try_catch": "try {{\n{body}\n}} catch ({exception} {var}) {{\n{handler}\n}}",
        "var": "var {name} = {value};",
        "list": "new List<{type}>()",
        "dict": "new Dictionary<{key_type}, {val_type}>()",
        "console": "Console.WriteLine({args})",
        "async_await": "await {expr};",
        "main": "static void Main(string[] args) {{\n{body}\n}}",
        "linq": "{source}.Where(x => {predicate}).Select(x => {{ {selector} }})",
        "string_interpolation": '"{template}"',
        "null_check": "{expr} ?? {default}",
        "nullable": "{type}?",
    },
    "libraries": {
        "web": {
            "aspnet": {
                "imports": "using Microsoft.AspNetCore.Mvc;\nusing Microsoft.AspNetCore.Builder;",
                "controller": "[ApiController]\n[Route(\"api/[controller]\")]\npublic class {name}Controller : ControllerBase {{\n{methods}\n}}",
                "get": "[HttpGet(\"{route}\")]\npublic {ret} {name}({params}) {{\n{body}\n}}",
                "post": "[HttpPost(\"{route}\")]\npublic {ret} {name}({params}) {{\n{body}\n}}",
                "json": "return Ok({data});",
            },
        },
    },
}

# ─────────────────────────────────────────────────
# RUBY
# ─────────────────────────────────────────────────
LANGUAGES["ruby"] = {
    "file_ext": ".rb",
    "comment": "# {text}",
    "aliases": ["rb"],
    "style": {"indent": "  ", "naming": "snake_case", "class_naming": "PascalCase"},
    "syntax": {
        "function": "def {name}({params})\n{body}\nend",
        "function_bang": "def {name}!({params})\n{body}\nend",
        "class": "class {name} < {parent}\n{body}\nend",
        "class_simple": "class {name}\n{body}\nend",
        "module": "module {name}\n{body}\nend",
        "initialize": "def initialize({params})\n{body}\nend",
        "return": "return {expr}",
        "if": "if {condition}\n{body}\nend",
        "if_else": "if {condition}\n{body}\nelse\n{else_body}\nend",
        "unless": "unless {condition}\n{body}\nend",
        "each": "{iterable}.each do |{var}|\n{body}\nend",
        "map": "{iterable}.map do |{var}|\n{body}\nend",
        "select": "{iterable}.select do |{var}|\n{condition}\nend",
        "reduce": "{iterable}.reduce({initial}) do |{var}, {acc}|\n{body}\nend",
        "begin_rescue": "begin\n{body}\nrescue {exception} => {var}\n{handler}\nend",
        "puts": "puts {args}",
        "require": "require '{module}'",
        "require_relative": "require_relative '{path}'",
        "attr_accessor": "attr_accessor {names}",
        "attr_reader": "attr_reader {names}",
        "string_interpolation": '"{template}"',
        "block": "do |{params}|\n{body}\nend",
        "lambda": "lambda do |{params}|\n{body}\nend",
        "proc": "Proc.new do |{params}|\n{body}\nend",
        "symbol": ":{name}",
        "hash": "{{ {key}: {value} }}",
        "nil": "nil",
        "true": "true",
        "false": "false",
    },
    "libraries": {
        "web": {
            "rails": {
                "route": "get '{route}', to: '{controller}#{action}'",
                "controller": "class {name}Controller < ApplicationController\n{methods}\nend",
                "action": "def {name}\n{body}\nend",
                "render_json": "render json: {data}",
                "render_json_status": "render json: {data}, status: {code}",
            },
            "sinatra": {
                "imports": "require 'sinatra'",
                "route": "get '{route}' do\n{body}\nend",
                "json_response": "content_type :json\n{data}.to_json",
            },
        },
        "db": {
            "activerecord": {
                "model": "class {name} < ApplicationRecord\n{body}\nend",
                "migration": "class {Name} < ActiveRecord::Migration[{version}]\n  def change\n{body}\n  end\nend",
                "find": "{model}.find({id})",
                "where": "{model}.where({query})",
                "create": "{model}.create({attributes})",
            },
            "sequel": {
                "connect": "DB = Sequel.connect('{conn}')",
                "dataset": "DB[:{table}]",
            },
        },
        "testing": {
            "rspec": {
                "describe": "RSpec.describe {name} do\n{body}\nend",
                "it": "it '{description}' do\n{body}\nend",
                "expect_equal": "expect({actual}).to eq({expected})",
                "before": "before(:each) do\n{body}\nend",
            },
        },
    },
}

# ─────────────────────────────────────────────────
# SQL
# ─────────────────────────────────────────────────
LANGUAGES["sql"] = {
    "file_ext": ".sql",
    "comment": "-- {text}",
    "comment_block": "/* {text} */",
    "aliases": ["mysql", "postgresql", "postgres", "sqlite"],
    "style": {"indent": "  ", "naming": "snake_case"},
    "syntax": {
        "create_table": "CREATE TABLE IF NOT EXISTS {name} (\n{columns}\n);",
        "column": "{name} {type} {constraints}",
        "column_int": "{name} INTEGER PRIMARY KEY",
        "column_serial": "{name} SERIAL PRIMARY KEY",
        "column_varchar": "{name} VARCHAR({length})",
        "column_text": "{name} TEXT",
        "column_timestamp": "{name} TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "column_boolean": "{name} BOOLEAN DEFAULT FALSE",
        "column_float": "{name} REAL",
        "column_unique": "{name} {type} UNIQUE",
        "column_not_null": "{name} {type} NOT NULL",
        "column_default": "{name} {type} DEFAULT {value}",
        "column_fk": "{name} INTEGER REFERENCES {table}({ref_column})",
        "create_index": "CREATE INDEX IF NOT EXISTS {name} ON {table}({columns});",
        "drop_table": "DROP TABLE IF EXISTS {name};",
        "insert": "INSERT INTO {table} ({columns})\nVALUES ({values});",
        "insert_or_ignore": "INSERT OR IGNORE INTO {table} ({columns})\nVALUES ({values});",
        "insert_returning": "INSERT INTO {table} ({columns})\nVALUES ({values})\nRETURNING {returning};",
        "select": "SELECT {columns}\nFROM {table}",
        "select_where": "SELECT {columns}\nFROM {table}\nWHERE {condition};",
        "select_join": "SELECT {columns}\nFROM {table1}\nJOIN {table2} ON {join_condition}",
        "select_left_join": "SELECT {columns}\nFROM {table1}\nLEFT JOIN {table2} ON {join_condition}",
        "select_group": "SELECT {columns}, {agg}({column})\nFROM {table}\nGROUP BY {group_cols};",
        "select_having": "SELECT {columns}\nFROM {table}\nGROUP BY {group_cols}\nHAVING {condition};",
        "select_order": "SELECT {columns}\nFROM {table}\nORDER BY {column} {direction};",
        "select_limit": "SELECT {columns}\nFROM {table}\nLIMIT {limit} OFFSET {offset};",
        "select_distinct": "SELECT DISTINCT {columns}\nFROM {table};",
        "select_count": "SELECT COUNT(*) FROM {table};",
        "select_sum": "SELECT SUM({column}) FROM {table};",
        "select_avg": "SELECT AVG({column}) FROM {table};",
        "select_min": "SELECT MIN({column}) FROM {table};",
        "select_max": "SELECT MAX({column}) FROM {table};",
        "select_search": "SELECT {columns}\nFROM {table}\nWHERE {column} LIKE '%{search}%';",
        "update": "UPDATE {table}\nSET {assignments}\nWHERE {condition};",
        "update_set": "{column} = {value}",
        "delete": "DELETE FROM {table}\nWHERE {condition};",
        "alter_add": "ALTER TABLE {table} ADD COLUMN {name} {type};",
        "alter_drop": "ALTER TABLE {table} DROP COLUMN {name};",
        "create_view": "CREATE VIEW {name} AS\nSELECT {columns}\nFROM {table}\nWHERE {condition};",
        "begin_transaction": "BEGIN;",
        "commit": "COMMIT;",
        "rollback": "ROLLBACK;",
        "upsert_postgres": "INSERT INTO {table} ({columns})\nVALUES ({values})\nON CONFLICT ({conflict_column}) DO UPDATE\nSET {assignments};",
        "window_function": "{function}() OVER (PARTITION BY {partition} ORDER BY {order})",
        "cte": "WITH {name} AS (\n{query}\n)\nSELECT {columns}\nFROM {name};",
        "subquery": "SELECT {columns}\nFROM {table}\nWHERE {column} IN (SELECT {column} FROM {sub_table});",
    },
}

# ─────────────────────────────────────────────────
# R
# ─────────────────────────────────────────────────
LANGUAGES["r"] = {
    "file_ext": ".r",
    "comment": "# {text}",
    "aliases": [],
    "style": {"indent": "  ", "naming": "snake_case"},
    "syntax": {
        "function": "{name} <- function({params}) {{\n{body}\n}}",
        "if": "if ({condition}) {{\n{body}\n}}",
        "if_else": "if ({condition}) {{\n{body}\n}} else {{\n{else_body}\n}}",
        "for": "for ({var} in {iterable}) {{\n{body}\n}}",
        "while": "while ({condition}) {{\n{body}\n}}",
        "library": "library({name})",
        "return": "return({expr})",
        "assign": "{name} <- {value}",
        "dataframe": "data.frame({args})",
        "list": "list({args})",
        "vector": "c({values})",
        "apply": "apply({data}, {margin}, {function})",
        "lapply": "lapply({data}, {function})",
        "sapply": "sapply({data}, {function})",
        "tapply": "tapply({data}, {groups}, {function})",
        "read_csv": 'read.csv("{path}")',
        "write_csv": 'write.csv({data}, "{path}")',
        "print": "print({args})",
        "cat": "cat({args})",
        "pipe": "{data} |> {function}()",
    },
    "libraries": {
        "data": {
            "dplyr": {
                "imports": "library(dplyr)",
                "filter": '{df} |> filter({condition})',
                "select": '{df} |> select({columns})',
                "mutate": '{df} |> mutate({name} = {expr})',
                "group_by": '{df} |> group_by({column})',
                "summarize": '{df} |> summarize({name} = {function}({column}))',
                "arrange": '{df} |> arrange({column})',
                "join": 'left_join({df1}, {df2}, by = "{column}")',
            },
            "ggplot2": {
                "imports": "library(ggplot2)",
                "plot": "ggplot({data}, aes(x = {x}, y = {y})) +\n  geom_{geom}()",
                "theme": "theme_{name}()",
                "labs": 'labs(title = "{title}", x = "{x}", y = "{y}")',
            },
        },
    },
}

# ─────────────────────────────────────────────────
# JAVA
# ─────────────────────────────────────────────────
LANGUAGES["java"] = {
    "file_ext": ".java",
    "comment": "// {text}",
    "comment_block": "/* {text} */",
    "aliases": [],
    "style": {"indent": "    ", "naming": "camelCase", "class_naming": "PascalCase"},
    "syntax": {
        "package": "package {name};",
        "import": "import {module};",
        "class": "public class {name} {\n{body}\n}",
        "class_inherit": "public class {name} extends {parent} {\n{body}\n}",
        "interface": "public interface {name} {\n{methods}\n}",
        "method": "public {ret} {name}({params}) {{\n{body}\n}}",
        "static_method": "public static {ret} {name}({params}) {{\n{body}\n}}",
        "constructor": "public {name}({params}) {{\n{body}\n}}",
        "return": "return {expr};",
        "if": "if ({condition}) {{\n{body}\n}}",
        "if_else": "if ({condition}) {{\n{body}\n}} else {{\n{else_body}\n}}",
        "for": "for (int {var} = 0; {var} < {limit}; {var}++) {{\n{body}\n}}",
        "for_each": "for ({type} {var} : {iterable}) {{\n{body}\n}}",
        "while": "while ({condition}) {{\n{body}\n}}",
        "try_catch": "try {{\n{body}\n}} catch ({exception} {var}) {{\n{handler}\n}}",
        "try_finally": "try {{\n{body}\n}} finally {{\n{handler}\n}}",
        "list": "List<{type}> {name} = new ArrayList<>();",
        "map": "Map<{key_type}, {val_type}> {name} = new HashMap<>();",
        "stream": "{data}.stream()\n    .filter(x -> {predicate})\n    .map(x -> {transform})\n    .collect(Collectors.toList())",
        "sout": "System.out.println({args});",
        "main": "public static void main(String[] args) {{\n{body}\n}}",
        "annotation": "@{name}",
        "nullable": "@Nullable {type}",
        "nonnull": "@NonNull {type}",
        "optional": "Optional<{type}>",
    },
    "libraries": {
        "web": {
            "springboot": {
                "imports": "import org.springframework.web.bind.annotation.*;\nimport org.springframework.stereotype.Controller;",
                "controller": "@RestController\n@RequestMapping(\"/{path}\")\npublic class {name}Controller {{\n{methods}\n}}",
                "get_mapping": "@GetMapping(\"/{route}\")\npublic {ret} {name}({params}) {{\n{body}\n}}",
                "post_mapping": "@PostMapping(\"/{route}\")\npublic {ret} {name}(@RequestBody {type} {param}) {{\n{body}\n}}",
                "response_body": "return ResponseEntity.ok({data});",
            },
        },
    },
}

# ─────────────────────────────────────────────────
# MONGODB (query language)
# ─────────────────────────────────────────────────
LANGUAGES["mongodb"] = {
    "file_ext": ".js",
    "comment": "// {text}",
    "aliases": ["mongo"],
    "style": {"indent": "  ", "naming": "camelCase"},
    "syntax": {
        "find": 'db.{collection}.find({query})',
        "find_one": 'db.{collection}.findOne({query})',
        "find_projection": 'db.{collection}.find({query}, {projection})',
        "insert_one": 'db.{collection}.insertOne({document})',
        "insert_many": 'db.{collection}.insertMany([{documents}])',
        "update_one": 'db.{collection}.updateOne({query}, {{"$set": {update}}})',
        "update_many": 'db.{collection}.updateMany({query}, {{"$set": {update}}})',
        "delete_one": 'db.{collection}.deleteOne({query})',
        "delete_many": 'db.{collection}.deleteMany({query})',
        "aggregate": 'db.{collection}.aggregate([{stages}])',
        "group": '{{"$group": {{"_id": "{field}", "count": {{"$sum": 1}}}}}}',
        "match": '{{"$match": {query}}}',
        "project": '{{"$project": {projection}}}',
        "sort": '{{"$sort": {{"{field}": {order}}}}}',
        "limit": '{{"$limit": {n}}}',
        "lookup": '{{"$lookup": {{"from": "{collection}", "localField": "{local}", "foreignField": "{foreign}", "as": "{as}"}}}}',
        "unwind": '{{"$unwind": "${field}"}}',
        "create_collection": 'db.createCollection("{name}")',
        "create_index": 'db.{collection}.createIndex({{ "{field}": 1 }})',
        "distinct": 'db.{collection}.distinct("{field}")',
        "count": 'db.{collection}.countDocuments({query})',
        "find_sort_limit": 'db.{collection}.find({query}).sort({sort}).limit({limit})',
    },
}

# ─────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────

def get_language(name: str) -> dict | None:
    """Look up a language by name or alias."""
    key = (name or "").strip().lower()
    if key in LANGUAGES:
        return LANGUAGES[key]
    for lang_name, lang in LANGUAGES.items():
        if key in [a.lower() for a in lang.get("aliases", [])]:
            return lang
        if key == lang_name:
            return lang
    return None


def list_languages() -> list[str]:
    """Return all known language names."""
    return sorted(LANGUAGES.keys())


def get_syntax(lang_name: str, rule: str) -> str | None:
    """Get a syntax rule from a language."""
    lang = get_language(lang_name)
    if lang is None:
        return None
    return lang.get("syntax", {}).get(rule)


def get_library(lang_name: str, category: str, library: str) -> dict | None:
    """Get library knowledge from a language."""
    lang = get_language(lang_name)
    if lang is None:
        return None
    return lang.get("libraries", {}).get(category, {}).get(library)


def detect_language(text: str) -> str | None:
    """Detect which language is mentioned in text."""
    lowered = (text or "").lower()
    for lang_name in sorted(LANGUAGES.keys(), key=len, reverse=True):
        lang = LANGUAGES[lang_name]
        for alias in [lang_name] + lang.get("aliases", []):
            if alias.lower() in lowered:
                return lang_name
    return None
