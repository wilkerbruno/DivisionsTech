"""
security.py — Hashing de senha usando bcrypt diretamente
Compatível com Python 3.10, 3.11, 3.12, 3.13 e 3.14
Usa bcrypt diretamente, compatível com Python 3.14.
"""

import bcrypt


def hash_password(plain: str) -> str:
    """Gera hash bcrypt da senha."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha contra hash bcrypt."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))