#!/usr/bin/env python3
"""Create tables and seed data on the configured MySQL database."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
ROOT = API_DIR.parent
os.chdir(API_DIR)
sys.path.insert(0, str(ROOT / "shared" / "database"))

from sqlalchemy import create_engine, inspect, text

from database.config import DatabaseSettings


def _split_sql(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    # Strip line comments; keep statements intact.
    lines = [line for line in raw.splitlines() if not line.strip().startswith("--")]
    body = "\n".join(lines)
    parts = re.split(r";\s*\n", body)
    return [p.strip() for p in parts if p.strip()]


def main() -> None:
    settings = DatabaseSettings()
    if "sqlite" in settings.database_url:
        print("DATABASE_URL points to SQLite. Use your MySQL URL in api/.env.local")
        sys.exit(1)

    schema_path = ROOT / "docs" / "schema.sql"
    seed_path = ROOT / "docs" / "seed_data.sql"
    if not schema_path.exists() or not seed_path.exists():
        print("Missing docs/schema.sql or docs/seed_data.sql")
        sys.exit(1)

    print(f"Connecting to {settings.database_url.split('@')[-1]} ...")
    engine = create_engine(settings.database_url, pool_pre_ping=True)

    with engine.begin() as conn:
        before = inspect(conn).get_table_names()
        print(f"Tables before: {before or '(none)'}")

        print("Applying schema...")
        for stmt in _split_sql(schema_path):
            conn.execute(text(stmt))

        print("Applying seed data...")
        for stmt in _split_sql(seed_path):
            conn.execute(text(stmt))

        after = inspect(conn).get_table_names()

    print(f"Tables after ({len(after)}): {', '.join(after)}")
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Bootstrap failed: {exc}")
        sys.exit(1)
