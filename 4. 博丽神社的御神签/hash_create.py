import hashlib
import base64

password = "ctf123456"
salt = "shrineledger"
rounds = 240000

digest = hashlib.pbkdf2_hmac(
    "sha256",
    password.encode("utf-8"),
    salt.encode("utf-8"),
    rounds,
)

encoded = base64.urlsafe_b64encode(digest).decode().rstrip("=")
hash_text = f"$pbkdf2-sha256${rounds}${salt}${encoded}"
print(hash_text)