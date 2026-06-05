import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def decrypt_gemini_key(encrypted_str: str, secret: str) -> str:
    try:
        salt_hex, iv_hex, ciphertext_b64 = encrypted_str.split(":")
        
        salt = bytes.fromhex(salt_hex)
        iv = bytes.fromhex(iv_hex)
        ciphertext = base64.b64decode(ciphertext_b64)
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA1(), # CryptoJS uses SHA1 for PBKDF2 by default
            length=32,
            salt=salt,
            iterations=1000,
            backend=default_backend()
        )
        key = kdf.derive(secret.encode())
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return None
