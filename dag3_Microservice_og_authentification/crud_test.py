# Enkel CRUD(L)-test for password

"""

Create: Opretter et password i “databasen” (liste)
Read: Tjekker om password findes
Update: Ændrer password
Delete: Sletter password
Login: Simulerer login med password

"""

# "Database" med passwords (simpel liste)
password_db = []

# Create: tilføj et password
def create_password(password):
    password_db.append(password)
    print(f"Password '{password}' oprettet.")

# Read: tjek om password findes
def read_password(password):
    return password in password_db

# Update: ændre eksisterende password
def update_password(old_password, new_password):
    if old_password in password_db:
        index = password_db.index(old_password)
        password_db[index] = new_password
        print(f"Password ændret fra '{old_password}' til '{new_password}'.")

# Delete: slet password
def delete_password(password):
    if password in password_db:
        password_db.remove(password)
        print(f"Password '{password}' slettet.")

# Login: tjek om password er gyldigt
def login(password):
    if password in password_db:
        print(f"Login succes med '{password}' ✅")
    else:
        print(f"Login fejlede med '{password}' ❌")

# -----------------------------
# Eksempel på CRUD(L) flow
create_password("MitKode123")
print("Findes i DB?", read_password("MitKode123"))
update_password("MitKode123", "NyKode456")
login("NyKode456")
delete_password("NyKode456")
login("NyKode456")  # Skal fejle