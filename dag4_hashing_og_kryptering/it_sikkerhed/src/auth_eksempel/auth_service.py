import hashlib, hmac, os, base64, datetime, jwt
from fastapi import HTTPException, status

from src.auth_eksempel.environment_loader import Environment_loader
from src.auth_eksempel.models import User, Role



class Auth_service:
    _algorithm = "HS256"

    _secret, _fernet = Environment_loader.load_environment_data()


    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16)  # unique salt for each password
        hashed = hmac.new(Auth_service._secret, salt + password.encode(), hashlib.sha256).digest()
        return base64.b64encode(salt + hashed).decode()

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        data = base64.b64decode(stored_hash.encode())
        salt = data[:16]
        stored_hmac = data[16:]
        new_hmac = hmac.new(Auth_service._secret, salt + password.encode(), hashlib.sha256).digest()
        return hmac.compare_digest(stored_hmac, new_hmac)

    @staticmethod
    def hmac_hash(password: str) -> str:
        return hmac.new(AuthService._secret, password.encode(), hashlib.sha256).hexdigest()


    # Symmetric enrcyption
    @staticmethod
    def encrypt_data(plaintext: str) -> str:
        token = Auth_service._fernet.encrypt(plaintext.encode())
        return token.decode()

    @staticmethod
    def decrypt_data(token: str) -> str:
        plaintext = Auth_service._fernet.decrypt(token.encode())
        return plaintext.decode()

    @staticmethod
    def get_bearer_token(user:User):
        payload = {
            "sub": user.username,  # subject (user ID)
            "roles": list(user.roles),
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),  # expires in 1 hour
            "iat": datetime.datetime.now(datetime.UTC),  # issued at
        }

        token = jwt.encode(payload, Auth_service._secret, algorithm=Auth_service._algorithm)

        return f"Bearer {token}"

    @staticmethod
    def verify_token(token: str):
        token_data = token.split()[1]
        try:
            payload = jwt.decode(token_data, Auth_service._secret, algorithms=[Auth_service._algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    