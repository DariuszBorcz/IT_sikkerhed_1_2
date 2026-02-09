# Simpel Cycle Process Test: Password-reset workflow

# "Database" med passwords
password_db = {"user1": "MitKode123"}

# Step 1: User request reset
def request_reset(user):
    print(f"{user} har anmodet om password reset.")
    # System sender token (vi simulerer bare)
    token = "12345"  
    return token

# Step 2 + 3: User indtaster token + nyt password
def reset_password(user, token, new_password):
    print(f"{user} indtaster token '{token}' og nyt password '{new_password}'")
    # Step 4: System validerer og opdaterer
    if token == "12345" and 8 <= len(new_password) <= 16:
        password_db[user] = new_password
        print(f"Password opdateret succesfuldt ✅")
        return True
    else:
        print(f"Password reset fejlede ❌")
        return False

# -----------------------------
# Simuler hele cyklussen
user = "user1"
token = request_reset(user)
success = reset_password(user, token, "NyKode456")

# Check at det virker
print(f"Opdateret password i DB: {password_db[user]}")
print(f"Test OK? {success}")
