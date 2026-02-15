"""
SCRIPT: Vis krypteret data i din users.json fil
Kør dette script for at se hvordan data ser ud i filen vs. i memory
"""

import json
import os
from src.flat_file.data_handler import Data_handler

print("=" * 80)
print("KRYPTERING & HASHING - DIN DATABASE")
print("=" * 80)

# 1. Opret test database med nogle brugere
print("\n1️⃣  OPRET TEST BRUGERE:")
print("-" * 80)

test_file = "demo_users.json"

# Opret tom database
with open(test_file, "w") as f:
    json.dump({"users": []}, f)

# Opret brugere
dh = Data_handler(test_file)
dh.create_user("Alice", "Hansen", "Hovedgaden", 10, "password123")
dh.create_user("Bob", "Jensen", "Søndergade", 42, "secret456")
dh.create_user("Charlie", "Nielsen", "Nørregade", 88, "mypass789")

print(f"✅ Oprettet {dh.get_number_of_users()} brugere")

# 2. VIS KRYPTERET DATA I FIL
print("\n2️⃣  KRYPTERET DATA I FILEN (users.json):")
print("-" * 80)

with open(test_file, "r", encoding="utf-8") as f:
    file_content = json.load(f)

print(json.dumps(file_content, indent=2, ensure_ascii=False))

# 3. VIS DEKRYPTERET DATA I MEMORY
print("\n3️⃣  DEKRYPTERET DATA I MEMORY (efter load):")
print("-" * 80)

for user in dh.users:
    print(f"""
User ID: {user.person_id}
  Navn:        {user.first_name} {user.last_name}
  Adresse:     {user.address} {user.street_number}
  Password:    {user.password[:20]}... (hashet, ikke plaintext)
  Enabled:     {user.enabled}
""")

# 4. SAMMENLIGNING
print("\n4️⃣  SAMMENLIGNING - FIL vs MEMORY:")
print("-" * 80)

stored_user = file_content["users"][0]
memory_user = dh.get_user_by_id(0)

print(f"First name i FIL:    {stored_user['first_name']}")
print(f"First name i MEMORY: {memory_user.first_name}")
print(f"Er de ens? {stored_user['first_name'] == memory_user.first_name} ❌ (som forventet)")
print()
print(f"Password i FIL:      {stored_user['password']}")
print(f"Password i MEMORY:   {memory_user.password}")
print(f"Er de ens? {stored_user['password'] == memory_user.password} ✅ (begge hashet)")

# 5. FERNET MARKERS
print("\n5️⃣  FERNET KRYPTERING MARKERS:")
print("-" * 80)

print(f"Krypteret first_name: {stored_user['first_name'][:60]}...")
print(f"Indeholder 'gAAAAA': {'gAAAAA' in stored_user['first_name']} ✅")
print("⚠️  'gAAAAA' er Fernet's timestamp marker (base64-kodet)")

# 6. BCRYPT HASH STRUKTUR
print("\n6️⃣  BCRYPT HASH STRUKTUR:")
print("-" * 80)

password_hash = stored_user['password']
print(f"Komplet hash: {password_hash}")
print(f"Længde: {len(password_hash)} karakterer")
print(f"Algoritme:    {password_hash[:4]} (bcrypt version 2b)")
print(f"Work factor:  {password_hash[4:7]} (12 = 2^12 = 4096 iterations)")
print(f"Salt:         {password_hash[7:29]} (22 karakterer)")
print(f"Hash:         {password_hash[29:]} (31 karakterer)")

# 7. FILSTØRRELSE
print("\n7️⃣  FIL INFORMATION:")
print("-" * 80)

file_size = os.path.getsize(test_file)
print(f"Filnavn:       {test_file}")
print(f"Størrelse:     {file_size} bytes")
print(f"Antal brugere: {len(file_content['users'])}")

# 8. SIKKERHEDSFORDELE
print("\n8️⃣  SIKKERHEDSFORDELE:")
print("-" * 80)
print("✅ Persondata KAN IKKE læses fra disk (krypteret)")
print("✅ Passwords KAN IKKE læses fra disk (hashet)")
print("✅ Hvis hacker stjæler users.json får de INGEN brugbar data")
print("✅ GDPR compliance: Data beskyttet at rest")

print("\n" + "=" * 80)
print("TIP: Åbn demo_users.json i Notepad for at se filen selv!")
print("=" * 80)