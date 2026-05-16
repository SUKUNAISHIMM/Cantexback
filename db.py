import psycopg
from psycopg.rows import dict_row
from config import DATABASE_URL

def db_connect():
    return psycopg.connect(DATABASE_URL, autocommit=True)

def fetch_active_accounts():
    with db_connect() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            SELECT id, name, operator_key, trading_key, auto_swap_enabled
            FROM accounts
            WHERE is_active = TRUE
        """)
        return list(cur.fetchall())

def fetch_swap_history(account_id: int):
    with db_connect() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            SELECT direction, input_amount, output_amount, status, executed_at
            FROM swap_history
            WHERE account_id = %s
            ORDER BY executed_at DESC
            LIMIT 50
        """, (account_id,))
        return list(cur.fetchall())

def fetch_global_gas_threshold():
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT gas_threshold FROM global_settings WHERE id = 1")
        row = cur.fetchone()
        return float(row[0]) if row and row[0] is not None else None
