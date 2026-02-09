import pytest

# Simpel password-policy funktion
def is_valid_password(password):
    has_uppercase = any(c.isupper() for c in password)
    has_number = any(c.isdigit() for c in password)
    length_ok = 8 <= len(password) <= 16
    return has_uppercase and has_number and length_ok

# Decision table: (password, forventet resultat)
decision_table = [
    ("MitKode123", True),     # stor bogstav + tal + gyldig længde
    ("mitkode123", False),    # ingen stort bogstav
    ("MitKode", False),       # ingen tal
    ("Mit123", False),        # for kort
    ("MITKODE1234567890", False)  # 17 tegn → for langt
]

# Data-drevet test
@pytest.mark.parametrize("password,expected", decision_table)
def test_password_policy(password, expected):
    assert is_valid_password(password) == expected