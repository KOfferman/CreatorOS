from __future__ import annotations

import re

_HANDLE_PATTERN = re.compile(r"^[a-z0-9._]{3,30}$")


def normalize_user_handle(raw: str) -> str:
    value = raw.strip().lstrip("@").lower()
    if not _HANDLE_PATTERN.fullmatch(value):
        raise ValueError(
            "User must be 3–30 characters and use only letters, numbers, dots, or underscores."
        )
    return value


def format_user_handle(handle: str) -> str:
    return f"@{normalize_user_handle(handle)}"
