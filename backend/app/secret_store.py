from __future__ import annotations

import base64
import hashlib
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from .config import settings


SECRET_STORE_VERSION = 1
SECRET_STORE_SCHEME = 'fernet-sha256-secret-key'


def _fernet() -> Fernet:
    source = str(settings.SECRET_KEY or 'dev-secret-change-me').encode('utf-8')
    key = base64.urlsafe_b64encode(hashlib.sha256(source).digest())
    return Fernet(key)


def protect_secret(value: str) -> dict[str, Any]:
    """Protect a runtime secret for durable storage."""
    secret = str(value or '').strip()
    if not secret:
        return {}
    token = _fernet().encrypt(secret.encode('utf-8')).decode('ascii')
    return {
        'version': SECRET_STORE_VERSION,
        'scheme': SECRET_STORE_SCHEME,
        'ciphertext': token,
    }


def reveal_secret(payload: Any) -> str:
    """Reveal a protected secret; legacy plaintext strings still migrate."""
    if not payload:
        return ''
    if isinstance(payload, str):
        return payload.strip()
    if not isinstance(payload, dict):
        return ''
    ciphertext = str(payload.get('ciphertext') or '')
    if not ciphertext:
        return ''
    try:
        return _fernet().decrypt(ciphertext.encode('ascii')).decode('utf-8')
    except (InvalidToken, UnicodeDecodeError, ValueError):
        return ''


def mask_secret(value: str) -> str:
    secret = str(value or '')
    if len(secret) <= 8:
        return '*' * len(secret)
    return secret[:4] + '...' + secret[-4:]
