import os
import re
import json

from cognition.language_cortex import normalize_language

# Per-kind definitions for the vertical full-stack generator.
FULLSTACK_KINDS = {
    "food_delivery": {
        "title": "Food Delivery",
        "tagline": "Order meals from local kitchens",
        "mode": "cart",
        "collection": "menu",
        "item_verb": "Dish",
        "item_fields": ("name", "price"),
        "seed": [
            ("Margherita Pizza", 12), ("Paneer Tikka", 14), ("Chicken Burger", 9),
            ("Mango Lassi", 4), ("Tiramisu", 6), ("Caesar Salad", 8),
        ],
        "cart_label": "Your Order",
        "checkout_label": "Delivery address",
        "schema": """-- Food delivery schema: users, sessions, menu items, carts, orders.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT,
    price REAL NOT NULL, rating REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS cart_items (
    username TEXT NOT NULL, item_id INTEGER NOT NULL, qty INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (username, item_id)
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, address TEXT,
    total REAL NOT NULL, status TEXT DEFAULT 'placed',
    payment_method TEXT, payment_last4 TEXT, payment_status TEXT DEFAULT 'paid',
    items TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    },
    "ecommerce": {
        "title": "E-Commerce Store",
        "tagline": "Browse, cart and buy products",
        "mode": "cart",
        "collection": "products",
        "item_verb": "Product",
        "item_fields": ("name", "price"),
        "seed": [
            ("Wireless Headphones", 79), ("Mechanical Keyboard", 59), ("4K Monitor", 249),
            ("USB-C Hub", 35), ("Desk Lamp", 22), ("Laptop Stand", 29),
        ],
        "cart_label": "Your Cart",
        "checkout_label": "Shipping address",
        "schema": """-- E-commerce schema: users, sessions, products, carts, orders.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT,
    price REAL NOT NULL, rating REAL DEFAULT 0, stock INTEGER DEFAULT 100
);
CREATE TABLE IF NOT EXISTS cart_items (
    username TEXT NOT NULL, item_id INTEGER NOT NULL, qty INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (username, item_id)
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, address TEXT,
    total REAL NOT NULL, status TEXT DEFAULT 'placed',
    payment_method TEXT, payment_last4 TEXT, payment_status TEXT DEFAULT 'paid',
    items TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    },
    "task_tracker": {
        "title": "Task Tracker",
        "tagline": "Organize your daily tasks",
        "mode": "collection",
        "collection": "tasks",
        "item_verb": "Task",
        "item_fields": ("title", "priority"),
        "seed": [("Plan the sprint", "high"), ("Write docs", "medium"), ("Fix the login bug", "high")],
        "cart_label": "Task List",
        "checkout_label": "",
        "schema": """-- Task tracker schema: users, sessions, tasks.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, title TEXT NOT NULL,
    done INTEGER DEFAULT 0, priority TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    },
    "chat": {
        "title": "Chat Room",
        "tagline": "Real-time room chat (Server-Sent Events)",
        "mode": "collection",
        "collection": "messages",
        "item_verb": "Message",
        "item_fields": ("user", "text"),
        "seed": [],
        "cart_label": "Messages",
        "checkout_label": "",
        "schema": """-- Chat schema: users, sessions, messages.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    },
    "booking": {
        "title": "Booking",
        "tagline": "Reserve time slots with local pros",
        "mode": "cart",
        "collection": "services",
        "item_verb": "Service",
        "item_fields": ("name", "price"),
        "seed": [
            ("Haircut", 25), ("Massage", 60), ("House Cleaning", 40),
            ("Tutoring", 30), ("Plumbing Visit", 55), ("Photoshoot", 120),
        ],
        "cart_label": "Your Booking",
        "checkout_label": "Preferred date/time",
        "schema": """-- Booking schema: users, sessions, services, carts, orders.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT,
    price REAL NOT NULL, rating REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS cart_items (
    username TEXT NOT NULL, item_id INTEGER NOT NULL, qty INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (username, item_id)
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, address TEXT,
    total REAL NOT NULL, status TEXT DEFAULT 'placed',
    payment_method TEXT, payment_last4 TEXT, payment_status TEXT DEFAULT 'paid',
    items TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    },
    "blog": {
        "title": "Blog / CMS",
        "tagline": "Publish articles for everyone",
        "mode": "collection",
        "collection": "posts",
        "item_verb": "Post",
        "item_fields": ("title", "body"),
        "public_read": True,
        "seed": [],
        "cart_label": "Articles",
        "checkout_label": "",
        "schema": """-- Blog schema: users, sessions, posts.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, title TEXT NOT NULL,
    body TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    },
    "notes": {
        "title": "Notes",
        "tagline": "Private, searchable notes",
        "mode": "collection",
        "collection": "notes",
        "item_verb": "Note",
        "item_fields": ("title", "body"),
        "public_read": False,
        "seed": [],
        "cart_label": "My Notes",
        "checkout_label": "",
        "schema": """-- Notes schema: users, sessions, notes.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, title TEXT NOT NULL,
    body TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    },
    "fitness": {
        "title": "Fitness Tracker",
        "tagline": "Log workouts and progress",
        "mode": "collection",
        "collection": "workouts",
        "item_verb": "Workout",
        "item_fields": ("title", "body"),
        "public_read": False,
        "seed": [],
        "cart_label": "Workouts",
        "checkout_label": "",
        "schema": """-- Fitness schema: users, sessions, workouts.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY, username TEXT NOT NULL, title TEXT NOT NULL,
    body TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
    },
}

_KIND_ALIASES = {
    "food": "food_delivery", "delivery": "food_delivery", "zomato": "food_delivery",
    "swiggy": "food_delivery", "restaurant": "food_delivery",
    "ecommerce": "ecommerce", "ecommerce store": "ecommerce", "store": "ecommerce",
    "shop": "ecommerce", "shopping": "ecommerce",
    "booking": "booking", "bookings": "booking", "reservation": "booking",
    "reservations": "booking", "appointment": "booking", "appointments": "booking",
    "task": "task_tracker", "tasks": "task_tracker", "todo": "task_tracker",
    "tracker": "task_tracker",
    "chat": "chat", "chatroom": "chat", "messaging": "chat", "messages": "chat",
    "blog": "blog", "blogs": "blog", "cms": "blog", "articles": "blog", "article": "blog",
    "notes": "notes", "note": "notes", "notebook": "notes",
    "fitness": "fitness", "workout": "fitness", "workouts": "fitness", "health": "fitness",
}


def _normalize_kind(kind):
    key = str(kind or "").strip().lower().replace("-", " ").replace("_", " ")
    if key in FULLSTACK_KINDS:
        return key
    return _KIND_ALIASES.get(key) or _KIND_ALIASES.get(key.split()[0]) or None


_BACKEND_ALIASES = {
    "fl": "flask", "flask": "flask",
    "dj": "django", "django": "django",
    "express": "express", "expressjs": "express", "node": "express",
    "fastify": "fastify", "fx": "fastify", "fastapi": "fastify",
}


def _normalize_backend(backend):
    return _BACKEND_ALIASES.get(str(backend or "").strip().lower()) or "flask"


_FRONTEND_ALIASES = {
    "react": "react", "reactjs": "react", "vite": "react",
    "single": "single", "html": "single", "vanilla": "single",
}


def _normalize_frontend(frontend):
    return _FRONTEND_ALIASES.get(str(frontend or "").strip().lower()) or "react"


def _pg_schema(sql):
    """Translate the SQLite schema SQL to a PostgreSQL variant (SERIAL ids)."""
    return sql.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")


def _pg_seed(seed_sql):
    """Translate SQLite INSERT OR IGNORE seed lines to Postgres idempotent inserts."""
    return (seed_sql.replace("INSERT OR IGNORE INTO", "INSERT INTO")
                    .replace('")', ' ON CONFLICT DO NOTHING")'))


def _node_cart_seeds(table, seed, is_pg):
    """Node seed statements for cart kinds (sqlite or postgres flavor)."""
    stmts = []
    for i, (name, price) in enumerate(seed):
        base = "INSERT OR IGNORE INTO {} (id, name, price) VALUES ({}, '{}', {})".format(
            table, i + 1, name.replace(chr(39), chr(39) * 2), price
        )
        if is_pg:
            base = base.replace("INSERT OR IGNORE INTO", "INSERT INTO") + " ON CONFLICT DO NOTHING"
        stmts.append('await db.run("{}")'.format(base))
    return "; ".join(stmts)


# ---- helpers for the deterministic app debugger (route analysis) ----------

def _backend_segments(path):
    segs = [s for s in path.split("/") if s != ""]
    return tuple("{}" if (s == "{}" or s.startswith("<") or s.startswith(":")) else s for s in segs)


def _frontend_segments(expr):
    """Normalize a frontend api()/EventSource() path expression into segments.

    String-literal pieces are kept verbatim; dynamic expressions (identifiers,
    template literals, numeric ids) collapse into a single '{}' wildcard."""
    parts, pos = [], 0
    for m in re.finditer(r"(['\"`])(.*?)\1", expr):
        parts.append(("dyn", expr[pos:m.start()]))
        parts.append(("lit", m.group(2)))
        pos = m.end()
    parts.append(("dyn", expr[pos:]))
    out = ""
    for kind, s in parts:
        if kind == "lit":
            out += s
        elif s.strip():
            out += "{}"
    out = out.split("?")[0]
    out = re.sub(r"\s+", "", out)
    out = out.rstrip("/") or "/"
    segs = [s for s in out.split("/") if s != ""]
    return tuple("{}" if s == "{}" else s for s in segs)


def _segments_match(a, b):
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x == "{}" or y == "{}":
            continue
        if x != y:
            return False
    return True


def _display(expr):
    parts = re.findall(r"(['\"`])(.*?)\1", expr)
    return "".join(p[1] for p in parts) or expr.strip()


def _frontend_calls(text):
    calls = []
    for m in re.finditer(r"\bapi\(\s*", text):
        end = _balanced_end(text, m.end() - 1)
        if end is None:
            continue
        call = text[m.end():end]
        arg = _first_arg(call, 0)
        if not re.search(r"['\"`]", arg):
            continue
        method = None
        mm = re.search(r"method\s*:\s*['\"]([A-Za-z]+)['\"]", call)
        if mm:
            method = mm.group(1).upper()
        calls.append((method, arg))
    for m in re.finditer(r"EventSource\(\s*(?:API\s*\+\s*)?(['\"`])(.*?)\1", text):
        calls.append(("GET", m.group(2)))
    return calls


def _balanced_end(text, start):
    """Index of the ')' closing the paren opened at text[start], or None."""
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        elif ch in "'\"`":
            quote = ch
            i += 1
            while i < len(text):
                if text[i] == "\\":
                    i += 2
                    continue
                if text[i] == quote:
                    break
                i += 1
            if i >= len(text):
                return None
    return None


def _first_arg(text, start):
    depth, buf = 0, ""
    for ch in text[start:]:
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth == 0:
                break
            depth -= 1
        elif ch == "," and depth == 0:
            break
        buf += ch
    return buf


def _sanitize(text, fallback="Untitled"):
    text = (text or "").strip()
    text = re.sub(r"[^A-Za-z0-9 _\-\.]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:60] or fallback


def _slug(text):
    return re.sub(r"[^a-z0-9_\-]+", "-", (text or "").lower()).strip("-") or "app"


def json_dumps(obj):
    return json.dumps(obj, indent=2)


# Shared helpers reused by every full-stack backend template.
_FULLSTACK_BACKEND_COMMON = '''# Auto-generated by the Aashu Virtual Brain (deterministic, no LLM).
# Production-shaped: SQLite (WAL) by default, PostgreSQL when DATABASE_URL is set.
# PBKDF2 password hashing, DB-backed sessions. Point DATABASE_URL at a managed
# Postgres (or DATABASE_PATH at a shared volume) to run many gunicorn workers /
# app instances against one store.
import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

USING_PG = bool(os.environ.get("DATABASE_URL"))
if USING_PG:
    import psycopg
    from psycopg.rows import dict_row

    class _Db:
        """Proxy that rewrites ? placeholders to %s on a psycopg connection."""

        def __init__(self, conn):
            self.conn = conn

        def execute(self, sql, *args):
            return self.conn.execute(_q(sql), *args)

        def commit(self):
            return self.conn.commit()

        def rollback(self):
            return self.conn.rollback()

        def close(self):
            return self.conn.close()

app = Flask(__name__, static_folder=None)

DB_PATH = os.environ.get("DATABASE_PATH", str(Path(__file__).resolve().parent / "app.db"))


def _q(sql):
    """Translate ? placeholders to %s when talking to PostgreSQL."""
    return sql.replace("?", "%s") if USING_PG else sql


def get_db():
    if USING_PG:
        return _Db(psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row))
    db = sqlite3.connect(DB_PATH, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    return db


def _rows(db, sql, args=()):
    return [dict(r) for r in db.execute(_q(sql), args).fetchall()]


def _one(db, sql, args=()):
    row = db.execute(_q(sql), args).fetchone()
    return dict(row) if row else None


def _is_unique_error(exc):
    if USING_PG:
        return getattr(exc, "sqlstate", "") == "23505"
    return isinstance(exc, sqlite3.IntegrityError)


def _query_args():
    """?q= search term, ?limit= page size (<=200), ?offset= paging cursor."""
    try:
        limit = min(max(int(request.args.get("limit", 50)), 1), 200)
    except (TypeError, ValueError):
        limit = 50
    try:
        offset = max(int(request.args.get("offset", 0)), 0)
    except (TypeError, ValueError):
        offset = 0
    return (request.args.get("q") or "").strip(), limit, offset


def _like_pattern(q):
    return "%" + q.replace("\\\\", "\\\\\\\\").replace("%", "\\\\%").replace("_", "\\\\_") + "%"


def _hash_password(password, salt):
    # PBKDF2-SHA256, 600k iterations, per-user salt. Stdlib only.
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 600_000
    ).hex()


def _new_session(db, username):
    token = secrets.token_hex(16)
    db.execute(_q("INSERT INTO sessions (token, username) VALUES (?, ?)"), (token, username))
    return token


def _current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    with closing(get_db()) as db:
        row = db.execute(
            _q("SELECT username FROM sessions WHERE token = ?"), (header[7:].strip(),)
        ).fetchone()
        return row["username"] if row else None


def _require_user():
    return _current_user()


@app.get("/api/auth/me")
def me():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": user})


@app.post("/api/auth/register")
def register():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    if len(username) < 3 or len(password) < 4:
        return jsonify({"error": "Username (>=3 chars) and password (>=4 chars) required"}), 400
    salt = secrets.token_hex(8)
    with closing(get_db()) as db, db:
        try:
            db.execute(
                _q("INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)"),
                (username, salt, _hash_password(password, salt)),
            )
        except Exception as exc:
            if _is_unique_error(exc):
                return jsonify({"error": "Username already taken"}), 409
            raise
        token = _new_session(db, username)
    return jsonify({"token": token, "user": username}), 201


@app.post("/api/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    with closing(get_db()) as db:
        row = db.execute(
            _q("SELECT salt, password_hash FROM users WHERE username = ?"), (username,)
        ).fetchone()
    if not row or row["password_hash"] != _hash_password(password, row["salt"]):
        return jsonify({"error": "Invalid credentials"}), 401
    with closing(get_db()) as db, db:
        token = _new_session(db, username)
    return jsonify({"token": token, "user": username})


@app.post("/api/auth/logout")
def logout():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        with closing(get_db()) as db, db:
            db.execute(_q("DELETE FROM sessions WHERE token = ?"), (header[7:].strip(),))
    return jsonify({"ok": True})


@app.after_request
def _cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, PATCH, OPTIONS"
    return response


@app.after_request
def _log_request(response):
    import sys
    sys.stderr.write(f"[api] {request.method} {request.full_path} -> {response.status_code}\\n")
    return response


@app.get("/healthz")
def healthz():
    with closing(get_db()) as db:
        db.execute(_q("SELECT 1")).fetchone()
    return jsonify({"status": "ok"})


def _init_db():
    with closing(get_db()) as db:
        if USING_PG:
            db.execute({{SCHEMA_PG}})
            {{SEED_SQL_PG}}
        else:
            db.executescript({{SCHEMA}})
            {{SEED_SQL}}
        db.commit()


_init_db()


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
SPA_INDEX = FRONTEND_DIR / "dist" / "index.html"
if not SPA_INDEX.exists():
    SPA_INDEX = FRONTEND_DIR / "index.html"


@app.get("/")
def index():
    return send_from_directory(SPA_INDEX.parent, SPA_INDEX.name)


@app.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(SPA_INDEX.parent / "assets", filename)


@app.errorhandler(404)
def spa_fallback(err):
    if request.path.startswith("/api/") or request.path == "/healthz":
        return jsonify({"error": "Not found"}), 404
    if SPA_INDEX.exists():
        return send_from_directory(SPA_INDEX.parent, SPA_INDEX.name)
    return jsonify({"error": "Not found"}), 404
'''

_FULLSTACK_BACKEND_CART = _FULLSTACK_BACKEND_COMMON + '''CATALOG_TABLE = "{{TABLE}}"


def _order_dict(o):
    return {
        "id": o["id"], "user": o["username"], "items": json.loads(o["items"] or "{}"),
        "total": o["total"], "address": o["address"], "status": o["status"],
        "created_at": o["created_at"],
        "payment": {
            "method": o["payment_method"], "last4": o["payment_last4"],
            "amount": o["total"], "status": o["payment_status"],
        },
    }


@app.get("/api/{{COLLECTION}}")
def list_items():
    q, limit, offset = _query_args()
    where, args = "", []
    if q:
        where = "WHERE name LIKE ? ESCAPE '\\\\'"
        args = [_like_pattern(q)]
    with closing(get_db()) as db:
        total = _one(db, "SELECT COUNT(*) AS n FROM " + CATALOG_TABLE + " " + where, args)["n"]
        items = _rows(db, "SELECT id, name, category, price, rating FROM " + CATALOG_TABLE + " " + where + " ORDER BY id LIMIT ? OFFSET ?", args + [limit, offset])
    return jsonify({"items": items, "total": total, "limit": limit, "offset": offset})


@app.get("/api/cart")
def get_cart():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    with closing(get_db()) as db:
        rows = _rows(db, "SELECT item_id, qty FROM cart_items WHERE username = ?", (user,))
    return jsonify({"items": {str(r["item_id"]): r["qty"] for r in rows}})


@app.post("/api/cart")
def add_to_cart():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    body = request.get_json(silent=True) or {}
    try:
        item_id = int(body.get("item_id", 0))
        qty = int(body.get("qty", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid item"}), 400
    with closing(get_db()) as db, db:
        item = _one(db, "SELECT id FROM " + CATALOG_TABLE + " WHERE id = ?", (item_id,))
        if not item:
            return jsonify({"error": "Item not found"}), 404
        db.execute(
            "INSERT INTO cart_items (username, item_id, qty) VALUES (?, ?, ?) "
            "ON CONFLICT(username, item_id) DO UPDATE SET qty = qty + excluded.qty",
            (user, item_id, qty),
        )
        rows = _rows(db, "SELECT item_id, qty FROM cart_items WHERE username = ?", (user,))
    return jsonify({"cart": {str(r["item_id"]): r["qty"] for r in rows}})


@app.post("/api/orders")
def place_order():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    body = request.get_json(silent=True) or {}
    payment = body.get("payment") or {}
    with closing(get_db()) as db, db:
        cart = _rows(db, "SELECT item_id, qty FROM cart_items WHERE username = ?", (user,))
        if not cart:
            return jsonify({"error": "Cart is empty"}), 400
        ids = ",".join(str(c["item_id"]) for c in cart)
        by_id = {i["id"]: i for i in _rows(db, "SELECT id, price FROM " + CATALOG_TABLE + " WHERE id IN (" + ids + ")")}
        order_items = {str(c["item_id"]): c["qty"] for c in cart}
        total = round(sum(by_id[c["item_id"]]["price"] * c["qty"] for c in cart), 2)
        cur = db.execute(
            "INSERT INTO orders (username, address, total, payment_method, payment_last4, items) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user, str(body.get("address", "")) or "Pickup", total,
             str(payment.get("method", "card")), str(payment.get("last4", "")),
             json.dumps(order_items)),
        )
        db.execute("DELETE FROM cart_items WHERE username = ?", (user,))
        order = _one(db, "SELECT * FROM orders WHERE id = ?", (cur.lastrowid,))
    return jsonify({"order": _order_dict(order)}), 201


@app.get("/api/orders")
def list_orders():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    with closing(get_db()) as db:
        rows = _rows(db, "SELECT * FROM orders WHERE username = ? ORDER BY id", (user,))
    return jsonify({"orders": [_order_dict(o) for o in rows]})


@app.post("/api/orders/<int:order_id>/advance")
def advance_order(order_id):
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    statuses = ["placed", "accepted", "delivered"]
    with closing(get_db()) as db, db:
        row = db.execute(
            "SELECT * FROM orders WHERE id = ? AND username = ?", (order_id, user)
        ).fetchone()
        if not row:
            return jsonify({"error": "Order not found"}), 404
        idx = statuses.index(row["status"]) if row["status"] in statuses else 0
        if idx < len(statuses) - 1:
            db.execute("UPDATE orders SET status = ? WHERE id = ?", (statuses[idx + 1], order_id))
        order = _one(db, "SELECT * FROM orders WHERE id = ?", (order_id,))
    return jsonify({"order": _order_dict(order)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
'''

_FULLSTACK_BACKEND_TASKS = _FULLSTACK_BACKEND_COMMON + '''TASK_FIELDS = "id, username AS user, title, done, priority, created_at"


@app.get("/api/tasks")
def list_tasks():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    q, limit, offset = _query_args()
    where, args = "username = ?", [user]
    if q:
        where += " AND title LIKE ? ESCAPE '\\\\'"
        args.append(_like_pattern(q))
    with closing(get_db()) as db:
        total = _one(db, "SELECT COUNT(*) AS n FROM tasks WHERE " + where, args)["n"]
        tasks = _rows(db, "SELECT " + TASK_FIELDS + " FROM tasks WHERE " + where + " ORDER BY id DESC LIMIT ? OFFSET ?", args + [limit, offset])
    return jsonify({"tasks": tasks, "total": total, "limit": limit, "offset": offset})


@app.post("/api/tasks")
def add_task():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    body = request.get_json(silent=True) or {}
    title = str(body.get("title", "")).strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400
    with closing(get_db()) as db, db:
        cur = db.execute(
            "INSERT INTO tasks (username, title, priority) VALUES (?, ?, ?)",
            (user, title, str(body.get("priority", "medium"))),
        )
        task = _one(db, "SELECT " + TASK_FIELDS + " FROM tasks WHERE id = ?", (cur.lastrowid,))
    return jsonify({"task": task}), 201


@app.post("/api/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    with closing(get_db()) as db, db:
        row = db.execute(
            "SELECT id FROM tasks WHERE id = ? AND username = ?", (task_id, user)
        ).fetchone()
        if not row:
            return jsonify({"error": "Task not found"}), 404
        db.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
        task = _one(db, "SELECT " + TASK_FIELDS + " FROM tasks WHERE id = ?", (task_id,))
    return jsonify({"task": task})


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    with closing(get_db()) as db, db:
        cur = db.execute(
            "DELETE FROM tasks WHERE id = ? AND username = ?", (task_id, user)
        )
        return jsonify({"deleted": cur.rowcount > 0})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
'''

_FULLSTACK_BACKEND_MESSAGES = _FULLSTACK_BACKEND_COMMON + '''import time
from flask import Response

MSG_FIELDS = "id, username AS user, text, created_at"


@app.get("/api/messages")
def list_messages():
    q, limit, offset = _query_args()
    where, args = "", []
    if q:
        where = "WHERE text LIKE ? ESCAPE '\\\\'"
        args = [_like_pattern(q)]
    with closing(get_db()) as db:
        total = _one(db, "SELECT COUNT(*) AS n FROM messages " + where, args)["n"]
        messages = _rows(db, "SELECT " + MSG_FIELDS + " FROM messages " + where + " ORDER BY id DESC LIMIT ? OFFSET ?", args + [limit, offset])
    return jsonify({"messages": messages, "total": total, "limit": limit, "offset": offset})


@app.get("/api/messages/stream")
def message_stream():
    def gen():
        last_id = 0
        while True:
            with closing(get_db()) as db:
                rows = _rows(db, "SELECT " + MSG_FIELDS + " FROM messages WHERE id > ? ORDER BY id", (last_id,))
            for r in rows:
                last_id = r["id"]
                yield "data: " + json.dumps(r) + "\\n\\n"
            time.sleep(1)
    return Response(gen(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/messages")
def post_message():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    body = request.get_json(silent=True) or {}
    text = str(body.get("text", "")).strip()
    if not text:
        return jsonify({"error": "Message text is required"}), 400
    with closing(get_db()) as db, db:
        cur = db.execute("INSERT INTO messages (username, text) VALUES (?, ?)", (user, text))
        msg = _one(db, "SELECT " + MSG_FIELDS + " FROM messages WHERE id = ?", (cur.lastrowid,))
    return jsonify({"message": msg}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
'''

_FULLSTACK_BACKEND_COLLECTION = _FULLSTACK_BACKEND_COMMON + '''COLLECTION_TABLE = "{{TABLE}}"
COLLECTION_FIELDS = "id, username AS user, title, body, created_at"


def _read_guard():
    if {{PUBLIC_READ_CHECK}}:
        user = _require_user()
        if not user:
            return None
    return True


@app.get("/api/{{COLLECTION}}")
def list_collection():
    if _read_guard() is None:
        return jsonify({"error": "Not authenticated"}), 401
    q, limit, offset = _query_args()
    where, args = "", []
    if q:
        where = "WHERE (title LIKE ? ESCAPE '\\\\' OR body LIKE ? ESCAPE '\\\\')"
        args = [_like_pattern(q), _like_pattern(q)]
    with closing(get_db()) as db:
        total = _one(db, "SELECT COUNT(*) AS n FROM " + COLLECTION_TABLE + " " + where, args)["n"]
        rows = _rows(db, "SELECT " + COLLECTION_FIELDS + " FROM " + COLLECTION_TABLE + " " + where + " ORDER BY id DESC LIMIT ? OFFSET ?", args + [limit, offset])
    return jsonify({"{{COLLECTION}}": rows, "total": total, "limit": limit, "offset": offset})


@app.post("/api/{{COLLECTION}}")
def add_collection_item():
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    body = request.get_json(silent=True) or {}
    title = str(body.get("title", "")).strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400
    text = str(body.get("body", "")).strip()
    with closing(get_db()) as db, db:
        cur = db.execute(
            "INSERT INTO " + COLLECTION_TABLE + " (username, title, body) VALUES (?, ?, ?)",
            (user, title, text),
        )
        item = _one(db, "SELECT " + COLLECTION_FIELDS + " FROM " + COLLECTION_TABLE + " WHERE id = ?", (cur.lastrowid,))
    return jsonify({"item": item}), 201


@app.delete("/api/{{COLLECTION}}/<int:item_id>")
def delete_collection_item(item_id):
    user = _require_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    with closing(get_db()) as db, db:
        cur = db.execute(
            "DELETE FROM " + COLLECTION_TABLE + " WHERE id = ? AND username = ?", (item_id, user)
        )
        return jsonify({"deleted": cur.rowcount > 0})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
'''

_FULLSTACK_FRONTEND_CART = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>%NAME%</title>
<style>
  :root { --bg: #f4f4f9; --fg: #22223b; --card: #ffffff; --accent: #6c63ff; --border: #ddd; }
  [data-theme="dark"] { --bg: #16161d; --fg: #e8e8f0; --card: #23232e; --accent: #8f8bff; --border: #33334a; }
  body { margin: 0; font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--fg); }
  header { background: var(--accent); color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
  main { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; }
  button { background: var(--accent); color: #fff; border: 0; padding: .5rem 1rem; border-radius: 6px; cursor: pointer; }
  input { padding: .5rem; border-radius: 6px; border: 1px solid var(--border); width: 100%; box-sizing: border-box; }
  .price { color: var(--accent); font-weight: 600; }
  .empty { opacity: .6; font-style: italic; }
  #orders { list-style: none; padding: 0; }
  #authBar { display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
  #authBar input { width: auto; }
  .badge { background: rgba(255,255,255,.2); padding: .25rem .6rem; border-radius: 999px; }
</style>
</head>
<body>
<header>
  <h1>%TITLE%</h1>
  <div id="authBar">
    <input id="authUser" placeholder="username" />
    <input id="authPass" type="password" placeholder="password" />
    <button onclick="auth('login')">Login</button>
    <button onclick="auth('register')">Register</button>
    <button onclick="logout()" id="logoutBtn" hidden>Logout</button>
    <span id="whoami" class="badge" hidden></span>
    <button onclick="document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark'">Toggle theme</button>
  </div>
</header>
<main>
  <p>%TAGLINE%</p>
  <h2>%ITEM_VERB%s</h2>
  <input id="search" placeholder="Search %COLLECTION%..." oninput="loadItems(true)" />
  <div id="items" class="grid"></div>
  <button id="moreBtn" hidden onclick="loadMore()">Load more</button>
  <h2>%CART_LABEL%</h2>
  <div id="cart"></div>
  <h2>Orders</h2>
  <ul id="orders"></ul>
</main>
<script>
  const API = '%API_BASE%';
  const KEY = 'aashu_token_' + '%COLLECTION%';
  let token = localStorage.getItem(KEY) || '';
  function headers(json) {
    const h = json ? {'Content-Type': 'application/json'} : {};
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
  }
  async function api(path, options) {
    options = options || {};
    options.headers = Object.assign(headers(options.body), options.headers || {});
    const res = await fetch(API + path, options);
    return res.json();
  }
  function guard(data) {
    if (data && data.error) { alert(data.error); return true; }
    return false;
  }
  async function auth(mode) {
    const username = document.getElementById('authUser').value.trim();
    const password = document.getElementById('authPass').value;
    if (!username || !password) { alert('Enter a username and password'); return; }
    const data = await api('/api/auth/' + mode, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ username, password }) });
    if (guard(data)) return;
    token = data.token;
    localStorage.setItem(KEY, token);
    loadAuth(); loadCart(); loadOrders();
  }
  async function logout() {
    await api('/api/auth/logout', { method: 'POST' });
    token = '';
    localStorage.removeItem(KEY);
    loadAuth(); loadCart(); loadOrders();
  }
  async function loadAuth() {
    const whoami = document.getElementById('whoami');
    if (!token) { whoami.hidden = true; document.getElementById('logoutBtn').hidden = true; return; }
    const data = await api('/api/auth/me');
    if (data && data.user) {
      whoami.textContent = 'Signed in as ' + data.user;
      whoami.hidden = false;
      document.getElementById('logoutBtn').hidden = false;
    }
  }
  let offset = 0, total = 0;
  async function loadItems(reset) {
    if (reset) { offset = 0; }
    const q = (document.getElementById('search') || {}).value || '';
    const data = await api('/api/%COLLECTION%?q=' + encodeURIComponent(q) + '&limit=6&offset=' + offset);
    if (guard(data)) return;
    total = data.total || 0;
    const items = data.items || [];
    const grid = document.getElementById('items');
    if (reset) grid.innerHTML = '';
    grid.innerHTML += items.map(i => `
      <div class="card">
        <strong>${i.name}</strong>
        <div class="price">$${i.price.toFixed(2)}</div>
        <button onclick="addToCart(${i.id})">Add</button>
      </div>`).join('') || '<div class="empty">No items found.</div>';
    document.getElementById('moreBtn').hidden = (offset + items.length) >= total;
  }
  async function loadMore() { offset += 6; loadItems(false); }
  async function loadCart() {
    if (!token) { document.getElementById('cart').innerHTML = '<div class="empty">Log in to see your %CART_LABEL%.</div>'; return; }
    const data = await api('/api/cart');
    if (guard(data)) return;
    const keys = Object.keys(data.items || {});
    document.getElementById('cart').innerHTML = keys.length ? keys.map(k => `
      <div class="card">Item #${k} &times; ${data.items[k]}</div>`).join('') : '<div class="empty">Cart is empty.</div>';
    if (keys.length) {
      const checkout = document.createElement('div');
      checkout.innerHTML = '<input id="addr" placeholder="%CART_LABEL% / address" /><br>' +
        '<input id="card4" placeholder="Card last 4 digits" maxlength="4" />' +
        '<input id="expiry" placeholder="MM/YY" maxlength="5" /><br>' +
        '<button onclick="placeOrder()">Pay &amp; place order</button>';
      document.getElementById('cart').appendChild(checkout);
    }
  }
  async function loadOrders() {
    if (!token) { document.getElementById('orders').innerHTML = '<li class="empty">Log in to see your orders.</li>'; return; }
    const data = await api('/api/orders');
    if (guard(data)) return;
    document.getElementById('orders').innerHTML = (data.orders || []).map(o => `
      <li>Order #${o.id} — total $${o.total.toFixed(2)} — ${o.status}
        <button onclick="advance(${o.id})">Advance</button></li>`).join('') || '<li class="empty">No orders yet.</li>';
  }
  async function addToCart(id) {
    if (!token) { alert('Log in first'); return; }
    const data = await api('/api/cart', { method: 'POST', body: JSON.stringify({ item_id: id, qty: 1 }) });
    if (guard(data)) return;
    loadCart();
  }
  async function placeOrder() {
    const addr = (document.getElementById('addr') || {}).value || '';
    const last4 = (document.getElementById('card4') || {}).value || '4242';
    await api('/api/orders', { method: 'POST', body: JSON.stringify({ address: addr, payment: { method: 'card', last4: last4 } }) });
    loadCart(); loadOrders();
  }
  async function advance(id) {
    await api('/api/orders/' + id + '/advance', { method: 'POST' });
    loadOrders();
  }
  loadItems(true); loadAuth(); loadCart(); loadOrders();
</script>
</body>
</html>
"""

_FULLSTACK_FRONTEND_TASKS = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>%NAME%</title>
<style>
  :root { --bg: #f4f4f9; --fg: #22223b; --card: #ffffff; --accent: #6c63ff; --border: #ddd; }
  [data-theme="dark"] { --bg: #16161d; --fg: #e8e8f0; --card: #23232e; --accent: #8f8bff; --border: #33334a; }
  body { margin: 0; font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--fg); }
  header { background: var(--accent); color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
  main { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; margin-bottom: .5rem; }
  button { background: var(--accent); color: #fff; border: 0; padding: .5rem 1rem; border-radius: 6px; cursor: pointer; }
  input { padding: .5rem; border-radius: 6px; border: 1px solid var(--border); }
  .empty { opacity: .6; font-style: italic; }
  .done { text-decoration: line-through; opacity: .6; }
  #authBar { display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
  #authBar input { width: auto; }
  .badge { background: rgba(255,255,255,.2); padding: .25rem .6rem; border-radius: 999px; }
</style>
</head>
<body>
<header>
  <h1>%TITLE%</h1>
  <div id="authBar">
    <input id="authUser" placeholder="username" />
    <input id="authPass" type="password" placeholder="password" />
    <button onclick="auth('login')">Login</button>
    <button onclick="auth('register')">Register</button>
    <button onclick="logout()" id="logoutBtn" hidden>Logout</button>
    <span id="whoami" class="badge" hidden></span>
    <button onclick="document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark'">Toggle theme</button>
  </div>
</header>
<main>
  <p>%TAGLINE%</p>
  <div>
    <input id="newTitle" placeholder="%INPUT_PLACEHOLDER%" />
    <button onclick="addItem()">Add</button>
  </div>
  <input id="search" placeholder="Search..." oninput="load(true)" />
  <h2>%CART_LABEL%</h2>
  <div id="list"></div>
  <button id="moreBtn" hidden onclick="loadMore()">Load more</button>
</main>
<script>
  const API = '%API_BASE%';
  const KEY = 'aashu_token_' + '%COLLECTION%';
  let token = localStorage.getItem(KEY) || '';
  let offset = 0, total = 0;
  function headers(json) {
    const h = json ? {'Content-Type': 'application/json'} : {};
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
  }
  async function api(path, options) {
    options = options || {};
    options.headers = Object.assign(headers(options.body), options.headers || {});
    const res = await fetch(API + path, options);
    return res.json();
  }
  function guard(data) {
    if (data && data.error) { alert(data.error); return true; }
    return false;
  }
  async function auth(mode) {
    const username = document.getElementById('authUser').value.trim();
    const password = document.getElementById('authPass').value;
    if (!username || !password) { alert('Enter a username and password'); return; }
    const data = await api('/api/auth/' + mode, { method: 'POST', body: JSON.stringify({ username, password }) });
    if (guard(data)) return;
    token = data.token;
    localStorage.setItem(KEY, token);
    loadAuth(); load(true);
  }
  async function logout() {
    await api('/api/auth/logout', { method: 'POST' });
    token = '';
    localStorage.removeItem(KEY);
    loadAuth(); load(true);
  }
  async function loadAuth() {
    const whoami = document.getElementById('whoami');
    if (!token) { whoami.hidden = true; document.getElementById('logoutBtn').hidden = true; return; }
    const data = await api('/api/auth/me');
    if (data && data.user) {
      whoami.textContent = 'Signed in as ' + data.user;
      whoami.hidden = false;
      document.getElementById('logoutBtn').hidden = false;
    }
  }
  async function load(reset) {
    if (!token) { document.getElementById('list').innerHTML = '<div class="empty">Log in to see your %CART_LABEL%.</div>'; return; }
    if (reset) offset = 0;
    const q = (document.getElementById('search') || {}).value || '';
    const data = await api('/api/%COLLECTION%?q=' + encodeURIComponent(q) + '&limit=8&offset=' + offset);
    if (guard(data)) return;
    total = data.total || 0;
    const items = data.%COLLECTION% || [];
    const list = document.getElementById('list');
    if (reset) list.innerHTML = '';
    list.innerHTML += items.map(i => `
      <div class="card ${i.done ? 'done' : ''}">
        <strong>${i.title}</strong>
        <span>${i.priority ? '· ' + i.priority : ''}</span>
        <button onclick="toggle(${i.id})">${i.done ? 'Undo' : 'Done'}</button>
        <button onclick="remove(${i.id})">Delete</button>
      </div>`).join('') || '<div class="empty">Nothing here yet.</div>';
    document.getElementById('moreBtn').hidden = (offset + items.length) >= total;
  }
  async function loadMore() { offset += 8; load(false); }
  async function addItem() {
    if (!token) { alert('Log in first'); return; }
    const val = document.getElementById('newTitle').value.trim();
    if (!val) return;
    const data = await api('/api/%COLLECTION%', { method: 'POST', body: JSON.stringify({ title: val, priority: 'medium' }) });
    if (guard(data)) return;
    document.getElementById('newTitle').value = '';
    load(true);
  }
  async function toggle(id) { await api('/api/%COLLECTION%/' + id + '/toggle', { method: 'POST' }); load(false); }
  async function remove(id) { await api('/api/%COLLECTION%/' + id, { method: 'DELETE' }); load(true); }
  loadAuth(); load(true);
</script>
</body>
</html>
"""

_FULLSTACK_FRONTEND_COLLECTION = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>%NAME%</title>
<style>
  :root { --bg: #f4f4f9; --fg: #22223b; --card: #ffffff; --accent: #6c63ff; --border: #ddd; }
  [data-theme="dark"] { --bg: #16161d; --fg: #e8e8f0; --card: #23232e; --accent: #8f8bff; --border: #33334a; }
  body { margin: 0; font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--fg); }
  header { background: var(--accent); color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
  main { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; margin-bottom: .5rem; }
  button { background: var(--accent); color: #fff; border: 0; padding: .5rem 1rem; border-radius: 6px; cursor: pointer; }
  input, textarea { padding: .5rem; border-radius: 6px; border: 1px solid var(--border); font: inherit; }
  textarea { width: 100%; min-height: 4rem; box-sizing: border-box; }
  .empty { opacity: .6; font-style: italic; }
  small { opacity: .6; }
  #authBar { display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
  #authBar input { width: auto; }
  .badge { background: rgba(255,255,255,.2); padding: .25rem .6rem; border-radius: 999px; }
</style>
</head>
<body>
<header>
  <h1>%TITLE%</h1>
  <div id="authBar">
    <input id="authUser" placeholder="username" />
    <input id="authPass" type="password" placeholder="password" />
    <button onclick="auth('login')">Login</button>
    <button onclick="auth('register')">Register</button>
    <button onclick="logout()" id="logoutBtn" hidden>Logout</button>
    <span id="whoami" class="badge" hidden></span>
    <button onclick="document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark'">Toggle theme</button>
  </div>
</header>
<main>
  <p>%TAGLINE%</p>
  <div>
    <input id="newTitle" placeholder="%INPUT_PLACEHOLDER%" />
    <textarea id="newBody" placeholder="%BODY_PLACEHOLDER%"></textarea>
    <button onclick="addItem()">Add</button>
  </div>
  <input id="search" placeholder="Search..." oninput="load(true)" />
  <h2>%CART_LABEL%</h2>
  <div id="list"></div>
  <button id="moreBtn" hidden onclick="loadMore()">Load more</button>
</main>
<script>
  const API = '%API_BASE%';
  const KEY = 'aashu_token_' + '%COLLECTION%';
  const publicRead = %PUBLIC_READ%;
  let token = localStorage.getItem(KEY) || '';
  let offset = 0, total = 0;
  function headers(json) {
    const h = json ? {'Content-Type': 'application/json'} : {};
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
  }
  async function api(path, options) {
    options = options || {};
    options.headers = Object.assign(headers(options.body), options.headers || {});
    const res = await fetch(API + path, options);
    return res.json();
  }
  function guard(data) {
    if (data && data.error) { alert(data.error); return true; }
    return false;
  }
  async function auth(mode) {
    const username = document.getElementById('authUser').value.trim();
    const password = document.getElementById('authPass').value;
    if (!username || !password) { alert('Enter a username and password'); return; }
    const data = await api('/api/auth/' + mode, { method: 'POST', body: JSON.stringify({ username, password }) });
    if (guard(data)) return;
    token = data.token;
    localStorage.setItem(KEY, token);
    loadAuth(); load(true);
  }
  async function logout() {
    await api('/api/auth/logout', { method: 'POST' });
    token = '';
    localStorage.removeItem(KEY);
    loadAuth(); load(true);
  }
  async function loadAuth() {
    const whoami = document.getElementById('whoami');
    if (!token) { whoami.hidden = true; document.getElementById('logoutBtn').hidden = true; return; }
    const data = await api('/api/auth/me');
    if (data && data.user) {
      whoami.textContent = 'Signed in as ' + data.user;
      whoami.hidden = false;
      document.getElementById('logoutBtn').hidden = false;
    }
  }
  async function load(reset) {
    if (!publicRead && !token) { document.getElementById('list').innerHTML = '<div class="empty">Log in to see your %CART_LABEL%.</div>'; return; }
    if (reset) offset = 0;
    const q = (document.getElementById('search') || {}).value || '';
    const data = await api('/api/%COLLECTION%?q=' + encodeURIComponent(q) + '&limit=8&offset=' + offset);
    if (guard(data)) return;
    total = data.total || 0;
    const items = data.%COLLECTION% || [];
    const list = document.getElementById('list');
    if (reset) list.innerHTML = '';
    list.innerHTML += items.map(i => `
      <div class="card">
        <strong>${i.title}</strong>
        <div>${i.body || ''}</div>
        <small>by ${i.user} · ${i.created_at || ''}</small>
        <button onclick="remove(${i.id})">Delete</button>
      </div>`).join('') || '<div class="empty">Nothing here yet.</div>';
    document.getElementById('moreBtn').hidden = (offset + items.length) >= total;
  }
  async function loadMore() { offset += 8; load(false); }
  async function addItem() {
    if (!token) { alert('Log in first'); return; }
    const title = document.getElementById('newTitle').value.trim();
    const body = document.getElementById('newBody').value.trim();
    if (!title) { alert('Title is required'); return; }
    const data = await api('/api/%COLLECTION%', { method: 'POST', body: JSON.stringify({ title, body }) });
    if (guard(data)) return;
    document.getElementById('newTitle').value = '';
    document.getElementById('newBody').value = '';
    load(true);
  }
  async function remove(id) {
    if (!token) { alert('Log in first'); return; }
    const data = await api('/api/%COLLECTION%/' + id, { method: 'DELETE' });
    if (guard(data)) return;
    load(true);
  }
  loadAuth(); load(true);
</script>
</body>
</html>
"""

_FULLSTACK_FRONTEND_CHAT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>%NAME%</title>
<style>
  :root { --bg: #f4f4f9; --fg: #22223b; --card: #ffffff; --accent: #6c63ff; --border: #ddd; }
  [data-theme="dark"] { --bg: #16161d; --fg: #e8e8f0; --card: #23232e; --accent: #8f8bff; --border: #33334a; }
  body { margin: 0; font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--fg); }
  header { background: var(--accent); color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
  main { max-width: 760px; margin: 2rem auto; padding: 0 1rem; }
  #list { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; height: 50vh; overflow-y: auto; margin-bottom: .5rem; }
  .msg { padding: .4rem .8rem; margin-bottom: .5rem; background: var(--bg); border-radius: 8px; }
  .msg strong { color: var(--accent); }
  button { background: var(--accent); color: #fff; border: 0; padding: .5rem 1rem; border-radius: 6px; cursor: pointer; }
  input { padding: .5rem; border-radius: 6px; border: 1px solid var(--border); }
  .empty { opacity: .6; font-style: italic; }
  #authBar { display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
  #authBar input { width: auto; }
  .badge { background: rgba(255,255,255,.2); padding: .25rem .6rem; border-radius: 999px; }
</style>
</head>
<body>
<header>
  <h1>%TITLE%</h1>
  <div id="authBar">
    <input id="authUser" placeholder="username" />
    <input id="authPass" type="password" placeholder="password" />
    <button onclick="auth('login')">Login</button>
    <button onclick="auth('register')">Register</button>
    <button onclick="logout()" id="logoutBtn" hidden>Logout</button>
    <span id="whoami" class="badge" hidden></span>
    <button onclick="document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark'">Toggle theme</button>
  </div>
</header>
<main>
  <p>%TAGLINE%</p>
  <div id="list"><div class="empty">No messages yet.</div></div>
  <div>
    <input id="newText" placeholder="%INPUT_PLACEHOLDER%" onkeydown="if(event.key==='Enter')send()" />
    <button onclick="send()">Send</button>
  </div>
</main>
<script>
  const API = '%API_BASE%';
  const KEY = 'aashu_token_' + '%COLLECTION%';
  let token = localStorage.getItem(KEY) || '';
  function headers(json) {
    const h = json ? {'Content-Type': 'application/json'} : {};
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
  }
  async function api(path, options) {
    options = options || {};
    options.headers = Object.assign(headers(options.body), options.headers || {});
    const res = await fetch(API + path, options);
    return res.json();
  }
  function guard(data) {
    if (data && data.error) { alert(data.error); return true; }
    return false;
  }
  function escapeHtml(s) {
    return (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }
  function appendMessage(m) {
    const list = document.getElementById('list');
    const div = document.createElement('div');
    div.className = 'msg';
    div.innerHTML = `<strong>${escapeHtml(m.user)}</strong> ${escapeHtml(m.text)} <small>${escapeHtml(m.created_at || '')}</small>`;
    list.appendChild(div);
    list.scrollTop = list.scrollHeight;
  }
  async function auth(mode) {
    const username = document.getElementById('authUser').value.trim();
    const password = document.getElementById('authPass').value;
    if (!username || !password) { alert('Enter a username and password'); return; }
    const data = await api('/api/auth/' + mode, { method: 'POST', body: JSON.stringify({ username, password }) });
    if (guard(data)) return;
    token = data.token;
    localStorage.setItem(KEY, token);
    loadAuth();
  }
  async function logout() {
    await api('/api/auth/logout', { method: 'POST' });
    token = '';
    localStorage.removeItem(KEY);
    loadAuth();
  }
  async function loadAuth() {
    const whoami = document.getElementById('whoami');
    if (!token) { whoami.hidden = true; document.getElementById('logoutBtn').hidden = true; return; }
    const data = await api('/api/auth/me');
    if (data && data.user) {
      whoami.textContent = 'Signed in as ' + data.user;
      whoami.hidden = false;
      document.getElementById('logoutBtn').hidden = false;
    }
  }
  async function load() {
    const data = await api('/api/messages?limit=50');
    const list = document.getElementById('list');
    list.innerHTML = '';
    (data.messages || []).slice().reverse().forEach(appendMessage);
    if (!data.messages || !data.messages.length) list.innerHTML = '<div class="empty">No messages yet.</div>';
  }
  async function send() {
    if (!token) { alert('Log in first'); return; }
    const text = document.getElementById('newText').value.trim();
    if (!text) return;
    const data = await api('/api/messages', { method: 'POST', body: JSON.stringify({ text }) });
    if (guard(data)) return;
    document.getElementById('newText').value = '';
  }
  const source = new EventSource(API + '/api/messages/stream');
  source.onmessage = e => { try { appendMessage(JSON.parse(e.data)); } catch (_) {} };
  load(); loadAuth();
</script>
</body>
</html>
"""


_NODE_COMMON = '''// Auto-generated by the Aashu Virtual Brain (deterministic, no LLM).
// SQLite (better-sqlite3, sync) by default; PostgreSQL when DATABASE_URL is
// set (pg Pool). Scrypt password hashing, DB-backed sessions.
const crypto = require('crypto');
const path = require('path');
const fs = require('fs');

const isPg = !!process.env.DATABASE_URL;
const PORT = process.env.PORT || 3000;

let pool, sdb;
if (isPg) {
  const { Pool } = require('pg');
  pool = new Pool({ connectionString: process.env.DATABASE_URL });
} else {
  const Database = require('better-sqlite3');
  sdb = new Database(process.env.DATABASE_PATH || path.join(__dirname, 'app.db'));
  sdb.pragma('journal_mode = WAL');
}

function pgq(sql) {
  if (!isPg) return sql;
  let i = 0;
  return sql.replace(/\\?/g, () => `$${++i}`);
}

const db = {
  all: async (sql, args = []) => {
    if (isPg) return (await pool.query(pgq(sql), args)).rows;
    return sdb.prepare(sql).all(...args);
  },
  one: async (sql, args = []) => {
    if (isPg) return (await pool.query(pgq(sql), args)).rows[0] || null;
    return sdb.prepare(sql).get(...args) || null;
  },
  run: async (sql, args = []) => {
    if (isPg) return (await pool.query(pgq(sql), args)).rowCount;
    return sdb.prepare(sql).run(...args).changes;
  },
  insert: async (sql, args = []) => {
    if (isPg) {
      const r = await pool.query(pgq(sql) + ' RETURNING id', args);
      return r.rows[0] ? r.rows[0].id : null;
    }
    return sdb.prepare(sql).run(...args).lastInsertRowid;
  },
};

function hashPassword(password, salt) {
  return crypto.scryptSync(password, salt, 64).toString('hex');
}

async function newSession(username) {
  const token = crypto.randomBytes(16).toString('hex');
  await db.run('INSERT INTO sessions (token, username) VALUES (?, ?)', [token, username]);
  return token;
}

async function currentUser(req) {
  const h = req.headers.authorization || '';
  if (!h.startsWith('Bearer ')) return null;
  const row = await db.one('SELECT username FROM sessions WHERE token = ?', [h.slice(7).trim()]);
  return row ? row.username : null;
}

function queryArgs(req) {
  const limit = Math.min(Math.max(parseInt(req.query.limit, 10) || 50, 1), 200);
  const offset = Math.max(parseInt(req.query.offset, 10) || 0, 0);
  return [String(req.query.q || '').trim(), limit, offset];
}

function likePattern(q) {
  return '%' + q.replace(/\\\\/g, '\\\\\\\\').replace(/%/g, '\\\\%').replace(/_/g, '\\\\_') + '%';
}

function uniqueViolation(e) {
  return isPg ? e.code === '23505' : /unique/i.test(e.message);
}

async function initDb() {
  if (isPg) {
    await pool.query(pgq({{SCHEMA}}));
    {{SEED_SQL_NODE_PG}}
  } else {
    sdb.exec({{SCHEMA}});
    {{SEED_SQL_NODE}}
  }
}

initDb().catch((err) => { console.error(err); process.exit(1); });
'''

_EXPRESS_HEAD = _NODE_COMMON + '''const express = require('express');

const app = express();
app.use(express.json());

app.use((req, res, next) => {
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.set('Access-Control-Allow-Methods', 'GET, POST, DELETE, PATCH, OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

app.get('/healthz', async (req, res) => {
  await db.one('SELECT 1 AS ok');
  res.json({ status: 'ok' });
});

app.get('/api/auth/me', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  res.json({ user });
});

app.post('/api/auth/register', async (req, res) => {
  const username = String((req.body && req.body.username) || '').trim();
  const password = String((req.body && req.body.password) || '');
  if (username.length < 3 || password.length < 4) {
    return res.status(400).json({ error: 'Username (>=3 chars) and password (>=4 chars) required' });
  }
  const salt = crypto.randomBytes(8).toString('hex');
  try {
    await db.run('INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)', [username, salt, hashPassword(password, salt)]);
  } catch (e) {
    if (uniqueViolation(e)) return res.status(409).json({ error: 'Username already taken' });
    throw e;
  }
  const token = await newSession(username);
  res.status(201).json({ token, user: username });
});

app.post('/api/auth/login', async (req, res) => {
  const username = String((req.body && req.body.username) || '').trim();
  const password = String((req.body && req.body.password) || '');
  const row = await db.one('SELECT salt, password_hash FROM users WHERE username = ?', [username]);
  if (!row || row.password_hash !== hashPassword(password, row.salt)) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  const token = await newSession(username);
  res.json({ token, user: username });
});

app.post('/api/auth/logout', async (req, res) => {
  const h = req.headers.authorization || '';
  if (h.startsWith('Bearer ')) await db.run('DELETE FROM sessions WHERE token = ?', [h.slice(7).trim()]);
  res.json({ ok: true });
});

{{ROUTES}}

const FE_ROOT = fs.existsSync(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'))
  ? path.join(__dirname, '..', 'frontend', 'dist')
  : path.join(__dirname, '..', 'frontend');
app.use(express.static(FE_ROOT));
app.use((req, res, next) => {
  if (req.method !== 'GET') return res.status(404).json({ error: 'Not found' });
  if (req.path.startsWith('/api/')) return res.status(404).json({ error: 'Not found' });
  res.sendFile(path.join(FE_ROOT, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`{{TITLE}} listening on http://0.0.0.0:${PORT}`);
});
'''

_FASTIFY_HEAD = _NODE_COMMON + '''const fastify = require('fastify');

const app = fastify();

app.addHook('onRequest', (req, reply, done) => {
  reply.header('Access-Control-Allow-Origin', '*');
  reply.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  reply.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, PATCH, OPTIONS');
  if (req.method === 'OPTIONS') return reply.code(204).send();
  done();
});

app.get('/healthz', async () => {
  await db.one('SELECT 1 AS ok');
  return { status: 'ok' };
});

app.get('/api/auth/me', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  return { user };
});

app.post('/api/auth/register', async (req, reply) => {
  const username = String((req.body && req.body.username) || '').trim();
  const password = String((req.body && req.body.password) || '');
  if (username.length < 3 || password.length < 4) {
    return reply.code(400).send({ error: 'Username (>=3 chars) and password (>=4 chars) required' });
  }
  const salt = crypto.randomBytes(8).toString('hex');
  try {
    await db.run('INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)', [username, salt, hashPassword(password, salt)]);
  } catch (e) {
    if (uniqueViolation(e)) return reply.code(409).send({ error: 'Username already taken' });
    throw e;
  }
  const token = await newSession(username);
  return reply.code(201).send({ token, user: username });
});

app.post('/api/auth/login', async (req, reply) => {
  const username = String((req.body && req.body.username) || '').trim();
  const password = String((req.body && req.body.password) || '');
  const row = await db.one('SELECT salt, password_hash FROM users WHERE username = ?', [username]);
  if (!row || row.password_hash !== hashPassword(password, row.salt)) {
    return reply.code(401).send({ error: 'Invalid credentials' });
  }
  const token = await newSession(username);
  return { token, user: username };
});

app.post('/api/auth/logout', async (req, reply) => {
  const h = req.headers.authorization || '';
  if (h.startsWith('Bearer ')) await db.run('DELETE FROM sessions WHERE token = ?', [h.slice(7).trim()]);
  return { ok: true };
});

{{ROUTES}}

const FE_ROOT = fs.existsSync(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'))
  ? path.join(__dirname, '..', 'frontend', 'dist')
  : path.join(__dirname, '..', 'frontend');
app.register(require('@fastify/static'), { root: FE_ROOT, wildcard: false });
app.setNotFoundHandler((req, reply) => {
  if (req.method === 'GET' && !req.url.startsWith('/api/')) {
    return reply.sendFile('index.html');
  }
  return reply.code(404).send({ error: 'Not found' });
});

app.listen({ port: PORT, host: '0.0.0.0' }).then(() => {
  console.log(`{{TITLE}} listening on http://0.0.0.0:${PORT}`);
});
'''

_EXPRESS_ROUTES_CART = '''
const CATALOG_TABLE = '{{TABLE}}';

function orderDict(o) {
  return {
    id: o.id, user: o.username, items: JSON.parse(o.items || '{}'),
    total: o.total, address: o.address, status: o.status, created_at: o.created_at,
    payment: { method: o.payment_method, last4: o.payment_last4, amount: o.total, status: o.payment_status },
  };
}

app.get('/api/{{COLLECTION}}', async (req, res) => {
  const [q, limit, offset] = queryArgs(req);
  let where = '';
  const args = [];
  if (q) { where = "WHERE name LIKE ? ESCAPE '\\\\'"; args.push(likePattern(q)); }
  const total = await db.one('SELECT COUNT(*) AS n FROM ' + CATALOG_TABLE + ' ' + where, args);
  const items = await db.all('SELECT id, name, category, price, rating FROM ' + CATALOG_TABLE + ' ' + where + ' ORDER BY id LIMIT ? OFFSET ?', args.concat([limit, offset]));
  res.json({ items, total: total.n, limit, offset });
});

app.get('/api/cart', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const rows = await db.all('SELECT item_id, qty FROM cart_items WHERE username = ?', [user]);
  const items = {};
  rows.forEach((r) => { items[String(r.item_id)] = r.qty; });
  res.json({ items });
});

app.post('/api/cart', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const itemId = parseInt(req.body && req.body.item_id, 10);
  const qty = parseInt(req.body && req.body.qty, 10) || 1;
  if (!itemId) return res.status(400).json({ error: 'Invalid item' });
  const item = await db.one('SELECT id FROM ' + CATALOG_TABLE + ' WHERE id = ?', [itemId]);
  if (!item) return res.status(404).json({ error: 'Item not found' });
  await db.run(
    'INSERT INTO cart_items (username, item_id, qty) VALUES (?, ?, ?) ON CONFLICT(username, item_id) DO UPDATE SET qty = qty + excluded.qty',
    [user, itemId, qty]
  );
  const rows = await db.all('SELECT item_id, qty FROM cart_items WHERE username = ?', [user]);
  const items = {};
  rows.forEach((r) => { items[String(r.item_id)] = r.qty; });
  res.json({ cart: items });
});

app.post('/api/orders', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const body = req.body || {};
  const payment = body.payment || {};
  const cart = await db.all('SELECT item_id, qty FROM cart_items WHERE username = ?', [user]);
  if (!cart.length) return res.status(400).json({ error: 'Cart is empty' });
  const ids = cart.map((c) => c.item_id).join(',');
  const byId = {};
  (await db.all('SELECT id, price FROM ' + CATALOG_TABLE + ' WHERE id IN (' + ids + ')')).forEach((i) => { byId[i.id] = i; });
  const orderItems = {};
  cart.forEach((c) => { orderItems[String(c.item_id)] = c.qty; });
  let total = 0;
  cart.forEach((c) => { total += byId[c.item_id].price * c.qty; });
  total = Math.round(total * 100) / 100;
  const id = await db.insert(
    'INSERT INTO orders (username, address, total, payment_method, payment_last4, items) VALUES (?, ?, ?, ?, ?, ?)',
    [user, String(body.address || '') || 'Pickup', total, String(payment.method || 'card'), String(payment.last4 || ''), JSON.stringify(orderItems)]
  );
  await db.run('DELETE FROM cart_items WHERE username = ?', [user]);
  const order = await db.one('SELECT * FROM orders WHERE id = ?', [id]);
  res.status(201).json({ order: orderDict(order) });
});

app.get('/api/orders', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const rows = await db.all('SELECT * FROM orders WHERE username = ? ORDER BY id', [user]);
  res.json({ orders: rows.map(orderDict) });
});

app.post('/api/orders/:id/advance', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const orderId = parseInt(req.params.id, 10);
  const statuses = ['placed', 'accepted', 'delivered'];
  const row = await db.one('SELECT * FROM orders WHERE id = ? AND username = ?', [orderId, user]);
  if (!row) return res.status(404).json({ error: 'Order not found' });
  const idx = statuses.indexOf(row.status) >= 0 ? statuses.indexOf(row.status) : 0;
  if (idx < statuses.length - 1) await db.run('UPDATE orders SET status = ? WHERE id = ?', [statuses[idx + 1], orderId]);
  const order = await db.one('SELECT * FROM orders WHERE id = ?', [orderId]);
  res.json({ order: orderDict(order) });
});
'''

_FASTIFY_ROUTES_CART = '''
const CATALOG_TABLE = '{{TABLE}}';

function orderDict(o) {
  return {
    id: o.id, user: o.username, items: JSON.parse(o.items || '{}'),
    total: o.total, address: o.address, status: o.status, created_at: o.created_at,
    payment: { method: o.payment_method, last4: o.payment_last4, amount: o.total, status: o.payment_status },
  };
}

app.get('/api/{{COLLECTION}}', async (req, reply) => {
  const [q, limit, offset] = queryArgs(req);
  let where = '';
  const args = [];
  if (q) { where = "WHERE name LIKE ? ESCAPE '\\\\'"; args.push(likePattern(q)); }
  const total = await db.one('SELECT COUNT(*) AS n FROM ' + CATALOG_TABLE + ' ' + where, args);
  const items = await db.all('SELECT id, name, category, price, rating FROM ' + CATALOG_TABLE + ' ' + where + ' ORDER BY id LIMIT ? OFFSET ?', args.concat([limit, offset]));
  return { items, total: total.n, limit, offset };
});

app.get('/api/cart', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const rows = await db.all('SELECT item_id, qty FROM cart_items WHERE username = ?', [user]);
  const items = {};
  rows.forEach((r) => { items[String(r.item_id)] = r.qty; });
  return { items };
});

app.post('/api/cart', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const itemId = parseInt(req.body && req.body.item_id, 10);
  const qty = parseInt(req.body && req.body.qty, 10) || 1;
  if (!itemId) return reply.code(400).send({ error: 'Invalid item' });
  const item = await db.one('SELECT id FROM ' + CATALOG_TABLE + ' WHERE id = ?', [itemId]);
  if (!item) return reply.code(404).send({ error: 'Item not found' });
  await db.run(
    'INSERT INTO cart_items (username, item_id, qty) VALUES (?, ?, ?) ON CONFLICT(username, item_id) DO UPDATE SET qty = qty + excluded.qty',
    [user, itemId, qty]
  );
  const rows = await db.all('SELECT item_id, qty FROM cart_items WHERE username = ?', [user]);
  const items = {};
  rows.forEach((r) => { items[String(r.item_id)] = r.qty; });
  return { cart: items };
});

app.post('/api/orders', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const body = req.body || {};
  const payment = body.payment || {};
  const cart = await db.all('SELECT item_id, qty FROM cart_items WHERE username = ?', [user]);
  if (!cart.length) return reply.code(400).send({ error: 'Cart is empty' });
  const ids = cart.map((c) => c.item_id).join(',');
  const byId = {};
  (await db.all('SELECT id, price FROM ' + CATALOG_TABLE + ' WHERE id IN (' + ids + ')')).forEach((i) => { byId[i.id] = i; });
  const orderItems = {};
  cart.forEach((c) => { orderItems[String(c.item_id)] = c.qty; });
  let total = 0;
  cart.forEach((c) => { total += byId[c.item_id].price * c.qty; });
  total = Math.round(total * 100) / 100;
  const id = await db.insert(
    'INSERT INTO orders (username, address, total, payment_method, payment_last4, items) VALUES (?, ?, ?, ?, ?, ?)',
    [user, String(body.address || '') || 'Pickup', total, String(payment.method || 'card'), String(payment.last4 || ''), JSON.stringify(orderItems)]
  );
  await db.run('DELETE FROM cart_items WHERE username = ?', [user]);
  const order = await db.one('SELECT * FROM orders WHERE id = ?', [id]);
  return reply.code(201).send({ order: orderDict(order) });
});

app.get('/api/orders', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const rows = await db.all('SELECT * FROM orders WHERE username = ? ORDER BY id', [user]);
  return { orders: rows.map(orderDict) };
});

app.post('/api/orders/:id/advance', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const orderId = parseInt(req.params.id, 10);
  const statuses = ['placed', 'accepted', 'delivered'];
  const row = await db.one('SELECT * FROM orders WHERE id = ? AND username = ?', [orderId, user]);
  if (!row) return reply.code(404).send({ error: 'Order not found' });
  const idx = statuses.indexOf(row.status) >= 0 ? statuses.indexOf(row.status) : 0;
  if (idx < statuses.length - 1) await db.run('UPDATE orders SET status = ? WHERE id = ?', [statuses[idx + 1], orderId]);
  const order = await db.one('SELECT * FROM orders WHERE id = ?', [orderId]);
  return { order: orderDict(order) };
});
'''

_EXPRESS_ROUTES_TASKS = '''
const TASK_FIELDS = 'id, username AS user, title, done, priority, created_at';

app.get('/api/tasks', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const [q, limit, offset] = queryArgs(req);
  let where = 'username = ?';
  const args = [user];
  if (q) { where += " AND title LIKE ? ESCAPE '\\\\'"; args.push(likePattern(q)); }
  const total = await db.one('SELECT COUNT(*) AS n FROM tasks WHERE ' + where, args);
  const tasks = await db.all('SELECT ' + TASK_FIELDS + ' FROM tasks WHERE ' + where + ' ORDER BY id DESC LIMIT ? OFFSET ?', args.concat([limit, offset]));
  res.json({ tasks, total: total.n, limit, offset });
});

app.post('/api/tasks', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const title = String((req.body && req.body.title) || '').trim();
  if (!title) return res.status(400).json({ error: 'Title is required' });
  const id = await db.insert('INSERT INTO tasks (username, title, priority) VALUES (?, ?, ?)', [user, title, String((req.body && req.body.priority) || 'medium')]);
  const task = await db.one('SELECT ' + TASK_FIELDS + ' FROM tasks WHERE id = ?', [id]);
  res.status(201).json({ task });
});

app.post('/api/tasks/:id/toggle', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const taskId = parseInt(req.params.id, 10);
  const row = await db.one('SELECT id FROM tasks WHERE id = ? AND username = ?', [taskId, user]);
  if (!row) return res.status(404).json({ error: 'Task not found' });
  await db.run('UPDATE tasks SET done = 1 - done WHERE id = ?', [taskId]);
  const task = await db.one('SELECT ' + TASK_FIELDS + ' FROM tasks WHERE id = ?', [taskId]);
  res.json({ task });
});

app.delete('/api/tasks/:id', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const taskId = parseInt(req.params.id, 10);
  const changes = await db.run('DELETE FROM tasks WHERE id = ? AND username = ?', [taskId, user]);
  res.json({ deleted: changes > 0 });
});
'''

_FASTIFY_ROUTES_TASKS = '''
const TASK_FIELDS = 'id, username AS user, title, done, priority, created_at';

app.get('/api/tasks', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const [q, limit, offset] = queryArgs(req);
  let where = 'username = ?';
  const args = [user];
  if (q) { where += " AND title LIKE ? ESCAPE '\\\\'"; args.push(likePattern(q)); }
  const total = await db.one('SELECT COUNT(*) AS n FROM tasks WHERE ' + where, args);
  const tasks = await db.all('SELECT ' + TASK_FIELDS + ' FROM tasks WHERE ' + where + ' ORDER BY id DESC LIMIT ? OFFSET ?', args.concat([limit, offset]));
  return { tasks, total: total.n, limit, offset };
});

app.post('/api/tasks', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const title = String((req.body && req.body.title) || '').trim();
  if (!title) return reply.code(400).send({ error: 'Title is required' });
  const id = await db.insert('INSERT INTO tasks (username, title, priority) VALUES (?, ?, ?)', [user, title, String((req.body && req.body.priority) || 'medium')]);
  const task = await db.one('SELECT ' + TASK_FIELDS + ' FROM tasks WHERE id = ?', [id]);
  return reply.code(201).send({ task });
});

app.post('/api/tasks/:id/toggle', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const taskId = parseInt(req.params.id, 10);
  const row = await db.one('SELECT id FROM tasks WHERE id = ? AND username = ?', [taskId, user]);
  if (!row) return reply.code(404).send({ error: 'Task not found' });
  await db.run('UPDATE tasks SET done = 1 - done WHERE id = ?', [taskId]);
  const task = await db.one('SELECT ' + TASK_FIELDS + ' FROM tasks WHERE id = ?', [taskId]);
  return { task };
});

app.delete('/api/tasks/:id', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const taskId = parseInt(req.params.id, 10);
  const changes = await db.run('DELETE FROM tasks WHERE id = ? AND username = ?', [taskId, user]);
  return { deleted: changes > 0 };
});
'''

_EXPRESS_ROUTES_MESSAGES = '''
const MSG_FIELDS = 'id, username AS user, text, created_at';
const clients = new Set();

app.get('/api/messages', async (req, res) => {
  const [q, limit, offset] = queryArgs(req);
  let where = '';
  const args = [];
  if (q) { where = "WHERE text LIKE ? ESCAPE '\\\\'"; args.push(likePattern(q)); }
  const total = await db.one('SELECT COUNT(*) AS n FROM messages ' + where, args);
  const messages = await db.all('SELECT ' + MSG_FIELDS + ' FROM messages ' + where + ' ORDER BY id DESC LIMIT ? OFFSET ?', args.concat([limit, offset]));
  res.json({ messages, total: total.n, limit, offset });
});

app.get('/api/messages/stream', async (req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no' });
  res.write('data: {"hello":true}\\n\\n');
  clients.add(res);
  req.on('close', () => clients.delete(res));
});

app.post('/api/messages', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const text = String((req.body && req.body.text) || '').trim();
  if (!text) return res.status(400).json({ error: 'Message text is required' });
  const id = await db.insert('INSERT INTO messages (username, text) VALUES (?, ?)', [user, text]);
  const msg = await db.one('SELECT ' + MSG_FIELDS + ' FROM messages WHERE id = ?', [id]);
  const payload = 'data: ' + JSON.stringify(msg) + '\\n\\n';
  clients.forEach((c) => { if (!c.writableEnded) c.write(payload); });
  res.status(201).json({ message: msg });
});
'''

_FASTIFY_ROUTES_MESSAGES = '''
const MSG_FIELDS = 'id, username AS user, text, created_at';
const clients = new Set();

app.get('/api/messages', async (req, reply) => {
  const [q, limit, offset] = queryArgs(req);
  let where = '';
  const args = [];
  if (q) { where = "WHERE text LIKE ? ESCAPE '\\\\'"; args.push(likePattern(q)); }
  const total = await db.one('SELECT COUNT(*) AS n FROM messages ' + where, args);
  const messages = await db.all('SELECT ' + MSG_FIELDS + ' FROM messages ' + where + ' ORDER BY id DESC LIMIT ? OFFSET ?', args.concat([limit, offset]));
  return { messages, total: total.n, limit, offset };
});

app.get('/api/messages/stream', async (req, reply) => {
  reply.hijack();
  reply.raw.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no' });
  reply.raw.write('data: {"hello":true}\\n\\n');
  clients.add(reply.raw);
  req.raw.on('close', () => clients.delete(reply.raw));
});

app.post('/api/messages', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const text = String((req.body && req.body.text) || '').trim();
  if (!text) return reply.code(400).send({ error: 'Message text is required' });
  const id = await db.insert('INSERT INTO messages (username, text) VALUES (?, ?)', [user, text]);
  const msg = await db.one('SELECT ' + MSG_FIELDS + ' FROM messages WHERE id = ?', [id]);
  const payload = 'data: ' + JSON.stringify(msg) + '\\n\\n';
  clients.forEach((c) => { if (!c.writableEnded) c.write(payload); });
  return reply.code(201).send({ message: msg });
});
'''

_EXPRESS_ROUTES_COLLECTION = '''
const COLLECTION_TABLE = '{{TABLE}}';
const COLLECTION_FIELDS = 'id, username AS user, title, body, created_at';

function readGuard(user) {
  return {{PUBLIC_READ_CHECK}} ? !!user : true;
}

app.get('/api/{{COLLECTION}}', async (req, res) => {
  const user = await currentUser(req);
  if (!readGuard(user)) return res.status(401).json({ error: 'Not authenticated' });
  const [q, limit, offset] = queryArgs(req);
  let where = '';
  const args = [];
  if (q) { where = "WHERE (title LIKE ? ESCAPE '\\\\' OR body LIKE ? ESCAPE '\\\\')"; args.push(likePattern(q), likePattern(q)); }
  const total = await db.one('SELECT COUNT(*) AS n FROM ' + COLLECTION_TABLE + ' ' + where, args);
  const rows = await db.all('SELECT ' + COLLECTION_FIELDS + ' FROM ' + COLLECTION_TABLE + ' ' + where + ' ORDER BY id DESC LIMIT ? OFFSET ?', args.concat([limit, offset]));
  res.json({ '{{COLLECTION}}': rows, total: total.n, limit, offset });
});

app.post('/api/{{COLLECTION}}', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const title = String((req.body && req.body.title) || '').trim();
  if (!title) return res.status(400).json({ error: 'Title is required' });
  const body = String((req.body && req.body.body) || '').trim();
  const id = await db.insert('INSERT INTO ' + COLLECTION_TABLE + ' (username, title, body) VALUES (?, ?, ?)', [user, title, body]);
  const item = await db.one('SELECT ' + COLLECTION_FIELDS + ' FROM ' + COLLECTION_TABLE + ' WHERE id = ?', [id]);
  res.status(201).json({ item });
});

app.delete('/api/{{COLLECTION}}/:id', async (req, res) => {
  const user = await currentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  const itemId = parseInt(req.params.id, 10);
  const changes = await db.run('DELETE FROM ' + COLLECTION_TABLE + ' WHERE id = ? AND username = ?', [itemId, user]);
  res.json({ deleted: changes > 0 });
});
'''

_FASTIFY_ROUTES_COLLECTION = '''
const COLLECTION_TABLE = '{{TABLE}}';
const COLLECTION_FIELDS = 'id, username AS user, title, body, created_at';

function readGuard(user) {
  return {{PUBLIC_READ_CHECK}} ? !!user : true;
}

app.get('/api/{{COLLECTION}}', async (req, reply) => {
  const user = await currentUser(req);
  if (!readGuard(user)) return reply.code(401).send({ error: 'Not authenticated' });
  const [q, limit, offset] = queryArgs(req);
  let where = '';
  const args = [];
  if (q) { where = "WHERE (title LIKE ? ESCAPE '\\\\' OR body LIKE ? ESCAPE '\\\\')"; args.push(likePattern(q), likePattern(q)); }
  const total = await db.one('SELECT COUNT(*) AS n FROM ' + COLLECTION_TABLE + ' ' + where, args);
  const rows = await db.all('SELECT ' + COLLECTION_FIELDS + ' FROM ' + COLLECTION_TABLE + ' ' + where + ' ORDER BY id DESC LIMIT ? OFFSET ?', args.concat([limit, offset]));
  return { '{{COLLECTION}}': rows, total: total.n, limit, offset };
});

app.post('/api/{{COLLECTION}}', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const title = String((req.body && req.body.title) || '').trim();
  if (!title) return reply.code(400).send({ error: 'Title is required' });
  const body = String((req.body && req.body.body) || '').trim();
  const id = await db.insert('INSERT INTO ' + COLLECTION_TABLE + ' (username, title, body) VALUES (?, ?, ?)', [user, title, body]);
  const item = await db.one('SELECT ' + COLLECTION_FIELDS + ' FROM ' + COLLECTION_TABLE + ' WHERE id = ?', [id]);
  return reply.code(201).send({ item });
});

app.delete('/api/{{COLLECTION}}/:id', async (req, reply) => {
  const user = await currentUser(req);
  if (!user) return reply.code(401).send({ error: 'Not authenticated' });
  const itemId = parseInt(req.params.id, 10);
  const changes = await db.run('DELETE FROM ' + COLLECTION_TABLE + ' WHERE id = ? AND username = ?', [itemId, user]);
  return { deleted: changes > 0 };
});
'''


_REACT_PACKAGE_JSON = """{
  "name": "%NAME%",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0"
  }
}
"""

_REACT_VITE_CONFIG = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In dev, Vite proxies /api to the backend so the SPA talks to the same origin.
// In production the backend serves frontend/dist at the same origin.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: 'http://127.0.0.1:%API_PORT%', changeOrigin: true },
    },
  },
})
"""

_REACT_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>%TITLE%</title>
</head>
<body>
<div id="root"></div>
<script type="module" src="/src/main.jsx"></script>
</body>
</html>
"""

_REACT_MAIN = """import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
"""

_REACT_BOOTSTRAP = """
const API = import.meta.env.VITE_API_BASE || ''
const KEY = 'aashu_token_%COLLECTION%'

function api(path, { method = 'GET', body } = {}) {
  const headers = {}
  const token = localStorage.getItem(KEY) || ''
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers['Authorization'] = 'Bearer ' + token
  return fetch(API + path, { method, headers, body: body !== undefined ? JSON.stringify(body) : undefined })
    .then(async (r) => {
      const data = await r.json().catch(() => ({}))
      if (!r.ok) throw new Error(data.error || 'Request failed')
      return data
    })
}

function useAuth() {
  const [user, setUser] = useState(null)
  useEffect(() => {
    api('/api/auth/me').then((d) => { if (d && d.user) setUser(d.user) }).catch(() => {})
  }, [])
  const login = (username, password) =>
    api('/api/auth/login', { method: 'POST', body: { username, password } }).then((d) => { localStorage.setItem(KEY, d.token); setUser(d.user) })
  const register = (username, password) =>
    api('/api/auth/register', { method: 'POST', body: { username, password } }).then((d) => { localStorage.setItem(KEY, d.token); setUser(d.user) })
  const logout = () =>
    api('/api/auth/logout', { method: 'POST' }).finally(() => { localStorage.removeItem(KEY); setUser(null) })
  return { user, setUser, login, register, logout }
}

function toggleTheme() {
  const cur = document.body.dataset.theme
  document.body.dataset.theme = cur === 'dark' ? 'light' : 'dark'
}
"""

_REACT_AUTH_BAR = """
function AuthBar({ user, login, register, logout }) {
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [err, setErr] = useState('')
  const submit = (fn) => {
    fn(u, p).catch((e) => setErr(e.message))
  }
  return (
    <header>
      <h1>%TITLE%</h1>
      <div className="authbar">
        {user ? (
          <>
            <span className="badge">{user}</span>
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <>
            <input placeholder="username" value={u} onChange={(e) => setU(e.target.value)} />
            <input type="password" placeholder="password" value={p} onChange={(e) => setP(e.target.value)} />
            <button onClick={() => submit(login)}>Login</button>
            <button onClick={() => submit(register)}>Register</button>
          </>
        )}
        <button onClick={toggleTheme}>Toggle theme</button>
      </div>
    </header>
  )
}
"""

_REACT_CSS = """
<style>{`
  :root { --bg: #f4f4f9; --fg: #22223b; --card: #ffffff; --accent: #6c63ff; --border: #ddd; }
  [data-theme="dark"] { --bg: #16161d; --fg: #e8e8f0; --card: #23232e; --accent: #8f8bff; --border: #33334a; }
  body { margin: 0; font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--fg); }
  header { background: var(--accent); color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
  main { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; }
  button { background: var(--accent); color: #fff; border: 0; padding: .5rem 1rem; border-radius: 6px; cursor: pointer; margin: .25rem; }
  input { padding: .5rem; border-radius: 6px; border: 1px solid var(--border); }
  .price { color: var(--accent); font-weight: 600; }
  .empty { opacity: .6; font-style: italic; }
  .badge { background: rgba(255,255,255,.2); padding: .25rem .6rem; border-radius: 999px; }
  .authbar { display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
  .row { display: flex; justify-content: space-between; align-items: center; gap: .5rem; margin-bottom: .4rem; }
  .error { color: #e5484d; }
  ul { list-style: none; padding: 0; }
  .msg { padding: .4rem .8rem; margin-bottom: .5rem; background: var(--bg); border-radius: 8px; }
`}</style>
"""

_REACT_CART_JSX = """import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom'
%REACT_BOOTSTRAP%
%REACT_CSS%

function App() {
  const { user, setUser, login, register, logout } = useAuth()
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [q, setQ] = useState('')
  const [cart, setCart] = useState({})
  const [orders, setOrders] = useState([])
  const [error, setError] = useState('')

  useEffect(() => { loadItems() }, [])
  useEffect(() => {
    if (!user) return
    api('/api/cart').then((d) => setCart(d.items || {})).catch(() => {})
    api('/api/orders').then((d) => setOrders(d.orders || [])).catch(() => {})
  }, [user])

  const loadItems = (opts) => {
    api('/api/%COLLECTION%?q=' + encodeURIComponent(opts ? opts.q : q))
      .then((d) => { setItems(d.items || []); setTotal(d.total || 0) })
      .catch((e) => setError(e.message))
  }

  const add = (id) => {
    api('/api/cart', { method: 'POST', body: { item_id: id, qty: 1 } })
      .then((d) => { setCart(d.cart || {}) })
      .catch((e) => setError(e.message))
  }

  const placeOrder = () => {
    api('/api/orders', { method: 'POST', body: { address: 'Pickup', payment: { method: 'card' } } })
      .then((d) => {
        setOrders([d.order, ...orders])
        setCart({})
      })
      .catch((e) => setError(e.message))
  }

  const advance = (id) => {
    api('/api/orders/' + id + '/advance', { method: 'POST' })
      .then((d) => setOrders(orders.map((o) => (o.id === d.order.id ? d.order : o))))
      .catch((e) => setError(e.message))
  }

  const inCart = Object.keys(cart || {})
  const cartTotal = items.filter((i) => inCart.includes(String(i.id))).reduce((s, i) => s + i.price * (cart[String(i.id)] || 0), 0)

  return (
    <div>
      <AuthBar user={user} login={login} register={register} logout={logout} />
      <main>
        <p>%TAGLINE%</p>
        {error && <p className="error">{error}</p>}
        <h2>%ITEM_VERB%s</h2>
        <input placeholder="Search %COLLECTION%..." value={q} onChange={(e) => { setQ(e.target.value); loadItems({ q: e.target.value }) }} />
        <div className="grid">
          {items.map((i) => (
            <div className="card" key={i.id}>
              <strong>{i.name}</strong> <span className="price">${i.price.toFixed(2)}</span>
              <p>{i.category}</p>
              <button onClick={() => add(i.id)}>Add</button>
            </div>
          ))}
        </div>
        <p className="empty">{total} %ITEM_VERB%s total</p>
        <h2>%CART_LABEL% ({inCart.length})</h2>
        <p>Total: ${cartTotal.toFixed(2)}</p>
        <button onClick={placeOrder} disabled={!user || inCart.length === 0}>Place order</button>
        {!user && <p className="empty">Login to place an order.</p>}
        <h2>Orders</h2>
        <ul>
          {orders.map((o) => (
            <li key={o.id}>
              <div className="row">
                <span>Order #{o.id} — {o.status}</span>
                <span>${o.total.toFixed(2)}</span>
                <button onClick={() => advance(o.id)}>Advance</button>
              </div>
            </li>
          ))}
        </ul>
      </main>
    </div>
  )
}

export default App
"""

_REACT_TASKS_JSX = """import React, { useEffect, useState } from 'react'
%REACT_BOOTSTRAP%
%REACT_CSS%

function App() {
  const { user, login, register, logout } = useAuth()
  const [tasks, setTasks] = useState([])
  const [title, setTitle] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) return
    api('/api/tasks').then((d) => setTasks(d.tasks || [])).catch((e) => setError(e.message))
  }, [user])

  const add = () => {
    api('/api/tasks', { method: 'POST', body: { title } })
      .then((d) => { setTasks([d.task, ...tasks]); setTitle('') })
      .catch((e) => setError(e.message))
  }

  const toggle = (id) => {
    api('/api/tasks/' + id + '/toggle', { method: 'POST' })
      .then((d) => setTasks(tasks.map((t) => (t.id === d.task.id ? d.task : t))))
      .catch((e) => setError(e.message))
  }

  const del = (id) => {
    api('/api/tasks/' + id, { method: 'DELETE' })
      .then(() => setTasks(tasks.filter((t) => t.id !== id)))
      .catch((e) => setError(e.message))
  }

  return (
    <div>
      <AuthBar user={user} login={login} register={register} logout={logout} />
      <main>
        <p>%TAGLINE%</p>
        {error && <p className="error">{error}</p>}
        {user && (
          <div>
            <input placeholder="task title" value={title} onChange={(e) => setTitle(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') add() }} />
            <button onClick={add}>Add task</button>
          </div>
        )}
        <ul>
          {tasks.map((t) => (
            <li key={t.id}>
              <div className="row">
                <span style={{ textDecoration: t.done ? 'line-through' : 'none' }}>{t.title}</span>
                <span>
                  <button onClick={() => toggle(t.id)}>{t.done ? 'Undo' : 'Done'}</button>
                  <button onClick={() => del(t.id)}>Delete</button>
                </span>
              </div>
            </li>
          ))}
        </ul>
      </main>
    </div>
  )
}

export default App
"""

_REACT_CHAT_JSX = """import React, { useEffect, useState } from 'react'
%REACT_BOOTSTRAP%
%REACT_CSS%

function App() {
  const { user, setUser, login, register, logout } = useAuth()
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')

  useEffect(() => {
    api('/api/messages').then((d) => setMessages(d.messages || [])).catch(() => {})
    const source = new EventSource(API + '/api/messages/stream')
    source.onmessage = (e) => {
      try {
        const m = JSON.parse(e.data)
        setMessages((prev) => (prev.some((x) => x.id === m.id) ? prev : [m, ...prev]))
      } catch (_) {}
    }
    return () => source.close()
  }, [])

  const send = () => {
    api('/api/messages', { method: 'POST', body: { text } })
      .then(() => setText(''))
      .catch(() => {})
  }

  return (
    <div>
      <AuthBar user={user} login={login} register={register} logout={logout} />
      <main>
        <p>%TAGLINE%</p>
        <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, padding: '1rem', height: '50vh', overflowY: 'auto', marginBottom: '.5rem' }}>
          {messages.length === 0 && <div className="empty">No messages yet.</div>}
          {messages.map((m) => (
            <div className="msg" key={m.id}><strong>{m.user}:</strong> {m.text}</div>
          ))}
        </div>
        {user && (
          <div>
            <input placeholder="message text" value={text} onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') send() }} />
            <button onClick={send}>Send</button>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
"""

_REACT_COLLECTION_JSX = """import React, { useEffect, useState } from 'react'
%REACT_BOOTSTRAP%
%REACT_CSS%

function App() {
  const { user, login, register, logout } = useAuth()
  const [rows, setRows] = useState([])
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [error, setError] = useState('')

  const load = () => {
    api('/api/%COLLECTION%').then((d) => setRows(d['%COLLECTION%'] || [])).catch((e) => setError(e.message))
  }

  useEffect(() => {
    api('/api/%COLLECTION%').then((d) => setRows(d['%COLLECTION%'] || [])).catch(() => {})
  }, [])

  const add = () => {
    api('/api/%COLLECTION%', { method: 'POST', body: { title, body } })
      .then((d) => { setRows([d.item, ...rows]); setTitle(''); setBody('') })
      .catch((e) => setError(e.message))
  }

  const del = (id) => {
    api('/api/%COLLECTION%/' + id, { method: 'DELETE' })
      .then(() => setRows(rows.filter((r) => r.id !== id)))
      .catch((e) => setError(e.message))
  }

  return (
    <div>
      <AuthBar user={user} login={login} register={register} logout={logout} />
      <main>
        <p>%TAGLINE%</p>
        {error && <p className="error">{error}</p>}
        {user && (
          <div>
            <input placeholder="%ITEM_VERB% title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <input placeholder="%BODY_PLACEHOLDER%" value={body} onChange={(e) => setBody(e.target.value)} />
            <button onClick={add}>Add</button>
          </div>
        )}
        {rows.map((r) => (
          <div className="card" key={r.id} style={{ marginBottom: '.5rem' }}>
            <div className="row">
              <strong>{r.title}</strong>
              {user && r.user === user && <button onClick={() => del(r.id)}>Delete</button>}
            </div>
            <p>{r.body}</p>
          </div>
        ))}
      </main>
    </div>
  )
}

export default App
"""


_DJANGO_MANAGE = '''#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    from django.core.management import call_command, execute_from_command_line

    argv = sys.argv
    base = argv[1] if len(argv) > 1 else ""
    if base not in ("migrate", "makemigrations", "help", "shell", "version", "dbshell", "flush"):
        try:
            call_command("migrate", run_syncdb=True, verbosity=0, interactive=False)
            from api.seed import run as seed_run
            seed_run()
        except Exception as exc:
            sys.stderr.write(f"[auto] migrate/seed skipped: {exc}\\n")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
'''

_DJANGO_SETTINGS = '''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "brain-generated-dev-key-change-me")
DEBUG = os.environ.get("DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "api.apps.ApiConfig",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "config.urls"
APPEND_SLASH = False
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {}
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    from urllib.parse import urlparse
    u = urlparse(DATABASE_URL)
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": u.path.lstrip("/"),
        "USER": u.username,
        "PASSWORD": u.password,
        "HOST": u.hostname,
        "PORT": u.port or 5432,
    }
else:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DATABASE_PATH", str(BASE_DIR / "app.db")),
    }

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
'''

_DJANGO_URLS_CONFIG = '''from django.urls import include, path

urlpatterns = [
    path("", include("api.urls")),
]
'''

_DJANGO_WSGI = '''import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()


def _boot():
    from django.core.management import call_command
    try:
        call_command("migrate", run_syncdb=True, verbosity=0, interactive=False)
        from api.seed import run as seed_run
        seed_run()
    except Exception as exc:
        import sys
        sys.stderr.write(f"[auto] migrate/seed skipped: {exc}\\n")


_boot()
'''

_DJANGO_ASGI = '''import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
'''

_DJANGO_APPS = '''from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
'''

_DJANGO_AUTH = '''import hashlib
import secrets
from django.db import connection
from django.utils import timezone


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 600_000
    ).hex()


def new_session(username):
    token = secrets.token_hex(16)
    with connection.cursor() as c:
        c.execute(
            "INSERT INTO sessions (token, username, created_at) VALUES (%s, %s, %s)",
            [token, username, timezone.now()],
        )
    return token


def current_user(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    with connection.cursor() as c:
        c.execute("SELECT username FROM sessions WHERE token = %s", [header[7:].strip()])
        row = c.fetchone()
    return row[0] if row else None
'''

_DJANGO_VIEWS_COMMON = '''import json
import secrets
from datetime import date, datetime
from pathlib import Path
from django.db import IntegrityError, connection
from django.http import FileResponse, JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .auth import current_user, hash_password, new_session


def _body(request):
    try:
        return json.loads(request.body or b"{}")
    except Exception:
        return {}


def _rows(cursor):
    cols = [d[0] for d in cursor.description]
    return [
        {k: (v.isoformat() if isinstance(v, (datetime, date)) else v) for k, v in zip(cols, r)}
        for r in cursor.fetchall()
    ]


def _like(q):
    return "%" + q.replace("\\\\", "\\\\\\\\").replace("%", "\\\\%").replace("_", "\\\\_") + "%"


def _query_args(request):
    try:
        limit = min(max(int(request.GET.get("limit", 50)), 1), 200)
    except (TypeError, ValueError):
        limit = 50
    try:
        offset = max(int(request.GET.get("offset", 0)), 0)
    except (TypeError, ValueError):
        offset = 0
    return (request.GET.get("q") or "").strip(), limit, offset


def _spa_root():
    root = Path(__file__).resolve().parent.parent.parent / "frontend"
    dist = root / "dist"
    return dist if (dist / "index.html").exists() else root


@csrf_exempt
def healthz(request):
    with connection.cursor() as c:
        c.execute("SELECT 1")
    return JsonResponse({"status": "ok"})


@csrf_exempt
def me(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    return JsonResponse({"user": user})


@csrf_exempt
def register(request):
    body = _body(request)
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    if len(username) < 3 or len(password) < 4:
        return JsonResponse(
            {"error": "Username (>=3 chars) and password (>=4 chars) required"}, status=400
        )
    salt = secrets.token_hex(8)
    with connection.cursor() as c:
        try:
            c.execute(
                "INSERT INTO users (username, salt, password_hash, created_at) VALUES (%s, %s, %s, %s)",
                [username, salt, hash_password(password, salt), timezone.now()],
            )
        except IntegrityError:
            return JsonResponse({"error": "Username already taken"}, status=409)
        token = new_session(username)
    return JsonResponse({"token": token, "user": username}, status=201)


@csrf_exempt
def login(request):
    body = _body(request)
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    with connection.cursor() as c:
        c.execute("SELECT salt, password_hash FROM users WHERE username = %s", [username])
        row = c.fetchone()
    if not row or row[1] != hash_password(password, row[0]):
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    token = new_session(username)
    return JsonResponse({"token": token, "user": username})


@csrf_exempt
def logout(request):
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        with connection.cursor() as c:
            c.execute("DELETE FROM sessions WHERE token = %s", [header[7:].strip()])
    return JsonResponse({"ok": True})


@csrf_exempt
def assets(request, path):
    base = _spa_root() / "assets"
    target = (base / path).resolve()
    if not str(target).startswith(str(base.resolve())) or not target.is_file():
        return JsonResponse({"error": "Not found"}, status=404)
    return FileResponse(target.open("rb"))


@csrf_exempt
def spa_index(request):
    root = _spa_root()
    index = root / "index.html"
    if request.path.startswith("/api/") or not index.exists():
        return JsonResponse({"error": "Not found"}, status=404)
    return FileResponse(index.open("rb"))


@csrf_exempt
def api_404(request, **kwargs):
    if request.path.startswith("/api/"):
        return JsonResponse({"error": "Not found"}, status=404)
    return spa_index(request)
'''

_DJANGO_VIEWS_CART = _DJANGO_VIEWS_COMMON + '''CATALOG_TABLE = "{{TABLE}}"


def _order_dict(o):
    return {
        "id": o["id"], "user": o["username"], "items": json.loads(o["items"] or "{}"),
        "total": o["total"], "address": o["address"], "status": o["status"],
        "created_at": o["created_at"],
        "payment": {
            "method": o["payment_method"], "last4": o["payment_last4"],
            "amount": o["total"], "status": o["payment_status"],
        },
    }


@csrf_exempt
def list_items(request):
    q, limit, offset = _query_args(request)
    where, args = "", []
    if q:
        where = "WHERE name LIKE %s ESCAPE '\\\\'"
        args = [_like(q)]
    with connection.cursor() as c:
        c.execute("SELECT COUNT(*) AS n FROM " + CATALOG_TABLE + " " + where, args)
        total = c.fetchone()[0]
        c.execute(
            "SELECT id, name, category, price, rating FROM " + CATALOG_TABLE + " " + where
            + " ORDER BY id LIMIT %s OFFSET %s",
            args + [limit, offset],
        )
        items = _rows(c)
    return JsonResponse({"items": items, "total": total, "limit": limit, "offset": offset})


@csrf_exempt
def cart(request):
    if request.method == "POST":
        return add_to_cart(request)
    return get_cart(request)


@csrf_exempt
def orders(request):
    if request.method == "POST":
        return place_order(request)
    return list_orders(request)


@csrf_exempt
def get_cart(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    with connection.cursor() as c:
        c.execute("SELECT item_id, qty FROM cart_items WHERE username = %s", [user])
        rows = _rows(c)
    return JsonResponse({"items": {str(r["item_id"]): r["qty"] for r in rows}})


@csrf_exempt
def add_to_cart(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    body = _body(request)
    try:
        item_id = int(body.get("item_id", 0))
        qty = int(body.get("qty", 1))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid item"}, status=400)
    with connection.cursor() as c:
        c.execute("SELECT id FROM " + CATALOG_TABLE + " WHERE id = %s", [item_id])
        if not c.fetchone():
            return JsonResponse({"error": "Item not found"}, status=404)
        c.execute(
            "INSERT INTO cart_items (username, item_id, qty) VALUES (%s, %s, %s) "
            "ON CONFLICT(username, item_id) DO UPDATE SET qty = cart_items.qty + excluded.qty",
            [user, item_id, qty],
        )
        c.execute("SELECT item_id, qty FROM cart_items WHERE username = %s", [user])
        rows = _rows(c)
    return JsonResponse({"cart": {str(r["item_id"]): r["qty"] for r in rows}})


@csrf_exempt
def place_order(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    body = _body(request)
    payment = body.get("payment") or {}
    with connection.cursor() as c:
        c.execute("SELECT item_id, qty FROM cart_items WHERE username = %s", [user])
        cart = _rows(c)
    if not cart:
        return JsonResponse({"error": "Cart is empty"}, status=400)
    ids = ",".join(str(x["item_id"]) for x in cart)
    with connection.cursor() as c:
        c.execute("SELECT id, price FROM " + CATALOG_TABLE + " WHERE id IN (" + ids + ")")
        by_id = {r["id"]: r for r in _rows(c)}
    order_items = {str(x["item_id"]): x["qty"] for x in cart}
    total = round(sum(by_id[x["item_id"]]["price"] * x["qty"] for x in cart), 2)
    order_id = _insert_order(
        user, str(body.get("address", "")) or "Pickup", total,
        str(payment.get("method", "card")), str(payment.get("last4", "")),
        json.dumps(order_items),
    )
    with connection.cursor() as c:
        c.execute("DELETE FROM cart_items WHERE username = %s", [user])
        c.execute("SELECT * FROM orders WHERE id = %s", [order_id])
        order = _rows(c)[0]
    return JsonResponse({"order": _order_dict(order)}, status=201)


def _insert_order(user, address, total, method, last4, items):
    with connection.cursor() as c:
        c.execute(
            "INSERT INTO orders (username, address, total, payment_method, payment_last4, items, status, payment_status, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            [user, address, total, method, last4, items, "placed", "paid", timezone.now()],
        )
        return c.fetchone()[0]


@csrf_exempt
def list_orders(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    with connection.cursor() as c:
        c.execute("SELECT * FROM orders WHERE username = %s ORDER BY id", [user])
        rows = _rows(c)
    return JsonResponse({"orders": [_order_dict(o) for o in rows]})


@csrf_exempt
def advance_order(request, order_id):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    statuses = ["placed", "accepted", "delivered"]
    with connection.cursor() as c:
        c.execute("SELECT * FROM orders WHERE id = %s AND username = %s", [order_id, user])
        row = c.fetchone()
        if not row:
            return JsonResponse({"error": "Order not found"}, status=404)
        cols = [d[0] for d in c.description]
        row = dict(zip(cols, row))
        idx = statuses.index(row["status"]) if row["status"] in statuses else 0
        if idx < len(statuses) - 1:
            c.execute("UPDATE orders SET status = %s WHERE id = %s", [statuses[idx + 1], order_id])
        c.execute("SELECT * FROM orders WHERE id = %s", [order_id])
        order = _rows(c)[0]
    return JsonResponse({"order": _order_dict(order)})
'''

_DJANGO_VIEWS_TASKS = _DJANGO_VIEWS_COMMON + '''TASK_FIELDS = "id, username AS user, title, done, priority, created_at"


@csrf_exempt
def tasks(request):
    if request.method == "POST":
        return add_task(request)
    return list_tasks(request)


@csrf_exempt
def list_tasks(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    q, limit, offset = _query_args(request)
    where, args = "username = %s", [user]
    if q:
        where += " AND title LIKE %s ESCAPE '\\\\'"
        args.append(_like(q))
    with connection.cursor() as c:
        c.execute("SELECT COUNT(*) AS n FROM tasks WHERE " + where, args)
        total = c.fetchone()[0]
        c.execute(
            "SELECT " + TASK_FIELDS + " FROM tasks WHERE " + where + " ORDER BY id DESC LIMIT %s OFFSET %s",
            args + [limit, offset],
        )
        tasks = _rows(c)
    return JsonResponse({"tasks": tasks, "total": total, "limit": limit, "offset": offset})


@csrf_exempt
def add_task(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    body = _body(request)
    title = str(body.get("title", "")).strip()
    if not title:
        return JsonResponse({"error": "Title is required"}, status=400)
    with connection.cursor() as c:
        c.execute(
            "INSERT INTO tasks (username, title, priority, done, created_at) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            [user, title, str(body.get("priority", "medium")), 0, timezone.now()],
        )
        task_id = c.fetchone()[0]
        c.execute("SELECT " + TASK_FIELDS + " FROM tasks WHERE id = %s", [task_id])
        task = _rows(c)[0]
    return JsonResponse({"task": task}, status=201)


@csrf_exempt
def toggle_task(request, task_id):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    with connection.cursor() as c:
        c.execute("SELECT id FROM tasks WHERE id = %s AND username = %s", [task_id, user])
        if not c.fetchone():
            return JsonResponse({"error": "Task not found"}, status=404)
        c.execute("UPDATE tasks SET done = 1 - done WHERE id = %s", [task_id])
        c.execute("SELECT " + TASK_FIELDS + " FROM tasks WHERE id = %s", [task_id])
        task = _rows(c)[0]
    return JsonResponse({"task": task})


@csrf_exempt
def delete_task(request, task_id):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    with connection.cursor() as c:
        c.execute("DELETE FROM tasks WHERE id = %s AND username = %s", [task_id, user])
        deleted = c.rowcount > 0
    return JsonResponse({"deleted": deleted})
'''

_DJANGO_VIEWS_MESSAGES = _DJANGO_VIEWS_COMMON + '''import time

MSG_FIELDS = "id, username AS user, text, created_at"


@csrf_exempt
def messages(request):
    if request.method == "POST":
        return post_message(request)
    return list_messages(request)


@csrf_exempt
def list_messages(request):
    q, limit, offset = _query_args(request)
    where, args = "", []
    if q:
        where = "WHERE text LIKE %s ESCAPE '\\\\'"
        args = [_like(q)]
    with connection.cursor() as c:
        c.execute("SELECT COUNT(*) AS n FROM messages " + where, args)
        total = c.fetchone()[0]
        c.execute(
            "SELECT " + MSG_FIELDS + " FROM messages " + where + " ORDER BY id DESC LIMIT %s OFFSET %s",
            args + [limit, offset],
        )
        messages = _rows(c)
    return JsonResponse({"messages": messages, "total": total, "limit": limit, "offset": offset})


def message_stream(request):
    def gen():
        last_id = 0
        while True:
            with connection.cursor() as c:
                c.execute("SELECT " + MSG_FIELDS + " FROM messages WHERE id > %s ORDER BY id", [last_id])
                rows = _rows(c)
            for r in rows:
                last_id = r["id"]
                yield "data: " + json.dumps(r) + "\\n\\n"
            time.sleep(1)
    return StreamingHttpResponse(gen(), content_type="text/event-stream")


@csrf_exempt
def post_message(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    body = _body(request)
    text = str(body.get("text", "")).strip()
    if not text:
        return JsonResponse({"error": "Message text is required"}, status=400)
    with connection.cursor() as c:
        c.execute(
            "INSERT INTO messages (username, text, created_at) VALUES (%s, %s, %s) RETURNING id",
            [user, text, timezone.now()],
        )
        msg_id = c.fetchone()[0]
        c.execute("SELECT " + MSG_FIELDS + " FROM messages WHERE id = %s", [msg_id])
        msg = _rows(c)[0]
    return JsonResponse({"message": msg}, status=201)
'''

_DJANGO_VIEWS_COLLECTION = _DJANGO_VIEWS_COMMON + '''COLLECTION_TABLE = "{{TABLE}}"
COLLECTION_FIELDS = "id, username AS user, title, body, created_at"


def _read_guard(request):
    if {{PUBLIC_READ_CHECK}}:
        return current_user(request)
    return True


@csrf_exempt
def collection_items(request):
    if request.method == "POST":
        return add_collection_item(request)
    return list_collection(request)


@csrf_exempt
def list_collection(request):
    if _read_guard(request) is None:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    q, limit, offset = _query_args(request)
    where, args = "", []
    if q:
        where = "WHERE (title LIKE %s ESCAPE '\\\\' OR body LIKE %s ESCAPE '\\\\')"
        args = [_like(q), _like(q)]
    with connection.cursor() as c:
        c.execute("SELECT COUNT(*) AS n FROM " + COLLECTION_TABLE + " " + where, args)
        total = c.fetchone()[0]
        c.execute(
            "SELECT " + COLLECTION_FIELDS + " FROM " + COLLECTION_TABLE + " " + where
            + " ORDER BY id DESC LIMIT %s OFFSET %s",
            args + [limit, offset],
        )
        rows = _rows(c)
    return JsonResponse({"{{COLLECTION}}": rows, "total": total, "limit": limit, "offset": offset})


@csrf_exempt
def add_collection_item(request):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    body = _body(request)
    title = str(body.get("title", "")).strip()
    if not title:
        return JsonResponse({"error": "Title is required"}, status=400)
    text = str(body.get("body", "")).strip()
    with connection.cursor() as c:
        c.execute(
            "INSERT INTO " + COLLECTION_TABLE + " (username, title, body, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
            [user, title, text, timezone.now()],
        )
        item_id = c.fetchone()[0]
        c.execute("SELECT " + COLLECTION_FIELDS + " FROM " + COLLECTION_TABLE + " WHERE id = %s", [item_id])
        item = _rows(c)[0]
    return JsonResponse({"item": item}, status=201)


@csrf_exempt
def delete_collection_item(request, item_id):
    user = current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    with connection.cursor() as c:
        c.execute(
            "DELETE FROM " + COLLECTION_TABLE + " WHERE id = %s AND username = %s",
            [item_id, user],
        )
        deleted = c.rowcount > 0
    return JsonResponse({"deleted": deleted})
'''

_DJANGO_MODELS_CART = '''from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    salt = models.CharField(max_length=64)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"


class Session(models.Model):
    token = models.CharField(max_length=64, primary_key=True)
    username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessions"


class CatalogItem(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(default=0)
    rating = models.FloatField(default=0)

    class Meta:
        db_table = "{{TABLE}}"


class CartItem(models.Model):
    username = models.CharField(max_length=255)
    item_id = models.IntegerField()
    qty = models.IntegerField(default=1)

    class Meta:
        db_table = "cart_items"
        unique_together = ("username", "item_id")


class Order(models.Model):
    username = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, default="")
    total = models.FloatField(default=0)
    status = models.CharField(max_length=50, default="placed")
    payment_method = models.CharField(max_length=50, default="card")
    payment_last4 = models.CharField(max_length=20, blank=True, default="")
    payment_status = models.CharField(max_length=50, default="paid")
    items = models.TextField(blank=True, default="{}")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"
'''

_DJANGO_MODELS_TASKS = '''from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    salt = models.CharField(max_length=64)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"


class Session(models.Model):
    token = models.CharField(max_length=64, primary_key=True)
    username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessions"


class Task(models.Model):
    username = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    done = models.BooleanField(default=False)
    priority = models.CharField(max_length=50, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tasks"
'''

_DJANGO_MODELS_MESSAGES = '''from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    salt = models.CharField(max_length=64)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"


class Session(models.Model):
    token = models.CharField(max_length=64, primary_key=True)
    username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessions"


class Message(models.Model):
    username = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
'''

_DJANGO_MODELS_COLLECTION = '''from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    salt = models.CharField(max_length=64)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"


class Session(models.Model):
    token = models.CharField(max_length=64, primary_key=True)
    username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessions"


class Item(models.Model):
    username = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "{{TABLE}}"
'''

_DJANGO_URLS_COMMON = '''from django.urls import path, re_path

from . import views

urlpatterns = [
    path("healthz", views.healthz),
    path("api/auth/me", views.me),
    path("api/auth/register", views.register),
    path("api/auth/login", views.login),
    path("api/auth/logout", views.logout),
    {{URLS}}
    path("assets/<path:path>", views.assets),
    re_path(r"^api/.*$", views.api_404),
    re_path(r"^(?!api/).*", views.spa_index),
]
'''

_DJANGO_URLS_CART = '''    path("api/{{COLLECTION}}", views.list_items),
    path("api/cart", views.cart),
    path("api/orders", views.orders),
    path("api/orders/<int:order_id>/advance", views.advance_order),
'''

_DJANGO_URLS_TASKS = '''    path("api/tasks", views.tasks),
    path("api/tasks/<int:task_id>/toggle", views.toggle_task),
    path("api/tasks/<int:task_id>", views.delete_task),
'''

_DJANGO_URLS_MESSAGES = '''    path("api/messages", views.messages),
    path("api/messages/stream", views.message_stream),
'''

_DJANGO_URLS_COLLECTION = '''    path("api/{{COLLECTION}}", views.collection_items),
    path("api/{{COLLECTION}}/<int:item_id>", views.delete_collection_item),
'''

_DJANGO_SEED_CART = '''from .models import CatalogItem


def run():
    items = [
        {{SEED_DATA}}
    ]
    for i, (name, price) in enumerate(items):
        CatalogItem.objects.update_or_create(pk=i + 1, defaults={"name": name, "price": price})
'''

_DJANGO_SEED_EMPTY = '''def run():
    pass
'''


_DOCKERFILE_FLASK = (
    "FROM python:3.12-slim\n"
    "WORKDIR /app\n"
    "ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1\n"
    "COPY backend/requirements.txt .\n"
    "RUN pip install --no-cache-dir -r requirements.txt\n"
    "COPY backend/app.py backend/schema.sql .\n"
    "COPY frontend /frontend\n"
    "EXPOSE 8000\n"
    'CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]\n'
)

_DOCKERFILE_DJANGO = (
    "FROM python:3.12-slim\n"
    "WORKDIR /app\n"
    "ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1\n"
    "COPY backend/requirements.txt .\n"
    "RUN pip install --no-cache-dir -r requirements.txt\n"
    "COPY backend/ .\n"
    "COPY frontend /frontend\n"
    "EXPOSE 8000\n"
    'CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "config.wsgi:application"]\n'
)

_DOCKERFILE_NODE = (
    "FROM node:20-slim\n"
    "WORKDIR /app\n"
    "COPY backend/package.json .\n"
    "RUN npm install --omit=dev\n"
    "COPY backend/server.js .\n"
    "COPY frontend /frontend\n"
    "EXPOSE 3000\n"
    'CMD ["node", "server.js"]\n'
)


class AppBuilder:
    """Brain-owned application generator.

    Builds full, runnable projects (static websites, Flask web apps, CLI
    tools) deterministically and ONLY for programming languages the brain has
    already learned. No external LLM is involved."""

    def __init__(self, language_cortex, output_dir="generated_apps"):
        self.cortex = language_cortex
        self.output_dir = output_dir

    # ---------------------------------------------------------------
    # Gates
    # ---------------------------------------------------------------

    def _gate(self, language):
        lang = normalize_language(language)
        if not self.cortex.knows(lang):
            return False, lang, f"I have not learned {lang} yet. Ask me to learn it from the internet first."
        return True, lang, None

    def _project_path(self, name):
        folder = os.path.join(self.output_dir, _slug(name))
        os.makedirs(folder, exist_ok=True)
        return folder

    # ---------------------------------------------------------------
    # Static website (single self-contained HTML file)
    # ---------------------------------------------------------------

    def build_website(self, name="My Website", title="My Website", sections=None, theme="light"):
        ok, lang, err = self._gate("html")
        if not ok:
            return False, err
        name = _sanitize(name, "My Website")
        title = _sanitize(title, name)
        theme = "dark" if str(theme).lower() == "dark" else "light"
        sections = [s.strip() for s in (sections or "").split(";") if s.strip()] or ["Welcome"]
        nav_links = "".join(
            f'<a href="#{_slug(s)}">{_sanitize(s, "Section")}</a>' for s in sections
        )
        section_blocks = "".join(
            f'<section id="{_slug(s)}"><h2>{_sanitize(s, "Section")}</h2>'
            f'<p>This is the {_sanitize(s, "section")} section of {title}.</p></section>'
            for s in sections
        )
        bg = "#1e1e2e" if theme == "dark" else "#f4f4f9"
        fg = "#e6e6ef" if theme == "dark" else "#22223b"
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{ margin: 0; font-family: -apple-system, Segoe UI, Roboto, sans-serif;
         background: {bg}; color: {fg}; }}
  header {{ padding: 1.2rem 2rem; display: flex; justify-content: space-between;
           align-items: center; border-bottom: 2px solid rgba(128,128,160,.3); }}
  nav a {{ color: {fg}; margin-right: 1rem; text-decoration: none; }}
  main {{ padding: 2rem; max-width: 900px; margin: auto; }}
  section {{ margin: 2rem 0; padding: 1rem 1.5rem; border-radius: 8px;
            background: rgba(128,128,160,.08); }}
  button {{ padding: .6rem 1.2rem; border: 0; border-radius: 6px; cursor: pointer;
           background: #6c63ff; color: white; font-size: 1rem; }}
  footer {{ text-align: center; padding: 1.5rem; color: rgba(128,128,160,.8); }}
</style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <nav>{nav_links}</nav>
  </header>
  <main>
    <button onclick="greet()">Say hello</button>
    <p id="hello"></p>
{section_blocks}
  </main>
  <footer>Generated by the Aashu Virtual Brain (learned: html)</footer>
  <script>
    function greet() {{
      document.getElementById('hello').textContent =
        'Hello from {title}! This site was built from the brain's learned html knowledge.';
    }}
  </script>
</body>
</html>
"""
        folder = self._project_path(name)
        path = os.path.join(folder, "index.html")
        with open(path, "w") as f:
            f.write(html)
        return True, f"Built website '{title}' at {path} ({len(sections)} sections, {theme} theme). Open in a browser to view."

    # ---------------------------------------------------------------
    # Flask web app (multi-file runnable project)
    # ---------------------------------------------------------------

    def build_webapp(self, name="My App", app_name="app", features=None, pages=None):
        ok, lang, err = self._gate("python")
        if not ok:
            return False, err
        name = _sanitize(name, "My App")
        app_name = _slug(_sanitize(app_name, "app"))
        features = [f.strip() for f in (features or "").split(";") if f.strip()] or ["Home"]
        pages = [p.strip() for p in (pages or "").split(";") if p.strip()] or features
        routes = "".join(
            f"\n@app.route('/{_slug(p)}')\ndef page_{_slug(p).replace('-', '_')}():\n"
            f"    return render_template('index.html', title='{_sanitize(p)}', app_name={app_name!r})\n"
            for p in pages
        )
        feature_list = ", ".join(features)
        app_py = f'''"""
{name} - a Flask web application generated by the Aashu Virtual Brain.
Features: {feature_list}
Run with: python {app_name}.py  (then open http://127.0.0.1:5000)
"""
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html', title='Home', app_name={app_name!r})
{routes}

if __name__ == '__main__':
    app.run(debug=True)
'''
        template_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} - {{ app_name }}</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header><h1>{{ app_name }}</h1><nav><a href="/">Home</a></nav></header>
  <main>
    <h2>{{ title }}</h2>
    <p>Welcome to {{ title }}. This page is served by the Flask app generated from
       the brain's learned python knowledge.</p>
  </main>
  <footer>{{ app_name }} &mdash; generated by Aashu</footer>
</body>
</html>
"""
        style_css = """body { margin: 0; font-family: -apple-system, Segoe UI, Roboto, sans-serif;
       background: #f4f4f9; color: #22223b; }
header { background: #6c63ff; color: #fff; padding: 1rem 2rem; }
nav a { color: #fff; margin-right: 1rem; text-decoration: none; }
main { padding: 2rem; max-width: 800px; margin: auto; }
footer { text-align: center; padding: 1.5rem; color: #888; }
"""
        folder = self._project_path(name)
        files = {
            f"{app_name}.py": app_py,
            "templates/index.html": template_html,
            "static/style.css": style_css,
            "requirements.txt": "flask>=3.0\n",
        }
        for rel, content in files.items():
            full = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(content)
        return True, (f"Built Flask web app '{name}' at {folder} "
                      f"({len(pages)} pages: {', '.join(pages)}). "
                      f"Run: python {app_name}.py")

    # ---------------------------------------------------------------
    # CLI tool (single-file Python program)
    # ---------------------------------------------------------------

    def build_cli(self, name="tool", task="print a friendly message", args=None):
        ok, lang, err = self._gate("python")
        if not ok:
            return False, err
        name = _slug(_sanitize(name, "tool"))
        task = _sanitize(task, "print a friendly message")
        arg_defs = []
        arg_uses = []
        for i, a in enumerate((args or "").split(";")[:6]):
            a = a.strip()
            if not a:
                continue
            akey = _slug(a).replace("-", "_")
            arg_defs.append(f"    parser.add_argument('--{akey}', default='{_sanitize(a)}')")
            arg_uses.append(f"    print(f'  - {_sanitize(a)}: {{args.{akey}}}')")
        arg_uses_code = "\n".join(arg_uses) or "    print('  - no arguments provided')"
        cli = f'''#!/usr/bin/env python3
"""{name} - {task}

Generated by the Aashu Virtual Brain (learned: python).
Run with: python {name}.py [options]
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description='{task}')
{chr(10).join(arg_defs)}
    args = parser.parse_args()
    print('=== {name} ===')
    print('Task: {task}')
{arg_uses_code}


if __name__ == '__main__':
    main()
'''
        folder = self._project_path(name)
        path = os.path.join(folder, f"{name}.py")
        with open(path, "w") as f:
            f.write(cli)
        return True, f"Built CLI tool '{name}' at {path} (task: {task}). Run: python {path}"

    # ---------------------------------------------------------------
    # React (Vite) web app (multi-file runnable project)
    # ---------------------------------------------------------------

    def build_reactapp(self, name="My App", app_name="app", features=None, pages=None):
        ok, lang, err = self._gate("reactjs")
        if not ok:
            return False, err
        name = _sanitize(name, "My App")
        app_name = _slug(_sanitize(app_name, "app"))
        features = [f.strip() for f in (features or "").split(";") if f.strip()] or ["Home"]
        pages = [p.strip() for p in (pages or "").split(";") if p.strip()] or features
        nav = " ".join(
            f'<li key="{_slug(p)}">{_sanitize(p)}</li>' for p in pages
        )
        feature_list = ", ".join(features)
        app_jsx = f"""import {{ useState }} from 'react';
import './index.css';

function App() {{
  const [count, setCount] = useState(0);

  return (
    <div className="App">
      <header>
        <h1>{name}</h1>
        <ul className="nav">
          {nav}
        </ul>
      </header>
      <main>
        <h2>Welcome</h2>
        <p>This React app was generated from the brain's learned reactjs knowledge.</p>
        <p>Features: {feature_list}</p>
        <button onClick={{() => setCount((c) => c + 1)}}>Count: {{{{count}}}}</button>
      </main>
    </div>
  );
}}

export default App;
"""
        main_jsx = "import React from 'react';\nimport { createRoot } from 'react-dom/client';\nimport App from './App.jsx';\n\ncreateRoot(document.getElementById('root')).render(<App />);\n"
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>%s</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
""" % name
        index_css = """:root { font-family: -apple-system, Segoe UI, Roboto, sans-serif; }
body { margin: 0; background: #f4f4f9; color: #22223b; }
.App { text-align: center; }
header { background: #6c63ff; color: #fff; padding: 1rem 2rem; }
.nav { list-style: none; display: flex; gap: 1rem; justify-content: center; padding: 0; }
button { padding: .6rem 1.2rem; border: 0; border-radius: 6px; background: #6c63ff; color: #fff; cursor: pointer; }
"""
        package_json = """{
  "name": "%s",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build", "preview": "vite preview" },
  "dependencies": { "react": "^18.3.1", "react-dom": "^18.3.1" },
  "devDependencies": { "@vitejs/plugin-react": "^4.3.1", "vite": "^5.4.0" }
}
""" % _slug(name)
        vite_config = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({ plugins: [react()] });
"""
        folder = self._project_path(name)
        files = {
            "package.json": package_json,
            "vite.config.js": vite_config,
            "index.html": index_html,
            "src/main.jsx": main_jsx,
            "src/App.jsx": app_jsx,
            "src/index.css": index_css,
        }
        for rel, content in files.items():
            full = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(content)
        return True, (f"Built React web app '{name}' at {folder} ({len(pages)} pages: {', '.join(pages)}). "
                      f"Run: cd {folder} && npm install && npm run dev")

    # ---------------------------------------------------------------
    # Angular (standalone) web app
    # ---------------------------------------------------------------

    def build_angularapp(self, name="My App", app_name="app", features=None, pages=None):
        ok, lang, err = self._gate("angular")
        if not ok:
            return False, err
        name = _sanitize(name, "My App")
        app_name = _slug(_sanitize(app_name, "app"))
        features = [f.strip() for f in (features or "").split(";") if f.strip()] or ["Home"]
        pages = [p.strip() for p in (pages or "").split(";") if p.strip()] or features
        nav = " ".join(f'<li>{_sanitize(p)}</li>' for p in pages)
        feature_list = ", ".join(features)
        app_ts = f"""import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-root',
  template: `
    <header><h1>{name}</h1><ul class="nav">{nav}</ul></header>
    <main>
      <h2>Welcome</h2>
      <p>This Angular app was generated from the brain's learned angular knowledge.</p>
      <p>Features: {feature_list}</p>
    </main>
  `,
  styles: [`:host {{ text-align: center; }} .nav {{ list-style: none; display: flex; gap: 1rem; justify-content: center; }}`]
}})
export class AppComponent {{ title = '{name}'; }}
"""
        main_ts = """import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent);
"""
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>%s</title>
</head>
<body>
  <app-root></app-root>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
""" % name
        angular_json = """{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "app": {
      "projectType": "application",
      "root": "",
      "sourceRoot": "src",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:browser",
          "options": { "outputPath": "dist", "index": "index.html", "main": "src/main.ts", "tsConfig": "tsconfig.json" }
        }
      }
    }
  }
}
"""
        package_json = """{
  "name": "%s",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@angular/core": "^18.2.0",
    "@angular/platform-browser": "^18.2.0"
  },
  "devDependencies": {
    "@angular/cli": "^18.2.0",
    "@angular-devkit/build-angular": "^18.2.0",
    "typescript": "^5.5.0"
  },
  "scripts": { "start": "ng serve" }
}
""" % _slug(name)
        tsconfig_json = """{
  "compilerOptions": { "target": "ES2022", "module": "ES2022", "experimentalDecorators": true,
                       "moduleResolution": "bundler", "strict": true },
  "files": ["src/main.ts", "src/app/app.component.ts"]
}
"""
        folder = self._project_path(name)
        files = {
            "package.json": package_json,
            "angular.json": angular_json,
            "tsconfig.json": tsconfig_json,
            "index.html": index_html,
            "src/main.ts": main_ts,
            "src/app/app.component.ts": app_ts,
        }
        for rel, content in files.items():
            full = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(content)
        return True, (f"Built Angular web app '{name}' at {folder} ({len(pages)} pages: {', '.join(pages)}). "
                      f"Run: cd {folder} && npm install && npm start")

    # ---------------------------------------------------------------
    # Vue (Vite) web app
    # ---------------------------------------------------------------

    def build_vueapp(self, name="My App", app_name="app", features=None, pages=None):
        ok, lang, err = self._gate("vuejs")
        if not ok:
            return False, err
        name = _sanitize(name, "My App")
        app_name = _slug(_sanitize(app_name, "app"))
        features = [f.strip() for f in (features or "").split(";") if f.strip()] or ["Home"]
        pages = [p.strip() for p in (pages or "").split(";") if p.strip()] or features
        nav = " ".join(f"<li>{_sanitize(p)}</li>" for p in pages)
        feature_list = ", ".join(features)
        app_vue = f"""<script setup>
import {{ ref }} from 'vue';

const count = ref(0);
const features = '{feature_list}';
</script>

<template>
  <header><h1>{name}</h1><ul class="nav">{nav}</ul></header>
  <main>
    <h2>Welcome</h2>
    <p>This Vue app was generated from the brain's learned vuejs knowledge.</p>
    <p>Features: {{{{ features }}}}</p>
    <button @click="count++">Count: {{{{ count }}}}</button>
  </main>
</template>

<style scoped>
:host {{ text-align: center; }}
.nav {{ list-style: none; display: flex; gap: 1rem; justify-content: center; }}
</style>
"""
        main_js = """import { createApp } from 'vue';
import App from './App.vue';
import './style.css';

createApp(App).mount('#app');
"""
        style_css = """body { margin: 0; font-family: -apple-system, Segoe UI, Roboto, sans-serif; background: #f4f4f9; color: #22223b; }
header { background: #6c63ff; color: #fff; padding: 1rem 2rem; }
.nav { list-style: none; display: flex; gap: 1rem; justify-content: center; padding: 0; }
button { padding: .6rem 1.2rem; border: 0; border-radius: 6px; background: #6c63ff; color: #fff; cursor: pointer; }
"""
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>%s</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
""" % name
        package_json = """{
  "name": "%s",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build", "preview": "vite preview" },
  "dependencies": { "vue": "^3.4.0" },
  "devDependencies": { "@vitejs/plugin-vue": "^5.1.0", "vite": "^5.4.0" }
}
""" % _slug(name)
        vite_config = """import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({ plugins: [vue()] });
"""
        folder = self._project_path(name)
        files = {
            "package.json": package_json,
            "vite.config.js": vite_config,
            "index.html": index_html,
            "src/main.js": main_js,
            "src/App.vue": app_vue,
            "src/style.css": style_css,
        }
        for rel, content in files.items():
            full = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(content)
        return True, (f"Built Vue web app '{name}' at {folder} ({len(pages)} pages: {', '.join(pages)}). "
                      f"Run: cd {folder} && npm install && npm run dev")

    # ---------------------------------------------------------------
    # Node/Express API server
    # ---------------------------------------------------------------

    def build_node_server(self, name="My Server", app_name="server", endpoints=None):
        ok, lang, err = self._gate("nodejs")
        if not ok:
            return False, err
        name = _sanitize(name, "My Server")
        app_name = _slug(_sanitize(app_name, "server"))
        endpoints = [e.strip() for e in (endpoints or "").split(";") if e.strip()] or ["/", "/health"]
        routes = []
        for ep in endpoints:
            clean = re.sub(r"[^A-Za-z0-9 _\-\./]", "", ep).strip()
            clean = re.sub(r"\s+", " ", clean).strip()
            if not clean.startswith("/"):
                clean = "/" + clean
            key = _slug(clean.replace("/", " ")) or "health"
            routes.append(
                f"app.get({clean!r}, (req, res) => res.json({{ route: {clean!r}, ok: true }}));"
            )
        route_code = "\n".join(routes)
        server_js = f"""const express = require('express');
const app = express();
app.use(express.json());

// Endpoints generated from the brain's learned nodejs knowledge.
{route_code}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`{name} listening on :${{PORT}}`));
"""
        package_json = """{
  "name": "%s",
  "version": "0.1.0",
  "private": true,
  "main": "server.js",
  "scripts": { "start": "node server.js" },
  "dependencies": { "express": "^4.19.0" }
}
""" % _slug(name)
        folder = self._project_path(name)
        files = {
            "server.js": server_js,
            "package.json": package_json,
        }
        for rel, content in files.items():
            full = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(content)
        return True, (f"Built Node/Express server '{name}' at {folder} ({len(endpoints)} endpoints: {', '.join(endpoints)}). "
                      f"Run: cd {folder} && npm install && npm start")

    # ---------------------------------------------------------------
    # SQL schema generator
    # ---------------------------------------------------------------

    def build_sql_schema(self, name="app", entities=None):
        ok, lang, err = self._gate("sql")
        if not ok:
            return False, err
        name = _slug(_sanitize(name, "app"))
        entities = [e.strip() for e in (entities or "").split(";") if e.strip()] or ["users"]
        lines = [f"-- SQL schema for {name} generated by the Aashu Virtual Brain."]
        for i, entity in enumerate(entities):
            table = _slug(entity.replace(" ", "_")) or f"entity_{i}"
            lines.append(
                f"\nCREATE TABLE IF NOT EXISTS {table} (\n"
                f"    id SERIAL PRIMARY KEY,\n"
                f"    name VARCHAR(255) NOT NULL,\n"
                f"    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
                f");"
            )
        folder = self._project_path(name)
        path = os.path.join(folder, "schema.sql")
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        return True, f"Built SQL schema '{name}' at {path} ({len(entities)} tables: {', '.join(entities)}). Apply with any SQL database."

    # ---------------------------------------------------------------
    # Vertical full-stack apps (food delivery, ecommerce, tracker, chat)
    # ---------------------------------------------------------------

    def build_fullstack(self, name="My App", kind="food_delivery", backend="flask",
                        frontend="single", theme="light"):
        """Build a complete, runnable full-stack vertical app.

        backend:  flask | django | express | fastify
        frontend: react (Vite SPA, built and served by the backend) | single (one HTML file)

        Persistence: SQLite (zero config) by default; PostgreSQL automatically
        when DATABASE_URL is set. Gated on learned Python."""
        ok, lang, err = self._gate("python")
        if not ok:
            return False, err
        kind_key = _normalize_kind(kind)
        if kind_key is None:
            return False, (f"Unknown app kind '{kind}'. Available kinds: "
                           f"{', '.join(sorted(FULLSTACK_KINDS))}.")
        backend_key = _normalize_backend(backend)
        frontend_key = _normalize_frontend(frontend)
        spec = FULLSTACK_KINDS[kind_key]
        name = _sanitize(name, "My App")
        folder = self._project_path(name)
        theme = "dark" if str(theme).lower() == "dark" else "light"
        cart_mode = spec["mode"] == "cart"

        api_base, api_port = {
            "flask": ("http://127.0.0.1:5000", 5000),
            "django": ("http://127.0.0.1:8000", 8000),
            "express": ("http://127.0.0.1:3000", 3000),
            "fastify": ("http://127.0.0.1:3000", 3000),
        }[backend_key]

        files = {}
        if frontend_key == "react":
            files.update(self._react_frontend(spec, name, cart_mode, theme, api_port))
        else:
            files["frontend/index.html"] = self._fullstack_frontend(spec, name, cart_mode, theme, api_base)

        if backend_key == "flask":
            files["backend/app.py"] = self._fullstack_backend(spec, cart_mode, backend_key, name)
            files["backend/requirements.txt"] = "flask>=3.0\ngunicorn>=21.0\npsycopg[binary]>=3.1\n"
            files["backend/Dockerfile"] = _DOCKERFILE_FLASK
        elif backend_key == "django":
            files.update(self._django_project(spec, cart_mode))
        else:
            files["backend/server.js"] = self._fullstack_backend(spec, cart_mode, backend_key, name)
            files["backend/package.json"] = self._node_package_json(name, backend_key)
            files["backend/Dockerfile"] = _DOCKERFILE_NODE
        files["backend/schema.sql"] = spec["schema"]
        files["docker-compose.yml"] = self._docker_compose(backend_key)
        files[".dockerignore"] = "**/node_modules\n**/.venv\n**/__pycache__\nfrontend/node_modules\n"
        files["README.md"] = self._fullstack_readme(name, spec, backend_key, frontend_key)

        for rel, content in files.items():
            full = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(content)
        return True, (
            f"Built full-stack '{spec['title']}' app '{name}' at {folder} "
            f"(backend: {backend_key}, frontend: {frontend_key}; SQLite by default, "
            f"PostgreSQL via DATABASE_URL; auth, "
            f"{'payments, ' if cart_mode else ''}search + pagination, Docker deployment). "
            f"See README.md for run steps."
        )

    def _django_project(self, spec, cart_mode):
        collection = spec["collection"]
        if cart_mode:
            table = {"menu": "menu_items", "products": "products", "services": "services"}.get(collection, "products")
            models = _DJANGO_MODELS_CART.replace("{{TABLE}}", table)
            views = _DJANGO_VIEWS_CART.replace("{{TABLE}}", table)
            urls = _DJANGO_URLS_CART.replace("{{COLLECTION}}", collection)
            seed_data = ",\n        ".join(
                "('{}', {})".format(nm.replace("'", "''"), price)
                for i, (nm, price) in enumerate(spec["seed"])
            )
            seed = _DJANGO_SEED_CART.replace("{{SEED_DATA}}", seed_data)
        elif collection == "tasks":
            models, views, urls, seed = _DJANGO_MODELS_TASKS, _DJANGO_VIEWS_TASKS, _DJANGO_URLS_TASKS, _DJANGO_SEED_EMPTY
        elif collection == "messages":
            models, views, urls, seed = _DJANGO_MODELS_MESSAGES, _DJANGO_VIEWS_MESSAGES, _DJANGO_URLS_MESSAGES, _DJANGO_SEED_EMPTY
        else:
            table = collection
            models = _DJANGO_MODELS_COLLECTION.replace("{{TABLE}}", table)
            views = (_DJANGO_VIEWS_COLLECTION
                     .replace("{{TABLE}}", table)
                     .replace("{{COLLECTION}}", collection)
                     .replace("{{PUBLIC_READ_CHECK}}", "False" if spec.get("public_read") else "True"))
            urls = _DJANGO_URLS_COLLECTION.replace("{{COLLECTION}}", collection)
            seed = _DJANGO_SEED_EMPTY
        return {
            "backend/manage.py": _DJANGO_MANAGE,
            "backend/requirements.txt": "django>=5.0\ngunicorn>=21.0\npsycopg[binary]>=3.1\n",
            "backend/config/__init__.py": "",
            "backend/config/settings.py": _DJANGO_SETTINGS,
            "backend/config/urls.py": _DJANGO_URLS_CONFIG,
            "backend/config/wsgi.py": _DJANGO_WSGI,
            "backend/config/asgi.py": _DJANGO_ASGI,
            "backend/api/__init__.py": "",
            "backend/api/apps.py": _DJANGO_APPS,
            "backend/api/auth.py": _DJANGO_AUTH,
            "backend/api/models.py": models,
            "backend/api/views.py": views,
            "backend/api/urls.py": _DJANGO_URLS_COMMON.replace("{{URLS}}", urls),
            "backend/api/seed.py": seed,
            "backend/Dockerfile": _DOCKERFILE_DJANGO,
        }

    @staticmethod
    def _node_package_json(name, backend_key):
        deps = {
            "express": {"express": "^4.21.0"},
            "fastify": {"fastify": "^4.28.0", "@fastify/static": "^7.0.0"},
        }[backend_key]
        deps["better-sqlite3"] = "^12.2.0"
        deps["pg"] = "^8.13.0"
        lines = ",\n".join(f'    "{k}": "{v}"' for k, v in deps.items())
        return (
            "{\n"
            f'  "name": "{_slug(name)}-backend",\n'
            '  "version": "1.0.0",\n'
            '  "private": true,\n'
            '  "type": "commonjs",\n'
            '  "scripts": { "start": "node server.js" },\n'
            '  "dependencies": {\n'
            f"{lines}\n"
            "  }\n"
            "}\n"
        )

    @staticmethod
    def _docker_compose(backend_key):
        ports = {
            "flask": '      - "8000:8000"\n      - "5000:8000"\n',
            "django": '      - "8000:8000"\n',
            "express": '      - "3000:3000"\n',
            "fastify": '      - "3000:3000"\n',
        }[backend_key]
        return (
            "services:\n"
            "  db:\n"
            "    image: postgres:16-alpine\n"
            "    environment:\n"
            "      POSTGRES_DB: app\n"
            "      POSTGRES_USER: app\n"
            "      POSTGRES_PASSWORD: app\n"
            "    volumes:\n"
            "      - dbdata:/var/lib/postgresql/data\n"
            "    healthcheck:\n"
            "      test: [\"CMD-SHELL\", \"pg_isready -U app -d app\"]\n"
            "      interval: 5s\n"
            "      timeout: 5s\n"
            "      retries: 10\n"
            "  web:\n"
            "    build: .\n"
            "    ports:\n"
            f"{ports}"
            "    environment:\n"
            "      - DATABASE_URL=postgresql://app:app@db:5432/app\n"
            "    depends_on:\n"
            "      db:\n"
            "        condition: service_healthy\n"
            "volumes:\n"
            "  dbdata:\n"
        )

    @staticmethod
    def _fullstack_readme(name, spec, backend_key, frontend_key):
        kind_title, tagline = spec["title"], spec["tagline"]
        stack_line = {
            "flask": "Flask + gunicorn",
            "django": "Django + gunicorn",
            "express": "Express",
            "fastify": "Fastify",
        }[backend_key]
        if backend_key == "flask":
            dev_cmd = "python app.py  # API on :5000 (SQLite app.db created on first boot)"
            prod_cmd = "gunicorn -w 4 -b 0.0.0.0:8000 app:app"
        elif backend_key == "django":
            dev_cmd = "python manage.py runserver  # API on :8000 (auto-migrates + seeds on boot)"
            prod_cmd = "gunicorn -w 4 -b 0.0.0.0:8000 config.wsgi:application"
        else:
            dev_cmd = "node server.js  # API on :3000 (SQLite app.db created on first boot)"
            prod_cmd = "node server.js"
        if frontend_key == "react":
            frontend_dev = (
                "3. `cd frontend && npm install && npm run dev` — Vite serves the SPA on :5173 and\n"
                "   proxies `/api` to the backend, so auth/session state stays on one origin.\n"
                "4. For production, build once: `cd frontend && npm run build`. The backend then\n"
                "   serves `frontend/dist` at `/` (single origin, no CORS)."
            )
        else:
            frontend_dev = (
                "3. Open `frontend/index.html` in a browser. In dev it talks to the API at\n"
                "   `%API_BASE%`; in Docker the backend serves it at `/` on the same origin."
            )
        frontend_dev = frontend_dev.replace("%API_BASE%", {
            "flask": "http://127.0.0.1:5000", "django": "http://127.0.0.1:8000",
            "express": "http://127.0.0.1:3000", "fastify": "http://127.0.0.1:3000",
        }[backend_key])
        return (
            f"# {name}\n\n{kind_title} — {tagline}.\n\n"
            f"Backend: **{stack_line}**. Frontend: **{'React + Vite' if frontend_key == 'react' else 'single HTML file'}**. "
            "Persistence: **SQLite** (zero config) or **PostgreSQL** via `DATABASE_URL`.\n\n"
            "## Run it (dev)\n\n"
            "1. Backend env: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`\n"
            f"2. {dev_cmd}\n"
            f"{frontend_dev}\n\n"
            "PostgreSQL instead of SQLite: set `DATABASE_URL=postgresql://user:pass@host:5432/dbname` "
            "before starting the backend — schema and seeds migrate automatically.\n\n"
            "## Run it (production-ish)\n\n"
            "Option A — process manager:\n\n"
            f"`{prod_cmd}` from the backend folder. For PostgreSQL point `DATABASE_URL` at a managed "
            "instance (or the local `db` service) so any number of workers share one store. "
            "Put a reverse proxy (nginx) in front for TLS.\n\n"
            "Option B — Docker (PostgreSQL included):\n\n"
            "1. If the frontend is React, build it first: `cd frontend && npm install && npm run build`.\n"
            "2. `docker compose up --build` from the project root. The `db` service runs PostgreSQL 16 "
            "and `web` is wired to it via `DATABASE_URL`; the backend serves the frontend at `/`.\n\n"
            "State survives restarts: users, sessions, carts, orders and messages are persisted "
            f"in `backend/app.db` (dev) or PostgreSQL (Docker/production).\n\n"
            "Generated deterministically by the Aashu Virtual Brain. No external LLM involved.\n"
        )

    def _fullstack_backend(self, spec, cart_mode, backend, name):
        collection = spec["collection"]
        item_verb = spec["item_verb"]
        if backend in ("express", "fastify"):
            return self._node_backend(spec, cart_mode, backend, name)
        schema_literal = json_dumps(spec["schema"])
        schema_pg_literal = json_dumps(_pg_schema(spec["schema"]))
        if cart_mode:
            table = {"menu": "menu_items", "products": "products", "services": "services"}.get(collection, "products")
            seeds = "; ".join(
                "db.execute("
                + json_dumps(
                    "INSERT OR IGNORE INTO {} (id, name, price) VALUES ({}, '{}', {})".format(
                        table, i + 1, name.replace(chr(39), chr(39) * 2), price
                    )
                )
                + ")"
                for i, (name, price) in enumerate(spec["seed"])
            )
            seeds_pg = _pg_seed(seeds)
            return (_FULLSTACK_BACKEND_CART
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SCHEMA_PG}}", schema_pg_literal)
                    .replace("{{SEED_SQL}}", seeds)
                    .replace("{{SEED_SQL_PG}}", seeds_pg)
                    .replace("{{TABLE}}", table)
                    .replace("{{COLLECTION}}", collection)
                    .replace("{{ITEM_VERB}}", item_verb))
        if collection == "tasks":
            return (_FULLSTACK_BACKEND_TASKS
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SCHEMA_PG}}", schema_pg_literal)
                    .replace("{{SEED_SQL}}", "")
                    .replace("{{SEED_SQL_PG}}", ""))
        if collection == "messages":
            return (_FULLSTACK_BACKEND_MESSAGES
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SCHEMA_PG}}", schema_pg_literal)
                    .replace("{{SEED_SQL}}", "")
                    .replace("{{SEED_SQL_PG}}", ""))
        return (_FULLSTACK_BACKEND_COLLECTION
                .replace("{{SCHEMA}}", schema_literal)
                .replace("{{SCHEMA_PG}}", schema_pg_literal)
                .replace("{{SEED_SQL}}", "")
                .replace("{{SEED_SQL_PG}}", "")
                .replace("{{TABLE}}", collection)
                .replace("{{COLLECTION}}", collection)
                .replace("{{PUBLIC_READ_CHECK}}", "False" if spec.get("public_read") else "True"))

    def _node_backend(self, spec, cart_mode, backend, name):
        """Express or Fastify backend, shared SQLite/PG data layer."""
        collection = spec["collection"]
        item_verb = spec["item_verb"]
        schema_literal = json_dumps(spec["schema"])
        schema_pg_literal = json_dumps(_pg_schema(spec["schema"]))
        head = _EXPRESS_HEAD if backend == "express" else _FASTIFY_HEAD
        if cart_mode:
            table = {"menu": "menu_items", "products": "products", "services": "services"}.get(collection, "products")
            routes = (_EXPRESS_ROUTES_CART if backend == "express" else _FASTIFY_ROUTES_CART)
            return (head
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SEED_SQL_NODE}}", _node_cart_seeds(table, spec["seed"], False))
                    .replace("{{SEED_SQL_NODE_PG}}", _node_cart_seeds(table, spec["seed"], True))
                    .replace("{{ROUTES}}", routes
                             .replace("{{TABLE}}", table)
                             .replace("{{COLLECTION}}", collection))
                    .replace("{{TITLE}}", name))
        if collection == "tasks":
            routes = (_EXPRESS_ROUTES_TASKS if backend == "express" else _FASTIFY_ROUTES_TASKS)
            return (head
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SEED_SQL_NODE}}", "")
                    .replace("{{SEED_SQL_NODE_PG}}", "")
                    .replace("{{ROUTES}}", routes)
                    .replace("{{TITLE}}", name))
        if collection == "messages":
            routes = (_EXPRESS_ROUTES_MESSAGES if backend == "express" else _FASTIFY_ROUTES_MESSAGES)
            return (head
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SEED_SQL_NODE}}", "")
                    .replace("{{SEED_SQL_NODE_PG}}", "")
                    .replace("{{ROUTES}}", routes)
                    .replace("{{TITLE}}", name))
        routes = (_EXPRESS_ROUTES_COLLECTION if backend == "express" else _FASTIFY_ROUTES_COLLECTION)
        return (head
                .replace("{{SCHEMA}}", schema_literal)
                .replace("{{SEED_SQL_NODE}}", "")
                .replace("{{SEED_SQL_NODE_PG}}", "")
                .replace("{{ROUTES}}", routes
                         .replace("{{TABLE}}", collection)
                         .replace("{{COLLECTION}}", collection)
                         .replace("{{PUBLIC_READ_CHECK}}",
                                  "true" if spec.get("public_read") else "false"))
                .replace("{{TITLE}}", name))

    def _fullstack_frontend(self, spec, name, cart_mode, theme, api_base):
        collection = spec["collection"]
        title = spec["title"]
        tagline = spec["tagline"]
        item_verb = spec["item_verb"]
        cart_label = spec["cart_label"]
        public_read = spec.get("public_read", False)
        if collection == "tasks":
            base = _FULLSTACK_FRONTEND_TASKS
            placeholder = "task title"
        elif collection == "messages":
            base = _FULLSTACK_FRONTEND_CHAT
            placeholder = "message text"
        elif cart_mode:
            base = _FULLSTACK_FRONTEND_CART
            placeholder = item_verb.lower()
        else:
            base = _FULLSTACK_FRONTEND_COLLECTION
            placeholder = item_verb.lower() + " title"
        tokens = {
            "%NAME%": name,
            "%TITLE%": title,
            "%TAGLINE%": tagline,
            "%COLLECTION%": collection,
            "%ITEM_VERB%": item_verb,
            "%CART_LABEL%": cart_label,
            "%THEME%": theme,
            "%INPUT_PLACEHOLDER%": placeholder,
            "%BODY_PLACEHOLDER%": "Write the " + item_verb.lower() + " body...",
            "%PUBLIC_READ%": "true" if public_read else "false",
            "%API_BASE%": api_base,
        }
        for token, value in tokens.items():
            base = base.replace(token, value)
        return base

    def _react_frontend(self, spec, name, cart_mode, theme, api_port):
        """React + Vite SPA served from the backend at `/` (built to dist/)."""
        collection = spec["collection"]
        title = spec["title"]
        tagline = spec["tagline"]
        item_verb = spec["item_verb"]
        cart_label = spec["cart_label"]
        public_read = spec.get("public_read", False)
        tokens = {
            "%NAME%": name,
            "%TITLE%": title,
            "%TAGLINE%": tagline,
            "%COLLECTION%": collection,
            "%ITEM_VERB%": item_verb,
            "%CART_LABEL%": cart_label,
            "%THEME%": theme,
            "%BODY_PLACEHOLDER%": "Write the " + item_verb.lower() + " body...",
            "%PUBLIC_READ%": "true" if public_read else "false",
        }
        index = _REACT_INDEX
        app_jsx = _REACT_CART_JSX
        if collection == "tasks":
            app_jsx = _REACT_TASKS_JSX
        elif collection == "messages":
            app_jsx = _REACT_CHAT_JSX
        elif not cart_mode:
            app_jsx = _REACT_COLLECTION_JSX
        app_jsx = self._replace_react_tokens(app_jsx, tokens)
        app_jsx = app_jsx.replace("%REACT_BOOTSTRAP%", _REACT_BOOTSTRAP).replace("%REACT_CSS%", _REACT_CSS)
        app_jsx = self._replace_react_tokens(app_jsx, tokens)
        return {
            "frontend/package.json": _REACT_PACKAGE_JSON.replace("%NAME%", name),
            "frontend/vite.config.js": _REACT_VITE_CONFIG.replace("%API_PORT%", str(api_port)),
            "frontend/index.html": self._replace_react_tokens(index, tokens),
            "frontend/src/main.jsx": _REACT_MAIN,
            "frontend/src/App.jsx": app_jsx,
        }

    @staticmethod
    def _replace_react_tokens(text, tokens):
        for token, value in tokens.items():
            text = text.replace(token, value)
        return text

    def list_projects(self):
        if not os.path.isdir(self.output_dir):
            return []
        projects = []
        for name in sorted(os.listdir(self.output_dir)):
            path = os.path.join(self.output_dir, name)
            if os.path.isdir(path):
                files = []
                for root, _, fnames in os.walk(path):
                    for fn in fnames:
                        files.append(os.path.relpath(os.path.join(root, fn), path))
                projects.append({"name": name, "path": path, "files": files})
        return projects

    # ---------------------------------------------------------------
    # Deterministic app debugger (no LLM): static checks + safe repair
    # ---------------------------------------------------------------

    _KIND_ROUTE_HINTS = [
        ("/api/menu", "food_delivery"), ("/api/products", "ecommerce"), ("/api/services", "booking"),
        ("/api/tasks", "task_tracker"), ("/api/messages", "chat"), ("/api/posts", "blog"),
        ("/api/notes", "notes"), ("/api/workouts", "fitness"),
    ]

    def debug_app(self, name="", fix=False):
        """Hunt for bugs in a generated app deterministically and optionally
        repair them in place.

        Framework-aware: detects the backend (Flask app.py, Express/Fastify
        server.js, or Django manage.py) and frontend (single HTML file or
        React + Vite).

        Checks: leftover template tokens, syntax (py_compile / node --check),
        tables referenced by the backend but missing from the schema, seed
        targets, frontend routes that do not exist on the backend, and DB
        bootstrap.

        Repairs (only when fix=True, only when unambiguous):
          * a single unused declared table renamed to the single missing table
            the backend actually uses (e.g. bookings -> orders);
          * a missing `_init_db()` call inserted before the main guard;
          * a fully template-driven rebuild of a brain-generated app when
            consistency bugs remain (deterministic, same inputs -> same output).
        """
        folder = os.path.join(self.output_dir, _slug(name))
        backend_path = os.path.join(folder, "backend", "app.py")
        schema_path = os.path.join(folder, "backend", "schema.sql")
        frontend_path = os.path.join(folder, "frontend", "index.html")
        bugs, fixed = [], []
        report = {
            "ok": True, "bugs": bugs, "fixed": fixed,
            "bug_count": 0, "fixed_count": 0,
        }

        # ---- framework detection -------------------------------------------
        if os.path.exists(backend_path):
            framework, backend_file = "flask", "backend/app.py"
        elif os.path.exists(os.path.join(folder, "backend", "server.js")):
            framework, backend_file = "node", "backend/server.js"
            backend_path = os.path.join(folder, "backend", "server.js")
        elif os.path.exists(os.path.join(folder, "backend", "manage.py")):
            framework, backend_file = "django", "backend/manage.py"
            backend_path = os.path.join(folder, "backend", "manage.py")
        else:
            if not os.path.isdir(folder):
                bugs.append({"severity": "error", "location": name,
                             "message": f"No generated app '{name}' found (no backend/app.py, server.js or manage.py) — nothing to debug."})
            else:
                bugs.append({"severity": "error", "location": name,
                             "message": "No recognizable backend found (expected app.py, server.js or manage.py) — nothing to debug."})
            report["ok"] = False
            report["bug_count"] = 1
            return report

        is_react = os.path.isdir(os.path.join(folder, "frontend", "src"))
        frontend_files = ["frontend/index.html"]
        if is_react:
            frontend_files = ["frontend/index.html"] + sorted(
                f"frontend/src/{p}" for p in os.listdir(os.path.join(folder, "frontend", "src"))
            )

        def bug(severity, location, message):
            bugs.append({"severity": severity, "location": location, "message": message})

        backend = open(backend_path).read()
        schema = open(schema_path).read() if os.path.exists(schema_path) else ""
        if framework == "django":
            api_dir = os.path.join(folder, "backend", "api")
            for f in ("views", "models", "auth", "urls"):
                p = os.path.join(api_dir, f + ".py")
                if os.path.exists(p):
                    backend += "\n" + open(p).read()
        frontend = "\n".join(
            open(os.path.join(folder, f)).read()
            for f in frontend_files if os.path.exists(os.path.join(folder, f))
        )

        # ---- 1. leftover template tokens -----------------------------------
        if "{{" in backend:
            bug("error", backend_file, "Unresolved {{...}} template token left in generated backend.")
        if re.search(r"%[A-Z][A-Z_]*%", frontend):
            bug("error", "frontend/" + ("src/*" if is_react else "index.html"),
                "Unresolved %TOKEN% template token left in generated frontend.")

        # ---- 2. syntax -------------------------------------------------------
        if framework == "node":
            node_bin = os.environ.get("NODE_BIN", "node")
            import subprocess as _sp
            try:
                chk = _sp.run([node_bin, "--check", backend_path], capture_output=True, text=True, timeout=30)
            except Exception as e:
                bug("warning", backend_file, f"Could not run `node --check` (is Node installed?): {e}")
            else:
                if chk.returncode != 0:
                    bug("error", backend_file, "JavaScript syntax error: " + (chk.stderr or "").strip().splitlines()[-1][:160])
        else:
            try:
                compile(backend, backend_path, "exec")
            except SyntaxError as e:
                bug("error", f"{backend_file}:{e.lineno}", f"Python syntax error: {e.msg}.")

        # ---- 3. tables referenced by the backend must exist in the schema --
        sql_keywords = {"SET", "SELECT", "WHERE", "VALUES", "FROM", "AND", "OR", "NOT", "IN",
                        "LIKE", "LIMIT", "OFFSET", "ORDER", "BY", "ASC", "DESC", "GROUP",
                        "HAVING", "COUNT", "DISTINCT", "INTO", "JOIN", "UPDATE"}
        if framework == "django":
            declared = set(re.findall(r'db_table\s*=\s*"([a-zA-Z_][a-zA-Z0-9_]*)"', backend))
            referenced = set(re.findall(r"\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*)", backend))
        else:
            declared = set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?([a-zA-Z_][a-zA-Z0-9_]*)", schema))
            declared |= set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?([a-zA-Z_][a-zA-Z0-9_]*)", backend))
            referenced = set(re.findall(r"\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*)", backend))
            for const in ("COLLECTION_TABLE", "CATALOG_TABLE"):
                for m in re.finditer(const + r'\s*=\s*"([a-zA-Z_][a-zA-Z0-9_]*)"', backend):
                    referenced.add(m.group(1))
        referenced -= sql_keywords
        referenced.discard("sqlite_master")
        missing = sorted(t for t in referenced if t not in declared)
        unused = sorted(t for t in declared if t not in referenced)
        for t in missing:
            bug("error", backend_file,
                f"Backend uses table '{t}' but it is missing from schema.sql (declared: {', '.join(sorted(declared)) or 'none'}).")

        # ---- 4. seed targets -------------------------------------------------
        if framework != "django":
            for t in set(re.findall(r"INSERT OR IGNORE INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)", backend)):
                if t not in declared:
                    bug("error", backend_file, f"Seed data inserts into unknown table '{t}'.")

        # ---- 5. frontend routes that do not exist on the backend ------------
        back_routes = {}
        if framework == "flask":
            for m in re.finditer(r'@app\.(get|post|put|delete|patch)\("([^"]+)"', backend):
                back_routes.setdefault(_backend_segments(m.group(2)), set()).add(m.group(1).upper())
            for m in re.finditer(r'@app\.route\("([^"]+)",\s*methods=\[([^\]]*)\]', backend):
                methods = {x.strip().strip('"').strip("'").upper() for x in m.group(2).split(",") if x.strip()}
                back_routes.setdefault(_backend_segments(m.group(1)), set()).update(methods or {"GET"})
        elif framework == "node":
            verb = r"(?:get|post|put|delete|patch)"
            for m in re.finditer(r"\bapp\." + verb + r"\s*\(\s*['\"]([^'\"]+)['\"]", backend):
                back_routes.setdefault(_backend_segments(m.group(1)), set()).add(m.group(0).split(".")[-1].split("(")[0].upper())
        else:  # django: path() entries carry no method; match any
            for m in re.finditer(r'path\(\s*"([^"]+)",\s*views\.\w+', backend):
                if m.group(1).startswith("api/"):
                    back_routes.setdefault(_backend_segments(m.group(1)), set())
        seen_paths = set()
        for method, expr in _frontend_calls(frontend):
            segs = _frontend_segments(expr)
            key = tuple(segs)
            if key in seen_paths:
                continue
            seen_paths.add(key)
            matches = [rv for rv, methods in back_routes.items()
                       if _segments_match(segs, rv) and (method is None or method in methods or not methods)]
            if not matches:
                bug("warning", "frontend/" + ("src/*" if is_react else "index.html"),
                    f"Frontend calls {method or 'any'} {_display(expr)} but backend has no matching route.")

        # ---- 6. DB bootstrap ---------------------------------------------------
        if framework == "django":
            if "call_command(\"migrate\"" not in backend and "call_command('migrate'" not in backend \
                    and "run_syncdb" not in backend:
                bug("warning", "backend/manage.py", "Django app does not auto-run migrate/syncdb on startup.")
        elif framework == "node":
            if "initDb" not in backend:
                bug("error", "backend/server.js", "App defines no initDb() schema bootstrap.")
            elif re.search(r"initDb\(\)", backend) is None:
                bug("warning", "backend/server.js", "initDb() is defined but never called on startup.")
            if not schema and "CREATE TABLE" in backend:
                bug("error", "backend/schema.sql", "schema.sql is missing even though the app creates tables.")
        else:
            if "sqlite3" in backend:
                if "def _init_db(" not in backend:
                    bug("error", "backend/app.py", "App uses sqlite3 but defines no _init_db() schema bootstrap.")
                elif re.search(r"(?<!def )_init_db\(\)", backend) is None:
                    bug("warning", "backend/app.py", "_init_db() is defined but never called on startup.")
                if not schema:
                    bug("error", "backend/schema.sql", "schema.sql is missing even though the app uses SQLite.")

        report["ok"] = not any(b["severity"] == "error" for b in bugs)
        report["bug_count"] = len(bugs)

        # ---- repairs -----------------------------------------------------------
        if fix and bugs and framework != "django":
            # R1: single unused declared table -> rename to the single missing table
            if len(missing) == 1 and len(unused) == 1:
                wrong, right = unused[0], missing[0]
                before = open(schema_path).read() if os.path.exists(schema_path) else ""
                after = before.replace(
                    "CREATE TABLE IF NOT EXISTS " + wrong,
                    "CREATE TABLE IF NOT EXISTS " + right,
                )
                after = after.replace(
                    "CREATE TABLE " + wrong + " ",
                    "CREATE TABLE " + right + " ",
                )
                if after != before:
                    with open(schema_path, "w") as f:
                        f.write(after)
                    if "CREATE TABLE IF NOT EXISTS " + wrong in backend:
                        new_backend = backend.replace("CREATE TABLE IF NOT EXISTS " + wrong,
                                                      "CREATE TABLE IF NOT EXISTS " + right)
                        new_backend = new_backend.replace(" " + wrong + " ", " " + right + " ")
                        with open(backend_path, "w") as f:
                            f.write(new_backend)
                        backend = new_backend
                    fixed.append(f"Renamed unused table '{wrong}' to '{right}' in schema.sql and backend.")
                bugs[:] = [b for b in bugs if not b["message"].startswith("Backend uses table")]

            # R2: missing _init_db() call
            if "def _init_db(" in backend and re.search(r"(?<!def )_init_db\(\)", backend) is None:
                guard = re.search(r"\nif __name__ == \"__main__\":", backend)
                insert_at = guard.start() if guard else len(backend.rstrip())
                head, tail = backend[:insert_at], backend[insert_at:]
                new_backend = head + "\n\n_init_db()\n" + tail.lstrip("\n")
                with open(backend_path, "w") as f:
                    f.write(new_backend)
                backend = new_backend
                fixed.append("Inserted missing _init_db() call before the main guard.")

            # R3: template-driven rebuild of a brain-generated app if bugs remain
            if any(b["severity"] == "error" for b in bugs):
                if "# Auto-generated by the Aashu Virtual Brain" in backend:
                    kind = self._detect_app_kind(backend)
                    if kind is not None:
                        app_name = self._app_display_name(folder, name)
                        ok, msg = self.build_fullstack(name=app_name, kind=kind,
                                                       backend="node" if framework == "node" else "flask",
                                                       frontend="react" if is_react else "single",
                                                       theme="light")
                        if ok:
                            fixed.append(f"Rebuilt '{app_name}' from the {kind} template (deterministic repair).")
                            backend = open(backend_path).read()
                            bugs[:] = []
                            report["message"] = msg
        report["fixed_count"] = len(fixed)
        report["bug_count"] = len(bugs)
        report["ok"] = not any(b["severity"] == "error" for b in bugs)
        return report

    def _detect_app_kind(self, backend):
        for hint, kind in self._KIND_ROUTE_HINTS:
            if hint in backend:
                return kind
        return None

    def _app_display_name(self, folder, fallback):
        readme = os.path.join(folder, "README.md")
        if os.path.exists(readme):
            for line in open(readme):
                m = re.match(r"^#\s+(.+)$", line.strip())
                if m:
                    return _sanitize(m.group(1), fallback)
        return _sanitize(fallback, "My App")
