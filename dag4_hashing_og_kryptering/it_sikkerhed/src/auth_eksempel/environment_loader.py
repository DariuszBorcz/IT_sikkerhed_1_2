import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from src.colors import Colors

class Environment_loader:

    @staticmethod
    def load_environment_data():
        if os.getenv("APP_ENV") is None: # if this is not set, then load the test data environment file '.env'
            load_dotenv()

        environment_name = os.getenv("ENVIRONMENT_NAME")
        if(environment_name == "test"):
            print(f"{Colors.red}WARNING: Loading data .env file ({environment_name}){Colors.reset}")

        secret = os.getenv("HASH_KEY")
        if secret != None:
            secret = secret.encode()
        else:
            raise ValueError("HASH_KEY not found in environment or .env file")

        fernet = os.getenv("ENCRYPTION_KEY")
        if fernet != None:
           fernet = Fernet(fernet)
        else:
            raise ValueError("ENCRYPTION_KEY not found in environment or .env file")
        
        return secret, fernet