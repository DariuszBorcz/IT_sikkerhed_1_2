from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel

from src.http_eksempel_4.flat_file_loader import Flat_file_loader
from src.http_eksempel_4.person import Person

class Rest_api:
    def __init__(self, database_file_name: str = "db_flat_file.json"):
        self.flate_file_loader = Flat_file_loader(database_file_name)
        self.in_memory_database : dict[str, dict] = {}

        self.app = FastAPI()
        self.app.add_event_handler("startup", self.on_startup)

        self.app.post("/person")(self.create_person)
        self.app.get("/person")(self.read_person_invalid)
        self.app.get("/person/{person_id}")(self.read_person)


    def on_startup(self):
        self.in_memory_database = self.flate_file_loader.load_memory_database_from_file()

    def create_person(self, person_id: str = Form(...), navn: str = Form(...), alder: int = Form(...)):
        self.in_memory_database[person_id] = {"person_id": person_id, "navn": navn, "alder": alder}
        self.flate_file_loader.save_memory_database_to_file(self.in_memory_database)
        return {
            "header": {"status": "gemt", "code": 200},
            "body": self.in_memory_database[person_id],
        }

    def read_person_invalid(self):
        raise HTTPException(status_code=400, detail="path skal være /person/<person_id>")

    def read_person(self, person_id: str):
        if person_id not in self.in_memory_database:
            raise HTTPException(status_code=404, detail=f"Person med id '{person_id}' findes ikke")
        return {
            "header": {"status": "ok", "code": 200},
            "body": self.in_memory_database[person_id],
        }