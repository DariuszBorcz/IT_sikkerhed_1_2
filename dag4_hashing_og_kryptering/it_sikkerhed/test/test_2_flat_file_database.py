import json
import os
import pytest
from src.flat_file.data_handler import Data_handler
from src.flat_file.user import User  #TILFØJET: manglende import

pytestmark = pytest.mark.focus
test_file_name = "db_flat_file_test.json"


# helpers
def create_json_file(filename: str, content: dict):
    """Helper til at oprette test-jsonfiler."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

def delete_json_files():
    filename = test_file_name
    # if os.path.exists(filename):
        # os.remove(filename)  # bare for at gemme filen og 

"""# setup / cleanup step for each test
@pytest.fixture(scope="function", autouse=True)
def cleanup_files():
    # before test
    delete_json_files()   # - kommenteret kun for test
    yield
    # after test
    delete_json_files()   # - kommenteret kun for test"""
    
@pytest.fixture(scope="function", autouse=True)
def setup_empty_db_file():
    # Before test: opret tom JSON-fil
    with open(test_file_name, "w", encoding="utf-8") as f:
        json.dump({"users": []}, f, indent=2)
    yield
    # After test: slet fil
    # if os.path.exists(test_file_name):
    #    os.remove(test_file_name)

# tests

def test_create_and_find_user():
    # Given: tom flat file database med 0 brugere (vi starter med en ny data_handler instance og verificerer at databasen er tom)
    
    data_handler = Data_handler(test_file_name)
    assert data_handler.get_number_of_users() == 0

    # When: vi opretter en ny bruger med create_user() og brugerdata: John Doe, Main Street 10, password "secret"
    data_handler.create_user("John", "Doe", "Main Street", 10, "secret")

    # Then: database indeholder præcis 1 bruger med korrekte værdier
    # vi verificerer at brugeren blev oprettet med alle felter korrekte
    assert data_handler.get_number_of_users() == 1
    print(data_handler.users)

    user:User = data_handler.get_user_by_id(0)
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.address == "Main Street"
    assert user.street_number == 10
    # FJERNET: assert user.password == "secret"  #ÆNDRET: Password er hashet med bcrypt, ikke plaintext!
    assert user.password is not None  #TILFØJET: verificer at password blev hashet (ikke None)
    assert user.password.startswith("$2b$")  #TILFØJET: verificer bcrypt hash format ($2b$ = bcrypt)
    assert user.enabled is True
# Sikkerhedsrisiko: hvis denne test fejler, kan brugere blive oprettet med forkerte eller manglende data, 
# hvilket kan føre til datakorruption og fejl i autentifikation og autorisation.

def test_disable_enable_user():
    # Given: database med 2 aktive brugere. Vi opretter to brugere og verificerer at begge er aktive (enabled=True)

    data_handler = Data_handler("db_flat_file_test.json")
    assert data_handler.get_number_of_users() == 0
    data_handler.create_user("John", "Doe", "Main Street", 11, "secret")
    data_handler.create_user("John2", "Doe2", "Main Street2", 12, "secret2")
    assert data_handler.get_number_of_users() == 2
    user0:User = data_handler.get_user_by_id(0)
    assert user0.enabled == True
    user1:User = data_handler.get_user_by_id(1)    
    assert user1.enabled == True

    # When disable: vi deaktiverer bruger 0
    data_handler.disable_user(0)
    
    # Then: kun bruger 0 er deaktiveret, bruger 1 stadig aktiv
    assert user0.enabled == False
    assert user1.enabled == True

    # When re-enable:  vi deaktiverer bruger 1 og genaktiverer bruger 0
    data_handler.disable_user(1)
    data_handler.enable_user(0)

    # Then: status er vendt (bruger 0 aktiv, bruger 1 deaktiveret)
    assert user0.enabled == True
    assert user1.enabled == False
# Sikkerhedsrisiko: hvis denne test fejler, kan deaktiverede brugere fortsat have adgang til systemet,
# eller aktive brugere kan blive låst ude, hvilket udgør en alvorlig sikkerhedsrisiko.

    
def test_update_user_fields():
     # Given: en database med en eksisterende bruger
    dh = Data_handler(test_file_name)
    dh.create_user("Alice", "Smith", "Street", 5, "pass123")
    
    original_password_hash = dh.get_user_by_id(0).password  #TILFØJET: gem original password hash for at verificere opdatering

    # When: vi opdaterer alle felter for brugeren
    dh.update_first_name(0, "Alicia")
    dh.update_last_name(0, "Brown")
    dh.update_address(0, "New Street")
    dh.update_street_number(0, 99)
    dh.update_password(0, "newpass")

    # Then: alle felter er opdateret korrekt
    user = dh.get_user_by_id(0)
    assert user.first_name == "Alicia"
    assert user.last_name == "Brown"
    assert user.address == "New Street"
    assert user.street_number == 99
    # FJERNET: assert user.password == "newpass"  #ÆNDRET: Password er hashet, ikke plaintext!
    assert user.password != original_password_hash  #TILFØJET: verificer at password blev opdateret (ny hash forskellig fra original)
    assert user.password.startswith("$2b$")  #TILFØJET: verificer bcrypt hash format
# Sikkerhedsrisiko: hvis denne test fejler, kan brugere have forkerte data,
# hvilket kan føre til misforståelser, fejlagtige autorisationer eller manglende adgang.

def test_delete_user():
    # Given: en database med en eksisterende bruger
    dh = Data_handler(test_file_name)
    dh.create_user("Bob", "Jones", "Street 2", 10, "pass")
    assert dh.get_number_of_users() == 1
    # When: vi sletter brugeren
    dh.delete_user(0)

    # Then: databasen er tom og brugeren findes ikke længere
    assert dh.get_number_of_users() == 0
    assert dh.get_user_by_id(0) is None
# Sikkerhedsrisiko: hvis denne test fejler, kan slettede brugere stadig have adgang,
# hvilket udgør en alvorlig sikkerhedsrisiko for systemets integritet.


def test_validate_user():
    # Given: en database med en eksisterende bruger
    dh = Data_handler(test_file_name)
    dh.create_user("Charlie", "Brown", "Main Street", 7, "mypassword")

    # When: vi tjekker med korrekt og forkert password
    valid_login = dh.validate_user("Charlie", "mypassword")
    invalid_login = dh.validate_user("Charlie", "wrongpass")

    # Then: korrekt login giver True, forkert login giver False
    assert valid_login is True
    assert invalid_login is False
# Sikkerhedsrisiko: hvis denne test fejler, kan brugere logge ind uden korrekt password
# hvilket kompromitterer systemets adgangskontrol.


def test_encryption_at_rest():  #TILFØJET: Ny test for kryptering i fil (GDPR compliance)
    """Test at persondata er krypteret i JSON-filen (encryption at rest)"""
    # Given: en database med en bruger
    dh = Data_handler(test_file_name)
    dh.create_user("David", "Miller", "Oak Street", 42, "testpass")
    
    # When: vi læser JSON-filen direkte
    with open(test_file_name, "r", encoding="utf-8") as f:
        file_content = json.load(f)
    
    # Then: persondata skal være krypteret i filen (ikke plaintext)
    stored_user = file_content["users"][0]
    assert stored_user["first_name"] != "David"  #TILFØJET: Skal være krypteret, ikke plaintext
    assert stored_user["last_name"] != "Miller"  #TILFØJET: Skal være krypteret
    assert stored_user["address"] != "Oak Street"  #TILFØJET: Skal være krypteret
    assert str(stored_user["street_number"]) != "42"  #TILFØJET: Skal være krypteret
    
    # Password skal være hashet (bcrypt format)
    assert stored_user["password"].startswith("$2b$")  #TILFØJET: bcrypt hash format
    
    # Krypteret data skal indeholde Fernet-kendetegn (base64 + "gAAAAA")
    assert "gAAAAA" in stored_user["first_name"]  #TILFØJET: Fernet timestamp marker (bevis for kryptering)
# Sikkerhedsrisiko: hvis data ikke er krypteret i filen, kan sensitive persondata læses direkte fra disk


def test_decryption_in_memory():  #TILFØJET: Ny test for dekryptering i memory
    """Test at data er dekrypteret korrekt i memory efter load"""
    # Given: en database med krypteret data i fil
    dh = Data_handler(test_file_name)
    dh.create_user("Emma", "Wilson", "Pine Street", 88, "pass456")
    
    # Verificer at data er krypteret i filen
    with open(test_file_name, "r", encoding="utf-8") as f:
        file_content = json.load(f)
    stored_user = file_content["users"][0]
    
    # Then: data i filen skal være krypteret (ikke plaintext)
    assert stored_user["first_name"] != "Emma"  #TILFØJET: ikke plaintext i fil
    assert "gAAAAA" in stored_user["first_name"]  #TILFØJET: Fernet kryptering marker
    assert stored_user["last_name"] != "Wilson"  #TILFØJET: ikke plaintext
    assert stored_user["address"] != "Pine Street"  #TILFØJET: ikke plaintext
    
    # Men data i memory skal være dekrypteret
    user_in_memory = dh.get_user_by_id(0)
    assert user_in_memory.first_name == "Emma"  #TILFØJET: dekrypteret i memory
    assert user_in_memory.last_name == "Wilson"  #TILFØJET: dekrypteret i memory
    assert user_in_memory.address == "Pine Street"  #TILFØJET: dekrypteret i memory
    assert user_in_memory.street_number == 88  #TILFØJET: dekrypteret i memory
# Sikkerhedsrisiko: hvis dekryptering fejler, kan applikationen ikke arbejde med dataene
# Testen verificerer: 1) Encryption at rest (i fil), 2) Decryption in memory (i RAM)


def test_clear_memory_gdpr():  #TILFØJET: Ny test for GDPR clear_memory()
    """Test at clear_memory() fjerner dekrypteret data fra hukommelsen (GDPR compliance)"""
    # Given: en database med brugere i memory
    dh = Data_handler(test_file_name)
    dh.create_user("Frank", "Davis", "Maple Street", 15, "secure123")
    assert dh.get_number_of_users() == 1
    
    # When: vi kalder clear_memory()
    dh.clear_memory()
    
    # Then: alle brugere skal være fjernet fra memory
    assert dh.get_number_of_users() == 0  #TILFØJET: verificer at memory er tom
    assert dh.get_user_by_id(0) is None  #TILFØJET: verificer at user ikke findes
# GDPR compliance: data skal kunne fjernes fra hukommelsen når det ikke længere er nødvendigt