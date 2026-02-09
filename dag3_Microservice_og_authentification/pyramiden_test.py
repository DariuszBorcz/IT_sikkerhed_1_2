# -----------------------------
# Unit-test: Test individuelle funktioner
# -----------------------------
def is_valid_password(password):
    """Returnerer True hvis password er mellem 8 og 16 tegn"""
    return 8 <= len(password) <= 16

def create_user(user, password, db):
    """Opretter en bruger med password i 'database' (liste/dict)"""
    if is_valid_password(password):
        db[user] = password
        return True
    return False

# Test unit-funktioner
db = {}
print("Unit-test - create_user gyldigt password:", create_user("user1", "MitKode123", db))  # True
print("Unit-test - create_user for kort password:", create_user("user2", "123", db))         # False

# -----------------------------
# Integration-test: Test funktioner sammen
# -----------------------------
def login(user, password, db):
    return db.get(user) == password

# Test integration: oprette bruger og login
print("Integration-test - login med gyldigt password:", login("user1", "MitKode123", db))  # True
print("Integration-test - login med forkert password:", login("user1", "Fejl123", db))    # False

# -----------------------------
# System-test / End-to-end: Hele workflow
# -----------------------------
def password_reset_workflow(user, new_password, db):
    """Simulerer hele password reset workflow"""
    if not is_valid_password(new_password):
        return False
    db[user] = new_password
    return True

# Test end-to-end workflow
print("System-test - password reset workflow:", password_reset_workflow("user1", "NyKode456", db))  # True
print("Opdateret password i DB:", db["user1"])