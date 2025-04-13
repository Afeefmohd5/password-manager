from cryptography.fernet import Fernet

# Generate a new key once and save it securely
def write_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Load key from file
def load_key():
    return open("secret.key", "rb").read()

# Encrypt password
def encrypt_password(password):
    key = load_key()
    return Fernet(key).encrypt(password.encode()).decode()

# Decrypt password
def decrypt_password(token):
    key = load_key()
    return Fernet(key).decrypt(token.encode()).decode()
