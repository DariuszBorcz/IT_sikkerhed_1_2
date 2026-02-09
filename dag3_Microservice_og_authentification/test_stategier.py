
# grænseværdi klasser:

def is_valid_password(password):
    """true hvis password er mellem 8 og 16 tegn"""
    return 8 <= len(password) <= 16

password = "MitKode123" ## hardcoded password <3 

resultat = is_valid_password(password)
print(resultat) 

# ækvivalens klasser:
if is_valid_password(password):
    print(f"Password '{password}' er gyldigt")
else:
    if len(password) < 8:
        print(f"Password '{password}' er for kort")
    elif len(password) > 16:
        print(f"Password '{password}' er for langt")


