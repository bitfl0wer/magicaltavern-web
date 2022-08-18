import secrets
from pathlib import Path


def _ensurepaths() -> None:
    """_ensurepaths is called to ensure that the directory data/ and the file data/keys.txt exist."""
    Path("data/keys.txt").touch(exist_ok=True)


def validate(key: str) -> bool:
    """Check if the given key is a valid API key.

    Args:
        key (str): Key that is supposed to be checked

    Returns:
        bool: True if the key is a valid API key, False if not.
    """
    _ensurepaths()
    with open("data/keys.txt", mode="r", encoding="utf8") as keyfile:
        for line in keyfile:
            line = line.strip()
            if key == line:
                return True
    keyfile.close()
    return False


def generate() -> str:
    """Generate a cryptographically- and url-safe API token.

    Returns:
        str: Generated token.
    """
    return secrets.token_urlsafe(nbytes=48)


def put(key: str) -> None:
    """Put a new API key into the keys file. The put' key is a valid API key after.

    Args:
        key (str): API Key to be put in the keys file.
    """
    if len(key) <= 15:
        print("Consider using longer keys for safety!")
    with open("data/keys.txt", mode="a", encoding="utf8") as keyfile:
        keyfile.write(key)
        keyfile.write("\n")  # Newline, so that every key is put into a new line :3
    keyfile.close()
