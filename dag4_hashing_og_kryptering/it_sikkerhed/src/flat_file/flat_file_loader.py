import json  # Modul til at læse og skrive JSON-filer (JavaScript Object Notation)
import os  # Modul til operativsystem-funktioner (fil/mappe operationer)
from dataclasses import asdict  # Konverterer dataclass objekt til dictionary (bruges til User → dict)
from pathlib import Path  # Moderne måde at håndtere filstier på (bedre end string paths)
from typing import List, Optional  # Type hints: List[User] = liste af User objekter, Optional = kan være None

from src.flat_file.user import User   # Importerer User dataclass (antager den findes i src/flat_file/user.py)

class Flat_file_loader:
    """Håndterer læsning og skrivning af brugere til/fra en JSON flat-file."""
    
    def __init__(self, database_file_name: str = "db_flat_file.json"):
        """
        Initialiserer loader med given filnavn.
        
        Args:
            database_file_name: Sti til JSON-filen (relativ eller absolut)
        """
        # Konverter string sti til Path objekt (giver bedre metoder som .is_file(), .parent, etc.)
        self.database_file_name = Path(database_file_name)
        
        # Sørg for at mappen findes (hvis relativ sti)
        # .parent = parent directory (f.eks. hvis fil er "data/users.json", parent = "data")
        # .mkdir() = create directory
        # parents=True = lav også parent directories hvis de ikke findes
        # exist_ok=True = giv IKKE fejl hvis mappen allerede findes
        self.database_file_name.parent.mkdir(parents=True, exist_ok=True)
    
    def load_memory_database_from_file(self) -> List[User]:
        """
        Indlæser brugere fra JSON-filen og returnerer som liste af User-objekter.
        
        Returns:
            Liste af User-instanser. Tom liste hvis fil ikke findes eller er ugyldig.
        """
        # Tjek om filen findes (is_file() returnerer True/False)
        if not self.database_file_name.is_file():
            # INFO log: Filen findes ikke, så vi starter med tom database
            print(f"INFO: Database-fil '{self.database_file_name}' findes ikke – starter med tom database.")
            return []  # Returner tom liste (ingen brugere)
        
        try:
            # Åbn filen i read mode ("r") med UTF-8 encoding (støtter danske tegn: æ, ø, å)
            with self.database_file_name.open("r", encoding="utf-8") as f:
                # json.load() læser filen og parser JSON til Python dict
                data = json.load(f)
                
                # Hent "users" nøglen fra dict, hvis den ikke findes returner [] (tom liste)
                # Forventet format: {"users": [{"person_id": 0, "first_name": "John", ...}, ...]}
                user_dicts = data.get("users", [])
                
                # List comprehension: Lav User objekt for hver dict i listen
                # **user_dict = unpacking af dict til keyword arguments
                # f.eks. User(**{"person_id": 0, "first_name": "John"}) → User(person_id=0, first_name="John")
                return [User(**user_dict) for user_dict in user_dicts]
                
        except json.JSONDecodeError as e:
            # Specifik fejl: JSON filen er korrupt (ugyldig syntax)
            # f.eks. manglende komma, forkert bracket, etc.
            print(f"FEJL: JSON korrupt i '{self.database_file_name}': {e}")
            return []  # Returner tom liste i stedet for at crashe
            
        except Exception as e:
            # Generel fejl: Alt andet (fil permissions, disk fuld, etc.)
            print(f"Uventet fejl ved læsning af '{self.database_file_name}': {e}")
            return []  # Returner tom liste i stedet for at crashe
    
    def save_memory_database_to_file(self, users: List[User]) -> None:
        """
        Gemmer liste af User-objekter til JSON-filen (serialiseret via asdict).
        
        Args:
            users: Liste af User-instanser der skal gemmes
        """
        try:
            # Byg dict struktur til JSON fil
            # asdict(user) konverterer User dataclass til dict
            # f.eks. User(person_id=0, first_name="John") → {"person_id": 0, "first_name": "John"}
            # List comprehension laver dette for ALLE users i listen
            serializable_data = {
                "users": [asdict(user) for user in users]
            }
            
            # Åbn filen i write mode ("w") - OVERSKRIVER eksisterende indhold!
            # UTF-8 encoding for at supportere danske tegn
            with self.database_file_name.open("w", encoding="utf-8") as f:
                # json.dump() skriver Python dict til fil som JSON
                json.dump(
                    serializable_data,  # Data der skal skrives
                    f,  # File handle (åben fil)
                    indent=2,  # Pretty print med 2 spaces indrykning (læsbart for mennesker)
                    ensure_ascii=False,  # Tillad unicode tegn (æ, ø, å) i stedet for \u escape sequences
                    sort_keys=False   # Bevar rækkefølge af keys (standard er False i Python 3.7+)
                )
            
            # Success log: Fortæl hvor mange brugere blev gemt
            print(f"INFO: Gemt {len(users)} brugere til '{self.database_file_name}'")
            
        except Exception as e:
            # Generel fejl: Disk fuld, permissions, etc.
            print(f"FEJL: Kunne ikke gemme database til '{self.database_file_name}': {e}")
            raise  # Re-raise exception så caller ved at save fejlede (eller bare logge – afhænger af dit projekt)