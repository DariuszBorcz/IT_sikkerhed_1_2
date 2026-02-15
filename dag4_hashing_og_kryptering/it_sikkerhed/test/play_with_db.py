from src.flat_file.data_handler import Data_handler

db = Data_handler("my_test_users.json")

# Opret en bruger
db.create_user("Anna", "Larsen", "Main Street", 5, "mypassword")

# Hent og print alle brugere
for user in db.users:
    print(user.person_id, user.first_name, user.last_name, user.password, user.enabled)

# Opdater en bruger
db.update_first_name(0, "Anne-Marie")

# Deaktiver en bruger
db.disable_user(0)

# Slet en bruger
db.delete_user(0)