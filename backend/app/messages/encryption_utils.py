from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

KEY = os.environ.get("MESSAGE_ENCRYPTION_KEY", "my32lengthsupersecretnooneknows1").encode()

def encrypt_message(plaintext: str):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(KEY), modes.CFB(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return ciphertext, iv

def decrypt_message(ciphertext: bytes, iv: bytes):
    cipher = Cipher(algorithms.AES(KEY), modes.CFB(iv))
    decryptor = cipher.decryptor()
    return (decryptor.update(ciphertext) + decryptor.finalize()).decode()
