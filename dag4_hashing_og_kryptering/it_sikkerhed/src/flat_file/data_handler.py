import os  # Operativsystem modul til at tilgå environment variables (SECRET_KEY fra .env)
import gc  # Garbage Collector - Python's automatiske memory management (bruges i clear_memory())
from typing import Optional  # Type hint: Optional[User] betyder "User eller None"

from cryptography.fernet import Fernet, InvalidToken  # Fernet = symmetrisk kryptering (AES-128 CBC), InvalidToken = exception når dekryptering fejler
import bcrypt  # Industry standard password hashing library (slow by design mod brute-force)
from dotenv import load_dotenv  # Loader environment variables fra .env fil (SECRET_KEY)

from src.flat_file.user import User  # User dataclass med felter: person_id, first_name, last_name, etc.
from src.flat_file.flat_file_loader import Flat_file_loader  # Håndterer JSON fil læsning/skrivning

load_dotenv()  #TILFØJET: Læs .env fil og load SECRET_KEY into os.environ

# Hent SECRET_KEY fra environment variables (.env fil)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Hvis SECRET_KEY mangler, crash med ValueError (bedre end at fortsætte med None)
    raise ValueError("SECRET_KEY mangler i .env – se README eller generer med Fernet.generate_key()")

# Initialiser Fernet med SECRET_KEY (encode() konverterer string → bytes, som Fernet kræver)
fernet = Fernet(SECRET_KEY.encode())  #TILFØJET: Global Fernet instance til kryptering/dekryptering


class Data_handler:
    # FJERNET: users = []  #ÆNDRET: Class-level variable fjernet - skaber problemer med delte instances
    # Hvis users var class-level, ville ALLE Data_handler instances dele samme liste (session hijacking risk!)

    def __init__(self, flat_file_name: str = "users.json"):
        """
        Initialiserer Data_handler med en JSON database fil.
        
        Args:
            flat_file_name: Sti til JSON fil (default: "users.json")
        
        Workflow:
            1. Opret Flat_file_loader til at håndtere JSON I/O
            2. Initialiser tom users liste (instance-level, ikke class-level!)
            3. Load brugere fra fil og dekrypter dem til memory
        """
        self.flat_file_loader = Flat_file_loader(flat_file_name)  # Håndterer JSON læsning/skrivning
        self.users: list[User] = []  # Instance-level liste (hver Data_handler har sin egen liste) - Type hint: list[User]
        self._load_and_decrypt_all()  #TILFØJET: GDPR-compliance - data dekrypteres kun i memory (ikke gemt krypteret i RAM hele tiden)

    def _load_and_decrypt_all(self) -> None:
        """
        Indlæser alle brugere fra fil og dekrypterer persondata.
        
        Workflow:
            1. Load krypteret data fra JSON fil via flat_file_loader
            2. For hver bruger: dekrypter persondata (first_name, last_name, address, street_number)
            3. Password forbliver hashet (passwords ALDRIG dekrypteres - de er enveis hashed!)
            4. Append dekrypteret bruger til self.users (memory er nu plaintext for performance)
        
        Error handling:
            - InvalidToken: Hvis kryptering er korrupt, skip brugeren (log fejl)
            - Exception: Generel fejl (log og skip)
        """
        # Load rå (krypteret) data fra fil - returnerer liste af User objekter med krypteret data
        raw_users = self.flat_file_loader.load_memory_database_from_file()
        self.users = []  # Reset users liste (sikre vi starter fra tom liste)

        # Iterer over hver rå (krypteret) bruger
        for raw in raw_users:
            try:
                # Opret ny User med DEKRYPTERET data (plaintext i memory for performance)
                decrypted = User(
                    person_id=raw.person_id,  # ID røres ikke (ikke sensitiv data)
                    first_name=self._decrypt(raw.first_name),  # Dekrypter fornavn (gAAAAA... → "John")
                    last_name=self._decrypt(raw.last_name),  # Dekrypter efternavn
                    address=self._decrypt(raw.address),  # Dekrypter adresse
                    street_number=self._safe_int_decrypt(raw.street_number),  # Dekrypter og konverter til int
                    password=raw.password,  # Password forbliver hashet ($2b$12$...) - ALDRIG dekrypteres!
                    enabled=raw.enabled  # Boolean røres ikke
                )
                self.users.append(decrypted)  # Tilføj dekrypteret bruger til memory liste
                
            except InvalidToken:
                # Specifik exception: Fernet dekryptering fejlede (korrupt data eller forkert SECRET_KEY)
                print(f"Ugyldig kryptering for bruger ID {raw.person_id} – skipper")
                # Skip denne bruger og fortsæt med næste (graceful degradation)
                
            except Exception as e:
                # Generel exception: Alt andet (uventet fejl)
                print(f"Fejl ved dekryptering af bruger {raw.person_id}: {e}")
                # Skip denne bruger og fortsæt

    def _safe_int_decrypt(self, val: any) -> int:
        """
        Dekrypter og konvertér til int – med fallback.
        
        Args:
            val: Krypteret værdi (kan være string eller allerede int)
        
        Returns:
            Integer værdi (0 hvis konvertering fejler)
        
        Hvorfor nødvendig?
            street_number gemmes som krypteret STRING i fil ("gAAAAA...")
            Men vi skal bruge det som INT i memory (42)
        """
        # Dekrypter først (returnerer string) - konverter til string først hvis det er int
        decrypted_str = self._decrypt(str(val))
        
        try:
            # Konverter string → int ("42" → 42)
            return int(decrypted_str)
        except ValueError:
            # Hvis dekryptering gav ugyldig int string (f.eks. "abc" kan ikke konverteres til int)
            print(f"street_number dekrypteret til ugyldigt tal: {decrypted_str}")
            return 0  # Fallback til 0 (eller raise ValueError afhængig af krav)

    def _decrypt(self, val: any) -> str:
        """
        Dekrypterer en værdi – returnerer original hvis allerede plaintext.
        
        Args:
            val: Værdi der skal dekrypteres (kan være krypteret eller plaintext)
        
        Returns:
            Dekrypteret string (plaintext)
        
        Hvorfor try-except InvalidToken?
            Ved første load er data krypteret → dekrypter med Fernet
            Ved create_user() er data allerede plaintext → returnér som-is
            InvalidToken exception betyder data er IKKE Fernet-krypteret → returnér original
        """
        # Tjek om værdien er en ikke-tom string
        if not isinstance(val, str) or not val.strip():
            # Hvis val er None, tom string, eller ikke en string → konverter til string
            return str(val) if val is not None else ""
        
        try:
            # Prøv at dekryptere med Fernet
            # .encode() konverterer string → bytes (Fernet kræver bytes)
            # fernet.decrypt() returnerer bytes → .decode("utf-8") konverterer til string
            return fernet.decrypt(val.encode()).decode("utf-8")
            
        except InvalidToken:
            # Data er IKKE Fernet-krypteret (allerede plaintext) → returnér original
            return val  # antag plaintext (TILFØJET: mere robust end string-tjek med "gAAAAA")
            
        except Exception as e:
            # Anden uventet fejl (disk fejl, memory problem, etc.)
            print(f"Dekrypteringsfejl: {e}")
            return val  # Returnér original værdi som fallback

    def _encrypt(self, val: any) -> str:
        """
        Krypter en værdi til Fernet-streng.
        
        Args:
            val: Værdi der skal krypteres (kan være string, int, etc.)
        
        Returns:
            Fernet-krypteret string (f.eks. "gAAAAABpi16L...")
        
        Raises:
            RuntimeError: Hvis kryptering fejler (disk fuld, memory problem)
        
        Hvorfor konvertere til string først?
            Fernet kræver bytes input
            Vi konverterer: int/string → string → bytes → kryptér → bytes → string
        """
        if val is None:
            # Hvis værdien er None, returnér tom string (undgå "None" string)
            return ""
        
        try:
            # Konverter til string → bytes → kryptér → bytes → string
            # str(val) håndterer både int og string input
            # .encode("utf-8") konverterer string → bytes
            # fernet.encrypt() krypterer bytes → returnerer bytes
            # .decode("utf-8") konverterer bytes → string
            return fernet.encrypt(str(val).encode("utf-8")).decode("utf-8")
            
        except Exception as e:
            # Hvis kryptering fejler, raise RuntimeError (kritisk fejl!)
            raise RuntimeError(f"Krypteringsfejl: {e}")

    def _save(self) -> None:
        """
        Krypter alle brugere og skriv til fil.
        
        Workflow:
            1. Iterer over self.users (plaintext i memory)
            2. For hver bruger: krypter persondata (first_name, last_name, address, street_number)
            3. Password forbliver hashet (passwords ALDRIG krypteres igen - allerede hashet!)
            4. Opret nye User objekter med KRYPTERET data
            5. Gem krypterede brugere til JSON fil via flat_file_loader
        
        Hvorfor ikke kryptere password?
            Passwords er HASHET (bcrypt) - enveis transformation
            Hashing != Kryptering (hash kan ikke dekrypteres)
            Vi gemmer bcrypt hash både i memory og fil ($2b$12$...)
        """
        # List comprehension: Opret liste af User objekter med KRYPTERET data
        encrypted_users = [
            User(
                person_id=u.person_id,  # ID krypteres ikke (ikke sensitiv)
                first_name=self._encrypt(u.first_name),  # "John" → "gAAAAABpi16L..."
                last_name=self._encrypt(u.last_name),  # "Doe" → "gAAAAABpi16L..."
                address=self._encrypt(u.address),  # "Main Street" → "gAAAAABpi16L..."
                street_number=self._encrypt(u.street_number),  # 42 → "gAAAAABpi16L..."
                password=u.password,  # hashes røres ikke (allerede $2b$12$...)
                enabled=u.enabled  # Boolean krypteres ikke
            )
            for u in self.users  # Iterer over plaintext brugere i memory
        ]
        # Gem krypterede brugere til JSON fil (encryption at rest!)
        self.flat_file_loader.save_memory_database_to_file(encrypted_users)

    # ────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────

    def get_number_of_users(self) -> int:
        """
        Returnerer antal brugere i databasen.
        
        Returns:
            Antal brugere (int)
        
        Simpel metode - returner længde af self.users liste
        """
        return len(self.users)

    def get_user_by_id(self, uid: int) -> Optional[User]:
        """
        Find bruger med specifik ID.
        
        Args:
            uid: User ID (person_id)
        
        Returns:
            User objekt hvis fundet, None hvis ikke fundet
        
        Linear search: O(n) kompleksitet (OK for small datasets)
        Production: Overvej dict lookup for O(1) kompleksitet
        """
        # Iterer over alle brugere (linear search)
        for u in self.users:
            if u.person_id == uid:
                return u  # Fundet! Returnér User objekt
        return None  # Ikke fundet - returnér None

    def create_user(
        self,
        first_name: str,
        last_name: str,
        address: str,
        street_number: int,
        password: str,
    ) -> None:
        """
        Opret ny bruger med kryptering og password hashing.
        
        Args:
            first_name: Fornavn (plaintext input)
            last_name: Efternavn (plaintext input)
            address: Adresse (plaintext input)
            street_number: Husnummer (int)
            password: Password (plaintext input) - ALDRIG gem plaintext password!
        
        Workflow:
            1. Generér nyt user ID (baseret på liste længde)
            2. Hash password med bcrypt (plaintext → $2b$12$...)
            3. Opret User objekt med PLAINTEXT data (memory)
            4. Append til self.users
            5. Save til fil (kryptering sker i _save())
        
        Sikkerhed:
            - Password hashet med bcrypt (salt + work factor 12)
            - Persondata gemmes plaintext i memory (performance)
            - Data krypteres ved save til disk (encryption at rest)
        """
        uid = len(self.users)  # Nyt ID = nuværende antal brugere (0, 1, 2, ...)
        enabled = True  # Nye brugere er enabled by default
        
        # Hash password (IKKE krypter - passwords hashes, ikke krypteres)  #TILFØJET KOMMENTAR
        # bcrypt.hashpw() tager plaintext password og genererer hash
        # .encode("utf-8") konverterer string → bytes (bcrypt kræver bytes)
        # bcrypt.gensalt() genererer tilfældig salt (22 tegn) - hver hash er unik!
        # .decode("utf-8") konverterer bytes hash → string (til User objekt)
        # Resultat: "secret" → "$2b$12$C7cFNEbtVPW4O1iN/RXW0OoOb5M5yaBASN731Lqj.TPePZHKRCO0K"
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Gem DEKRYPTERET i memory - kryptering sker kun ved save til fil  #TILFØJET KOMMENTAR
        # Opret User objekt med PLAINTEXT data (first_name="John", ikke "gAAAAA...")
        # Hvorfor plaintext? Performance - application layer kan arbejde direkte med data
        user = User(uid, first_name, last_name, address, street_number, password_hash, enabled)
        self.users.append(user)  # Tilføj til memory liste (plaintext)
        
        # Krypter kun når vi gemmer til fil  #TILFØJET KOMMENTAR
        # _save() krypterer persondata før skrivning til disk
        self._save()

    def disable_user(self, uid: int) -> None:
        """
        Deaktiver bruger (sæt enabled=False).
        
        Args:
            uid: User ID
        
        Sikkerhedsanvendelse:
            Deaktiverede brugere kan ikke logge ind
            Men data forbliver i database (ikke slettet)
            Kan genaktiveres med enable_user()
        """
        user = self.get_user_by_id(uid)
        if user:
            user.enabled = False  # Deaktiver brugeren
            self._save()  # ÆNDRET: brug centraliseret save-metode (persist til disk)

    def enable_user(self, uid: int) -> None:
        """
        Genaktiver bruger (sæt enabled=True).
        
        Args:
            uid: User ID
        """
        user = self.get_user_by_id(uid)
        if user:
            user.enabled = True  # Genaktiver brugeren
            self._save()  # ÆNDRET: brug centraliseret save-metode

    def update_first_name(self, uid: int, new_first_name: str) -> bool:
        """
        Opdater brugerens fornavn.
        
        Args:
            uid: User ID
            new_first_name: Nyt fornavn (plaintext)
        
        Returns:
            True hvis success, False hvis bruger ikke findes
        
        Workflow:
            1. Find bruger med ID
            2. Opdater first_name (plaintext i memory)
            3. Save til disk (_save() krypterer automatisk)
        """
        user = self.get_user_by_id(uid)
        if not user:
            return False  # Bruger ikke fundet - returnér False
        user.first_name = new_first_name  #ÆNDRET: gem dekrypteret (ikke krypter her) - opdater plaintext i memory
        self._save()  # ÆNDRET: brug centraliseret save-metode (kryptering sker her)
        return True  # Success!

    def update_last_name(self, uid: int, new_last_name: str) -> bool:
        """Opdater brugerens efternavn."""
        user = self.get_user_by_id(uid)
        if not user:
            return False
        user.last_name = new_last_name  #ÆNDRET: gem dekrypteret (ikke krypter her)
        self._save()  # ÆNDRET: brug centraliseret save-metode (kryptering sker her)
        return True

    def update_address(self, uid: int, new_address: str) -> bool:
        """Opdater brugerens adresse."""
        user = self.get_user_by_id(uid)
        if not user:
            return False
        user.address = new_address  #ÆNDRET: gem dekrypteret (ikke krypter her)
        self._save()  # ÆNDRET: brug centraliseret save-metode (kryptering sker her)
        return True

    def update_street_number(self, uid: int, new_street_number: int) -> bool:
        """Opdater brugerens husnummer."""
        user = self.get_user_by_id(uid)
        if not user:
            return False
        user.street_number = new_street_number  #ÆNDRET: gem dekrypteret (ikke krypter her)
        self._save()  # ÆNDRET: brug centraliseret save-metode (kryptering sker her)
        return True

    def update_password(self, uid: int, new_password: str) -> bool:
        """
        Opdater brugerens password med ny bcrypt hash.
        
        Args:
            uid: User ID
            new_password: Nyt password (plaintext input)
        
        Returns:
            True hvis success, False hvis bruger ikke findes
        
        Sikkerhed:
            Gammelt password kasseres (ikke gemt nogen steder)
            Nyt password hashes med bcrypt (ny salt genereres!)
            Hver password opdatering får unik hash selvom password er samme
        """
        user = self.get_user_by_id(uid)
        if not user:
            return False
        # Hash nyt password med bcrypt (generér NY salt hver gang!)
        # "newpass" → "$2b$12$POraNBeosPrFajhM8BNBYeSkPyhoL2zYhy9VDJrmxa4U7wem/xmAW"
        user.password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")  #ÆNDRET: hash nyt password
        self._save()  # ÆNDRET: brug centraliseret save-metode
        return True

    def delete_user(self, uid: int) -> bool:
        """
        Slet bruger permanent fra database.
        
        Args:
            uid: User ID
        
        Returns:
            True hvis success, False hvis bruger ikke findes
        
        GDPR compliance:
            Right to erasure (Article 17)
            Brugeren slettes både fra memory og disk
        """
        user = self.get_user_by_id(uid)
        if not user:
            return False
        self.users.remove(user)  # Fjern fra memory liste
        self._save()  # ÆNDRET: brug centraliseret save-metode (persist sletning til disk)
        return True

    def validate_user(self, first_name: str, password: str) -> bool:
        """
        Validerer login baseret på fornavn og password.
        
        Args:
            first_name: Fornavn (plaintext)
            password: Password (plaintext)
        
        Returns:
            True hvis valid login, False hvis invalid
        
        Workflow:
            1. Iterer over alle brugere
            2. Match first_name (plaintext sammenligning - data allerede dekrypteret i memory)
            3. Verificer password med bcrypt.checkpw() (sammenlign plaintext med hash)
        
        Sikkerhed:
            bcrypt.checkpw() er SLOW by design (beskyttelse mod brute-force)
            Hash sammenlignes sikkert (timing attack resistent)
            Plaintext password ALDRIG gemt (kun brugt til verification)
        """
        # Iterer over alle brugere (linear search)
        for user in self.users:
            # Data er allerede dekrypteret i memory - ingen dekryptering nødvendig  #ÆNDRET KOMMENTAR
            # Match first_name (plaintext sammenligning: "John" == "John")
            # OG verificer password med bcrypt
            # bcrypt.checkpw() hasher input password og sammenligner med stored hash
            # "mypassword" + hash → verify → True/False
            if user.first_name == first_name and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                return True  # Valid login!
        return False  # Ingen match - invalid login

    def clear_memory(self) -> None:
        """
        GDPR: Fjern dekrypteret data fra hukommelsen.
        
        GDPR compliance:
            Article 5 - Data minimisation
            Article 17 - Right to erasure
            Article 32 - Security of processing
        
        Hvorfor overskrive før sletning?
            Python's garbage collector sletter data EVENTUELT
            Men memory kan stadig indeholde data indtil GC kører
            Overskriving sikrer data er "værdiløs" hvis memory dumpes
        
        Workflow:
            1. Overskriv sensitive felter med "0" strings (128 tegn)
            2. Clear users liste (fjern alle referencer)
            3. Force garbage collection (gc.collect())
        
        Begrænsning:
            Python garanterer IKKE fuld memory sletning (CPython limitation)
            Dette er "best effort" defense-in-depth
            Production: Overvej full-disk encryption + secure memory management
        """
        for user in self.users:
            # Bedste indsats – overskriv strenge før sletning (Python garanterer ikke fuld sletning)
            # Overskriv med "0" string (128 karakterer) - gør data værdiløs hvis memory dumpes
            user.first_name = "0" * 128  # "John" → "00000000000..." (128 nuller)
            user.last_name  = "0" * 128  # "Doe" → "00000000000..."
            user.address    = "0" * 128  # "Main Street" → "00000000000..."
            # street_number og password ikke overskrevet (mindre kritisk)

        self.users.clear()  #TILFØJET: slet alle brugere fra memory (fjern alle User objekter)
        gc.collect()  # Forsøg at tvinge garbage collection hurtigere (CPython specific)
        # gc.collect() returnerer antal objekter der blev frigivet
        # Dette garanterer IKKE øjeblikkelig memory cleanup, men hjælper