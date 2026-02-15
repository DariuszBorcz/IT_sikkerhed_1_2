# kun for at generere en gang SEKRET_KEY (.env),  ikke slettet med vilje

from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(key.decode())