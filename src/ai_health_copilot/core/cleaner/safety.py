from pathlib import Path

SENSITIVE_KEYWORDS = (
    "login data",
    "cookies",
    "web data",
    "preferences",
    "local state",
    "logins.json",
    "key4.db",
    "formhistory.sqlite",
    "permissions.sqlite",
    "signons.sqlite",
    "bookmarks",
    "autofill",
    "credit card",
    "password",
    "passwords",
    "keychain",
    "secret",
    "credentials",
    ".key",
    ".pem",
    ".pfx",
)


def is_sensitive_path(path: str | Path) -> bool:
    """Returns True when a path must never be deleted (passwords, autofill,
    cookies, login credentials or encryption keys)."""
    name = Path(path).name.lower()
    return any(keyword in name for keyword in SENSITIVE_KEYWORDS)
