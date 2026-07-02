#!/usr/bin/env python3
"""Check which database the API uses and whether tables exist."""

from __future__ import annotations

import os
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
os.chdir(API_DIR)
sys.path.insert(0, str(API_DIR.parent / "shared" / "database"))

from sqlalchemy import inspect, text

from database import get_session_factory
from database.config import DatabaseSettings


def main() -> None:
    settings = DatabaseSettings()
    url = settings.database_url
    # Mask password in output
    display = url
    if "@" in url and "://" in url:
        prefix, rest = url.split("://", 1)
        if "@" in rest:
            creds, hostpart = rest.split("@", 1)
            display = f"{prefix}://***:***@{hostpart}"

    print(f"DATABASE_URL = {display}")

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            tables = inspect(session.bind).get_table_names()
            print(f"Connection: OK")
            print(f"Tables ({len(tables)}): {', '.join(tables) if tables else '(none)'}")
            if "users" in tables:
                count = session.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
                print(f"users rows: {count}")
    except Exception as exc:
        print(f"Connection: FAILED")
        print(f"Error: {exc}")
        print()
        print("Hostinger remote MySQL often blocks local connections.")
        print("Fix in hPanel → Databases → Remote MySQL → add your IP,")
        print("or create tables via phpMyAdmin using docs/schema.sql")
        sys.exit(1)


if __name__ == "__main__":
    main()
