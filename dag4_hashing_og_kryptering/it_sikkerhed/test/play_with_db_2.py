from src.flat_file.data_handler import Data_handler

# Load din fil (opretter den hvis den ikke findes)
dh = Data_handler("db_flat_file_test.json")

# Se alle brugere
print("Alle brugere i databasen:")
for user in dh.users:
    print(user.__dict__)

# Opret en ny bruger
dh.create_user("Test", "User", "Street 1", 1, "mypassword")
print("\nEfter oprettelse:")
for user in dh.users:
    print(user.__dict__)

# Opdater en bruger
dh.update_password(0, "newsecret")
print("\nEfter password-opdatering:")
for user in dh.users:
    print(user.__dict__)

# Slet en bruger
dh.delete_user(0)
print("\nEfter sletning:")
for user in dh.users:
    print(user.__dict__)