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