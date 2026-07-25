"""Order persistence schema."""

ORDER_COLUMNS = ("id", "partner_id", "amount_cents", "created_at")


def create_table_sql() -> str:
    return (
        "CREATE TABLE orders ("
        "id TEXT PRIMARY KEY, partner_id TEXT NOT NULL, "
        "amount_cents INTEGER NOT NULL, created_at TEXT NOT NULL)"
    )
