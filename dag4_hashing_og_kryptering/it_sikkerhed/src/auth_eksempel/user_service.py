import json, re
from fastapi import HTTPException, status
from typing import List

from src.auth_eksempel.models import User, Role
from src.auth_eksempel.flat_file_loader import Flat_file_loader
from src.auth_eksempel.auth_service import Auth_service


class User_service:
    def __init__(self, database_file: str = "db_user_flat_file.json"):
        self._file_loader = Flat_file_loader(database_file)
        self._user_db:dict = {}
        self._load_database()

    # ----------- Private helpers -----------
    def _load_database(self):
        raw_data = self._file_loader.load_memory_database_from_file()

        if not raw_data:
            print("Warning: No database file found, creating one with default admin user.")
            self._create_default_admin()

        else: 
            for username, data in raw_data.items():
                try:
                    user = User(**data)
                    self._user_db[username] = user
                except Exception as e:
                    print(f"WARNING: Skipping invalid user entry '{username}': {e}")


    def _create_default_admin(self):
        admin_user = User(
            username="admin",
            password=Auth_service.hash_password("admin"),
            first_name=Auth_service.encrypt_data("admin_first_name"),
            last_name=Auth_service.encrypt_data("admin_last_name"),
            active=True,
            roles=[Role.admin],
        )
        self._user_db = {admin_user.username: admin_user}
        self._save_database()


    def _save_database(self):
        dict_db = {}
        for key, obj in self._user_db.items():
            dict_db[key] = obj.toDict()
        
        self._file_loader.save_memory_database_to_file(dict_db)

    def _check_if_email(self, username):
        if "@" in username and len(username)>=3:
            pass
        else:
            raise HTTPException(status_code=400, detail="Invalid email address")

    def _get_user(self, username: str):
        output = self._user_db[username]
        if(output == None):
            raise HTTPException(status_code=404, detail=f"User '{username}' not found in _user_db")
        return output

    def _user_has_at_least_one_role_for_access(self, username:str, accept_at_least_one_role: List[Role]):
        access = False
        user = self._get_user(username)
        for user_has_role in user.roles:
            for expected_role in accept_at_least_one_role:
                if(user_has_role == expected_role):
                    access = True
                    break
            if(access): # breaks second loop, when it is found
                break
        return access


    # ----------- Public methods -----------

    def register_user(self, username: str, password:str, first_name:str, last_name:str, roles: List[Role]):
        self._check_if_email(username)

        if username in self._user_db:
            raise HTTPException(status_code=400, detail="Username already exists")
        user = User(
            username = username,
            password = Auth_service.hash_password(password),
            first_name = Auth_service.encrypt_data(first_name),
            last_name = Auth_service.encrypt_data(last_name),
            active = True,
            roles = roles
        )
        self._user_db[user.username] = user
        self._save_database()
        return user

    def get_bearer_token(self, username: str, password: str):
        user = self._user_db.get(username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        if not Auth_service.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return Auth_service.get_bearer_token(user)   

    def deactivate_user(self, token: str, username_for_deactivation: str):
        payload = Auth_service.verify_token(token)
        username_who_makes_deactivation = payload["sub"]
        roles = list(payload["roles"])
        deactivate = False
        user_who_makes_deactivation = self._get_user(username_who_makes_deactivation)

        if(user_who_makes_deactivation.active == True):
            if self._user_has_at_least_one_role_for_access(username_who_makes_deactivation, [Role.admin]):
                deactivate = True

            elif self._user_has_at_least_one_role_for_access(username_who_makes_deactivation, [Role.user]):
                if username_who_makes_deactivation == username_for_deactivation:
                    deactivate = True 
            
        if deactivate:         
            user = self._get_user(username_for_deactivation)
            user.active = False
            self._save_database()
        else:
            raise HTTPException(status_code=403, detail="User don't have the privileges")

    def activate_user(self, token: str, username_for_activation: str):
        payload = Auth_service.verify_token(token)
        username_who_makes_activation = payload["sub"]
        roles = list(payload["roles"]),

        if self._user_has_at_least_one_role_for_access(username_who_makes_activation, [Role.admin]):
            user = self._get_user(username_for_activation)
            user.active = True
            self._save_database()
        else:
            raise HTTPException(status_code=403, detail="Admin privileges required")

