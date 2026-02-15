# IT_sikkerhed_1_2

**Zealand Erhvervsakademi - IT-Sikkerhed Top-Up Bachelor 2025-2026**

Repository til kurset **Softwaresikkerhed** 



## Dag 2. Unit test opgaver:

![alt text](<Screenshot 2026-02-03 111039.png>)

![alt text](<Screenshot 2026-02-03 111249.png>)

![alt text](<Screenshot 2026-02-03 111348.png>)

![alt text](<Screenshot 2026-02-03 111353.png>)

![alt text](<Screenshot 2026-02-03 111404.png>)

![alt text](<Screenshot 2026-02-03 111446.png>)



## Dag 3: Microservice og authentification

Opgave: test strategier: password validation (tjek af passwordlængde, kompleksitet og workflow)

1. **Ækvivalensklasser**:
Formål: test input, der tilhører samme kategori (fx gyldigt eller ugyldigt password)
   Eksempel:
     - Gyldigt password: MitKode123
     - For kort: 123
     - For langt: MITKODE1234567890

Security gate: code/dev gate (unit tests på testmiljø, sikrer at input validering fungerer korrekt)

2. **Grænseværdi test**:
Formål: test på og lige omkring kritiske grænser
   Eksempel:
     - Længde 7 = for kort
     - Længde 8 = gyldigt
     - Længde 16 = gyldigt
     - Længde 17 = for langt

Security gate: code/dev gate (testmiljø, tjekker at funktionalitet og krav ikke brydes)

3. **CRUD(L) test**
Formål: Test Create, Read, Update, Delete (og Login)
   Eksempel:
     - Create: MitKode123 -> tilføjet i DB
     - Read: tjekker, om password findes
     - Update: ændrer password til NyKode456
     - Delete: sletter password
     - Login: tjek om password virker

Security gate: integration gate (testen sikrer at integration mellem komponenter/DB virker korrekt)

4. **Cycle process test**
Formål: Test hele workflow/cyklus.
   Eksempel (Password reset workflow):
     - User anmoder om reset
     - System sender token
     - User indtaster token + nyt password
     - System validerer og opdaterer password

Security gate: system / end-to-end gate (hele workflow testes i staging, sikrer at kritiske brugerrejser fungerer)

   **Flowchart:**
![alt text](<Screenshot 2026-02-05 142242-1.png>)

5. **Testpyramiden**:
Formål: test lagdelt (unit -> integration → system).
   Eksempel:
     - Unit: is_valid_password("MitKode123") → True
     - Integration: opret bruger + login
     - System: hele workflow: password reset

Security gate: afhængigt af niveau (unit, integration, system)?

6. **Decision table test**:
Formål: Test kombinationer af input og forventet output.

   |      Password     | Has Uppercase | Has Number | Length OK | Forventet |
   |:-----------------:|:-------------:|:----------:|:---------:|:---------:|
   | MitKode123        | Yes           | Yes        | Yes       | Pass      |
   | mitkode123        | No            | Yes        | Yes       | Fail      |
   | MitKode           | Yes           | No         | Yes       | Fail      |
   | Mit123            | Yes           | Yes        | No        | Fail      |
   | MITKODE1234567890 | Yes           | Yes        | No        | Fail      |

Security gate: code/dev gate (unit/data-drevne tests for input validering)


Ekstra opgave:  pipeline:

![alt text](<Screenshot 2026-02-09 210525.png>)



Dag 4. Hashing og kryptering

- Hvorfor Flat File?  pga. deres enkelhed og høje portabilitet er de enkle at implementere uden db server (de kan fx. kopieres frit uden afhængighede), så de passer  til små projekter.

fungerende flat_file_database med:

User model (person_id, first_name, last_name, address, street_number, password, enabled)
Data_handler til CRUD operationer
Flat_file_loader til at gemme/loade JSON
Tests der beviser det virker:

- Given/When/Then test logik og sikkerhedsrisici af test kommentarer:
![alt text](<Screenshot 2026-02-10 140443.png>)

![alt text](<Screenshot 2026-02-10 140453.png>)

![alt text](<Screenshot 2026-02-10 140504.png>)

![alt text](<Screenshot 2026-02-10 140513.png>)

![alt text](<Screenshot 2026-02-10 140519.png>)

- Tests: 
![alt text](<Screenshot 2026-02-10 140801.png>)



Opgave 2:

# Kryptering og Hashing Implementation

## Om dette projekt

Dette projekt er udviklet som en læringsopgave med fokus på kryptering, hashing og GDPR-compliance. 

### Udvikling med AI-assistance

**Baggrund:**
Som studerende med begrænset programmering erfaring valgte jeg at benytte AI-værktøjer (primært Claude.ai og Grok) til at implementere produktionsklar kode med robust error handling

**Hvorfor AI?**
- **Nysgerrighed**: Afprøve hvordan moderne AI-værktøjer håndterer sikkerhedsopgaver
- **Læring**: Forstå komplekse koncepter gennem praktisk implementation
- **Sammenligning**: Se forskellige tilgange fra Claude vs Grok

**Kompleksitet:**
Koden blev mere kompleks end oprindeligt planlagt fordi jeg løste problemer iterativt:
1. Tests fejlede → Tilføjede dekryptering
2. Class-level variable bug → Fixede instance isolation
3. Silent errors → Tilføjede robust exception handling
4. Memory security → Tilføjede overwrite i `clear_memory()`


---

Kryptering: Felter, som vi gerne vil kunne læse igen (f.eks. fornavn, efternavn, by, email, telefon). Kryptering skal kunne dekrypteres, men skal ikke gemmes som klar tekst.

Hashing: Felter som kun skal kunne valideres, men aldrig dekrypteres. fx passwords (bcrypt eller sha256 + salt)

Alle kodeændringer blev lavet med claude.ai og koden blev kompleks fordi jeg prøvede at løse problemer løbende, jeg gætter at der findes svagheder og steder hvor det er blevet unødigt komplekst 

Adskillelse:  
- password til bcrypt hashing
- persondata (navn, adresse, email, telefon osv.) til Fernet symmetrisk kryptering
- encryption at rest, data ligger krypteret i JSON filen
- dekryptering kun i memory (loader - dekrypterer - arbejder med plaintext i RAM)
- clear_memory() — simpel implementering der tømmer listen (i hukommelsen)
- der blev tilføjet ekstra sikkerhedstests (godt!)

## Algoritmevalg

### Kryptering: Fernet (AES-128 CBC)
**Valgt fordi:**
- FIPS 140-2 approved (US government standard)
- Built-in HMAC for integrity verification
- Automatisk timestamp support
- Del af `cryptography` biblioteket (industry standard)

**Alternativer overvejet:**
- AES-256 GCM: Stærkere, men mere kompleks
- RSA: Asymmetrisk, men for langsom til storage
- Triple DES: Forældet, ikke anbefalet

### Hashing: bcrypt
**Valgt fordi:**
- OWASP Top 10 anbefaling
- Automatisk salt generation
- Work factor (2^12 iterations by default)
- Slow by design (brute-force beskyttelse)

**Alternativer overvejet:**
- Argon2: Nyere, men mindre kendt
- PBKDF2: God, men hurtigere end bcrypt
- SHA-256: FOR hurtig til passwords

---

## Hvornår krypteres data?

**Tidspunkt:** Ved save til fil (`_save()` metoden)

**Hvorfor:**
- GDPR Article 32: Encryption of personal data at rest
- Beskyttelse mod database theft
- Defense-in-depth princip

**Hvad krypteres:**
Persondata (first_name, last_name, address, street_number)

**Hvad krypteres IKKE:**
- Passwords (allerede hashet med bcrypt)
- person_id (ikke sensitiv)
- enabled (boolean, ikke sensitiv)

---

## Hvornår dekrypteres data?

**Tidspunkt:** Ved load fra fil (`_load_and_decrypt_all()`)

**Hvorfor:**
- Performance: Dekrypter én gang i stedet for konstant
- Funktionalitet: Application layer arbejder med plaintext
- Fleksibilitet: Nemmere søgning og filtrering

**Trade-off:**
Data ligger plaintext i RAM (mitigeret med `clear_memory()`)

---

## Hvornår fjernes data fra hukommelsen?

**Tidspunkt:** Eksplicit via `clear_memory()` metoden

**Hvorfor:**
- GDPR Article 5: Data minimisation
- GDPR Article 17: Right to erasure
- Security: Beskyt mod memory dumps

**Implementation:**
1. Overskriv sensitive felter med "0" * 128
2. Clear users liste
3. Force garbage collection (`gc.collect()`)

---

## Beskriv om du tager hensyn til noget andet vedrørende dekrypteret data fra hukommelsen

### Ja - flere hensyn:

**1. Overskriv før sletning (Defense-in-depth)**
- Python's `clear()` sletter kun referencer, ikke memory
- Vi overskriver data med "0" * 128 først
- Gør data værdiløs hvis memory dumpes

**2. Garbage Collection**
- `gc.collect()` forsøger at frigive memory hurtigere
- Reducerer tiden dekrypteret data ligger i RAM
- Ikke garanteret, men best practice

**3. Memory Dump Risici**
Vi er bevidste om følgende risici:
- **Swap/Pagefile**: Data kan swappes til disk (ukrypteret)
- **Crash dumps**: Process dumps kan indeholde dekrypteret data
- **Hibernation**: RAM gemmes til disk ved hibernation
- **Cold boot attacks**: Memory kan læses efter restart

**4. Mitigations (Production anbefalinger):**
- Krypter swap partition (Linux: dm-crypt, Windows: BitLocker)
- Disable core dumps: `ulimit -c 0`
- Disable hibernation på sikkerhedskritiske systemer
- Full-disk encryption som ekstra lag

**5. Python Begrænsninger**
- CPython garanterer ikke fuld memory cleanup
- Strings er immutable (gamle værdier kan overleve)
- Overskriving er "best effort", ikke garanteret

**Konklusion:**
Vores `clear_memory()` implementation er best practice for Python, men har begrænsninger. I et high-security miljø ville vi anbefale:
- C extensions for secure memory wiping
- Memory locking (`mlock()`) for at forhindre swapping
- Process isolation (containers/VMs)

---

## GDPR Compliance

- ✅ Article 32: Encryption at rest (Fernet)
- ✅ Article 32: Password security (bcrypt)
- ✅ Article 5: Data minimisation (clear_memory)
- ✅ Article 17: Right to erasure (delete_user + clear_memory)

---

## Dataflow
```
Create: Plaintext → Hash password → Store plaintext in memory → Encrypt → Save to disk
Load:   Encrypted on disk → Decrypt → Store plaintext in memory → Application use
Clear:  Plaintext in memory → Overwrite → Clear → GC collect
```


## Beskriv om du tager hensyn til noget andet vedrørende dekrypteret data fra hukommelsen

### Ja - flere sikkerhedshensyn:

**1. Overskriv før sletning (Defense-in-depth)**
- Python's `clear()` sletter kun referencer, ikke faktisk memory
- Vi overskriver først data med "0" * 128 for at gøre det værdiløst
- Dette beskytter mod memory dump attacks

**2. Garbage Collection**
- Kalder `gc.collect()` for at frigive memory hurtigere
- Reducerer vinduesperiode hvor dekrypteret data ligger i RAM
- Ikke garanteret øjeblikkelig, men best practice

**3. Kendte Memory Dump Risici**
Vi er bevidste om følgende trusler:
- **Swap/Pagefile**: Data kan swappes til disk (ukrypteret)
- **Crash dumps**: Process memory dumps kan indeholde plaintext
- **Hibernation**: RAM gemmes til disk ved sleep
- **Cold boot attacks**: Memory kan læses kort efter power-off

**4. Production Mitigations**
I et produktionsmiljø ville vi anbefale:
- Krypter swap partition (Linux: dm-crypt, Windows: BitLocker)
- Disable core dumps: `ulimit -c 0`
- Disable hibernation på servere
- Full-disk encryption som ekstra sikkerhedslag
- Process memory locking (`mlock()`) for kritisk data

**5. Python Tekniske Begrænsninger**
- CPython garanterer ikke fuld memory cleanup
- Strings er immutable (gamle værdier kan overleve i heap)
- Vores overskriving er "best effort", ikke kryptografisk garanteret

**Konklusion:**
`clear_memory()` følger best practices for Python, men har platform-begrænsninger. High-security systemer bør overveje:
- C extensions for secure memory wiping
- Hardware security modules (HSM)
- Trusted execution environments (TEE)