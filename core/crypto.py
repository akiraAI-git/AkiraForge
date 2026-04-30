from __future__ import annotations
import os
from typing import Tuple
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def derive_key(passphrase: str, salt: bytes, iterations: int = 200_000) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(passphrase.encode())

def encrypt_bytes(key: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    return nonce, ct

def decrypt_bytes(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None)

def encrypt_text(key: bytes, text: str) -> Tuple[bytes, bytes]:
    return encrypt_bytes(key, text.encode('utf-8'))

def decrypt_text(key: bytes, nonce: bytes, ciphertext: bytes) -> str:
    return decrypt_bytes(key, nonce, ciphertext).decode('utf-8')
