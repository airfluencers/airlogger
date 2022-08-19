from typing import Any, Dict


SANITIZED_FIELDS = [
    "password",
    "token",
    "access_token",
    "refresh_token",
    "auth_code"
]


def sanitize_body(data: Dict[str, Any]):
    for key in data:
        if key in SANITIZED_FIELDS:
            data[key] = "******"

    return data