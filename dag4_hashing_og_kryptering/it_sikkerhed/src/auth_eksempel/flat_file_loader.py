import os, json
from src.auth_eksempel.models import User

class Flat_file_loader:
    def __init__(self, database_file_name: str = "db_user_flat_file.json"):
        self.database_file_name = database_file_name

    def load_memory_database_from_file(self):
        in_meomery_database = {}
        try:
           with open(self.database_file_name, "r", encoding="utf-8") as f:
                in_meomery_database = json.load(f)
        except:
            print(f"WARNING: file '{self.database_file_name}' don't exist or is corrupt")
        return in_meomery_database

    def save_memory_database_to_file(self, in_meomery_database):
        with open(self.database_file_name, "w", encoding="utf-8") as f:
            json.dump(in_meomery_database, f, indent=2, ensure_ascii=False)