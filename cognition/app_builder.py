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


# ---- helpers for the deterministic app debugger (route analysis) ----------

def _backend_segments(path):
    segs = [s for s in path.split("/") if s != ""]
    return tuple("{}" if (s == "{}" or s.startswith("<")) else s for s in segs)


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
        arg = _first_arg(text, m.end())
        if not re.search(r"['\"`]", arg):
            continue
        method = None
        window = text[m.end():m.end() + 300]
        mm = re.search(r"method\s*:\s*['\"]([A-Za-z]+)['\"]", window)
        if mm:
            method = mm.group(1).upper()
        calls.append((method, arg))
    for m in re.finditer(r"EventSource\(\s*(?:API\s*\+\s*)?(['\"`])(.*?)\1", text):
        calls.append(("GET", m.group(2)))
    return calls


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
# Production-shaped: SQLite (WAL) persistence, PBKDF2 password hashing,
# DB-backed sessions. Point DATABASE_PATH at a shared volume to run many
# gunicorn workers / app instances against one store.
import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_PATH = os.environ.get("DATABASE_PATH", str(Path(__file__).resolve().parent / "app.db"))


def get_db():
    db = sqlite3.connect(DB_PATH, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    return db


def _rows(db, sql, args=()):
    return [dict(r) for r in db.execute(sql, args).fetchall()]


def _one(db, sql, args=()):
    row = db.execute(sql, args).fetchone()
    return dict(row) if row else None


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
    db.execute("INSERT INTO sessions (token, username) VALUES (?, ?)", (token, username))
    return token


def _current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    with closing(get_db()) as db:
        row = db.execute(
            "SELECT username FROM sessions WHERE token = ?", (header[7:].strip(),)
        ).fetchone()
        return row["username"] if row else None


def _require_user():
    user = _current_user()
    if not user:
        return None
    return user


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
                "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                (username, salt, _hash_password(password, salt)),
            )
        except sqlite3.IntegrityError:
            return jsonify({"error": "Username already taken"}), 409
        token = _new_session(db, username)
    return jsonify({"token": token, "user": username}), 201


@app.post("/api/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    with closing(get_db()) as db:
        row = db.execute(
            "SELECT salt, password_hash FROM users WHERE username = ?", (username,)
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
            db.execute("DELETE FROM sessions WHERE token = ?", (header[7:].strip(),))
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
        db.execute("SELECT 1").fetchone()
    return jsonify({"status": "ok"})


def _init_db():
    with closing(get_db()) as db, db:
        db.executescript({{SCHEMA}})
        {{SEED_SQL}}


_init_db()
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
  const API = 'http://127.0.0.1:5000';
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
  const API = 'http://127.0.0.1:5000';
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
  const API = 'http://127.0.0.1:5000';
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
  const API = 'http://127.0.0.1:5000';
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

    def build_fullstack(self, name="My App", kind="food_delivery", theme="light"):
        """Build a complete, runnable full-stack vertical app (Flask REST
        backend + SQL schema + single-page frontend wired together).

        Gated on learned Python (Flask drives the backend)."""
        ok, lang, err = self._gate("python")
        if not ok:
            return False, err
        kind_key = _normalize_kind(kind)
        if kind_key is None:
            return False, (f"Unknown app kind '{kind}'. Available kinds: "
                           f"{', '.join(sorted(FULLSTACK_KINDS))}.")
        spec = FULLSTACK_KINDS[kind_key]
        name = _sanitize(name, "My App")
        slug = _slug(name)
        folder = self._project_path(name)
        theme = "dark" if str(theme).lower() == "dark" else "light"
        cart_mode = spec["mode"] == "cart"

        backend_py = self._fullstack_backend(spec, cart_mode)
        frontend_html = self._fullstack_frontend(spec, name, cart_mode, theme)
        files = {
            "backend/app.py": backend_py,
            "backend/requirements.txt": "flask>=3.0\ngunicorn>=21.0\n",
            "backend/schema.sql": spec["schema"],
            "backend/Dockerfile": (
                "FROM python:3.12-slim\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY app.py schema.sql .\n"
                "EXPOSE 8000\n"
                "CMD [\"gunicorn\", \"-w\", \"4\", \"-b\", \"0.0.0.0:8000\", \"app:app\"]\n"
            ),
            "docker-compose.yml": (
                "services:\n"
                "  web:\n"
                "    build: ./backend\n"
                "    ports:\n"
                "      - \"8000:8000\"\n"
                "    environment:\n"
                "      - DATABASE_PATH=/app/data/app.db\n"
                "    volumes:\n"
                "      - data:/app/data\n"
                "volumes:\n"
                "  data:\n"
            ),
            "frontend/index.html": frontend_html,
            "README.md": (
                f"# {name}\n\n{spec['title']} — {spec['tagline']}.\n\n"
                "## Run it (dev)\n\n"
                "1. `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`\n"
                "2. `python app.py`  (serves the API on :5000; creates SQLite `app.db` on first boot)\n"
                "3. Open `frontend/index.html` in a browser (serve it, e.g. `python -m http.server 8000`).\n\n"
                "## Run it (production-ish)\n\n"
                "Option A — gunicorn:\n\n"
                "`gunicorn -w 4 -b 0.0.0.0:8000 app:app` from the backend folder. "
                "Each worker serves the same SQLite store (WAL mode, busy timeout). "
                "Set `DATABASE_PATH` to a shared location to run multiple instances, and "
                "put a reverse proxy (nginx) in front for TLS.\n\n"
                "Option B — Docker:\n\n"
                "`docker compose up --build` from the project root (web on :8000, "
                "SQLite persisted in a named volume).\n\n"
                "State survives restarts: users, sessions, carts, orders and messages "
                "are persisted in `backend/app.db`. For very large scale, migrate the "
                "schema to PostgreSQL with SQLAlchemy.\n\n"
                "Generated deterministically by the Aashu Virtual Brain. No external LLM involved.\n"
            ),
        }
        for rel, content in files.items():
            full = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(content)
        return True, (
            f"Built full-stack '{spec['title']}' app '{name}' at {folder} "
            f"(Flask + gunicorn backend, SQLite persistence, auth, payments, "
            f"search + pagination, Docker deployment). "
            f"See README.md for run steps."
        )

    def _fullstack_backend(self, spec, cart_mode):
        collection = spec["collection"]
        item_verb = spec["item_verb"]
        schema_literal = json_dumps(spec["schema"])
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
            return (_FULLSTACK_BACKEND_CART
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SEED_SQL}}", seeds)
                    .replace("{{TABLE}}", table)
                    .replace("{{COLLECTION}}", collection)
                    .replace("{{ITEM_VERB}}", item_verb))
        if collection == "tasks":
            return (_FULLSTACK_BACKEND_TASKS
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SEED_SQL}}", ""))
        if collection == "messages":
            return (_FULLSTACK_BACKEND_MESSAGES
                    .replace("{{SCHEMA}}", schema_literal)
                    .replace("{{SEED_SQL}}", ""))
        return (_FULLSTACK_BACKEND_COLLECTION
                .replace("{{SCHEMA}}", schema_literal)
                .replace("{{SEED_SQL}}", "")
                .replace("{{TABLE}}", collection)
                .replace("{{COLLECTION}}", collection)
                .replace("{{PUBLIC_READ_CHECK}}", "False" if spec.get("public_read") else "True"))

    def _fullstack_frontend(self, spec, name, cart_mode, theme):
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
        }
        for token, value in tokens.items():
            base = base.replace(token, value)
        return base

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

        Checks: leftover template tokens, python syntax, tables referenced by
        the backend but missing from the schema, seed targets, frontend routes
        that do not exist on the backend, and missing DB bootstrap.

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
        if not os.path.isdir(folder) or not os.path.exists(backend_path):
            bugs.append({"severity": "error", "location": name,
                         "message": f"No generated app '{name}' found (no backend/app.py) — nothing to debug."})
            report["ok"] = False
            report["bug_count"] = 1
            return report

        def bug(severity, location, message):
            bugs.append({"severity": severity, "location": location, "message": message})

        backend = open(backend_path).read()
        schema = open(schema_path).read() if os.path.exists(schema_path) else ""
        frontend = open(frontend_path).read() if os.path.exists(frontend_path) else ""

        # ---- 1. leftover template tokens -----------------------------------
        if "{{" in backend:
            bug("error", "backend/app.py", "Unresolved {{...}} template token left in generated backend.")
        if re.search(r"%[A-Z][A-Z_]*%", frontend):
            bug("error", "frontend/index.html", "Unresolved %TOKEN% template token left in generated frontend.")

        # ---- 2. python syntax -----------------------------------------------
        try:
            compile(backend, backend_path, "exec")
        except SyntaxError as e:
            bug("error", f"backend/app.py:{e.lineno}", f"Python syntax error: {e.msg}.")

        # ---- 3. tables referenced by the backend must exist in the schema --
        sql_keywords = {"SET", "SELECT", "WHERE", "VALUES", "FROM", "AND", "OR", "NOT", "IN",
                        "LIKE", "LIMIT", "OFFSET", "ORDER", "BY", "ASC", "DESC", "GROUP",
                        "HAVING", "COUNT", "DISTINCT", "INTO", "JOIN", "UPDATE"}
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
            bug("error", "backend/app.py",
                f"Backend uses table '{t}' but it is missing from schema.sql (declared: {', '.join(sorted(declared)) or 'none'}).")

        # ---- 4. seed targets -------------------------------------------------
        for t in set(re.findall(r"INSERT OR IGNORE INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)", backend)):
            if t not in declared:
                bug("error", "backend/app.py", f"Seed data inserts into unknown table '{t}'.")

        # ---- 5. frontend routes that do not exist on the backend ------------
        back_routes = {}
        for m in re.finditer(r'@app\.(get|post|put|delete|patch)\("([^"]+)"', backend):
            back_routes.setdefault(_backend_segments(m.group(2)), set()).add(m.group(1).upper())
        for m in re.finditer(r'@app\.route\("([^"]+)",\s*methods=\[([^\]]*)\]', backend):
            methods = {x.strip().strip('"').strip("'").upper() for x in m.group(2).split(",") if x.strip()}
            back_routes.setdefault(_backend_segments(m.group(1)), set()).update(methods or {"GET"})
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
                bug("warning", "frontend/index.html",
                    f"Frontend calls {method or 'any'} {_display(expr)} but backend has no matching route.")

        # ---- 6. DB bootstrap ---------------------------------------------------
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
        if fix and bugs:
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
                        ok, msg = self.build_fullstack(name=app_name, kind=kind, theme="light")
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
