#!/usr/bin/env python3
"""Run Alembic migrations using api/.env and api/.env.local."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_DIR = API_DIR.parent / "shared" / "database"
VENV_ALEMBIC = API_DIR / ".venv" / "bin" / "alembic"


def main() -> None:
    if not VENV_ALEMBIC.exists():
        print("Missing api/.venv — create it and install requirements first.")
        sys.exit(1)

    env = os.environ.copy()
    result = subprocess.run(
        [str(VENV_ALEMBIC), "upgrade", "head"],
        cwd=ALEMBIC_DIR,
        env=env,
        check=False,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
