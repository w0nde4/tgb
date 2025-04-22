import hashlib

def get_callback_data(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]