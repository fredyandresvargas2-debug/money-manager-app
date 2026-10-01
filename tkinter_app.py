import hashlib
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "money_manager.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                limit_amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def register_user(username: str, password: str):
    username = username.strip()
    if not username or not password:
        raise ValueError("Usuario y contraseña son obligatorios.")

    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("El usuario ya existe.")
    finally:
        conn.close()


def login_user(username: str, password: str):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
        if row and row["password_hash"] == hash_password(password):
            return {"id": row["id"], "username": row["username"]}
        return None
    finally:
        conn.close()


def add_transaction(user_id: int, type_: str, category: str, amount: float, description: str = ""):
    if amount <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    if type_ not in ("income", "expense"):
        raise ValueError("El tipo debe ser 'income' o 'expense'.")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO transactions (user_id, type, category, amount, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, type_, category.strip(), float(amount), description.strip()),
        )
        conn.commit()
    finally:
        conn.close()


def add_budget(user_id: int, category: str, limit_amount: float):
    if limit_amount <= 0:
        raise ValueError("El límite debe ser mayor que cero.")

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM budgets WHERE user_id = ? AND lower(category) = lower(?)",
            (user_id, category.strip()),
        ).fetchone()
        if existing:
            raise ValueError("Ya existe un presupuesto para esa categoría.")

        conn.execute(
            "INSERT INTO budgets (user_id, category, limit_amount) VALUES (?, ?, ?)",
            (user_id, category.strip(), float(limit_amount)),
        )
        conn.commit()
    finally:
        conn.close()


def get_transactions(user_id: int):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, type, category, amount, description, created_at
            FROM transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_budgets(user_id: int):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, category, limit_amount FROM budgets WHERE user_id = ? ORDER BY category",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_summary(user_id: int):
    conn = get_connection()
    try:
        totals = conn.execute(
            """
            SELECT
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income_total,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense_total
            FROM transactions
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        income_total = totals["income_total"] or 0
        expense_total = totals["expense_total"] or 0
        balance = income_total - expense_total
        return {
            "income_total": float(income_total),
            "expense_total": float(expense_total),
            "balance": float(balance),
        }
    finally:
        conn.close()


def get_expenses_by_category(user_id: int):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE user_id = ? AND type = 'expense'
            GROUP BY category
            ORDER BY total DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


init_db()
