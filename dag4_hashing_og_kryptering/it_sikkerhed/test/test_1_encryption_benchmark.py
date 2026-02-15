import pytest
import time
import tracemalloc
from Crypto.Cipher import AES, Blowfish, PKCS1_OAEP
from Crypto.PublicKey import RSA, ECC
from Crypto.Hash import SHA256, SHA3_256
from Crypto.Random import get_random_bytes
from Crypto.Signature import DSS, pkcs1_15
from Crypto.PublicKey import ElGamal
from Crypto import Random
from Crypto.Util import number
from Crypto.Util.Padding import pad, unpad
import hashlib

#pytestmark = pytest.mark.focus

# Helper: measure execution time and memory
def benchmark(func, *args, **kwargs):
    tracemalloc.start()
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed*1000, peak / 1024  # peak memory in KB

testData = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."[0:1024]
print("length: ", len(testData))



# ---------- SYMMETRIC ----------

def test_aes_128():
    # given
    key = get_random_bytes(16)  # AES-128 bit = 16 byte 
    data = testData.encode()  # 1024 bytes

    # when
    print(f"\n[AES-128] Encrypt / Decrypt")    

    for n in range(4):
        # Benchmark encryption
        cipher_enc = AES.new(key, AES.MODE_EAX)
        _, enc_time, enc_mem = benchmark(cipher_enc.encrypt, data)
        ciphertext, tag = cipher_enc.encrypt_and_digest(data)
        nonce = cipher_enc.nonce

        # Benchmark decryption
        cipher_dec = AES.new(key, AES.MODE_EAX, nonce=nonce)
        _, dec_time, dec_mem = benchmark(cipher_dec.decrypt, ciphertext)
        decrypted = cipher_dec.decrypt(ciphertext)
    
        # then (manual)
        print(f"CPU:\t{enc_time:.6f}\tms / \t{dec_time:.6f}\tms")
        print(f"RAM:\t{enc_mem:.2f}\tKB / {dec_mem:.2f}\tKB")


def test_aes_256():
    # given
    key = get_random_bytes(32)  # AES-256 bit = 32 byte
    data = testData.encode()  # 1024 bytes

    # when
    print(f"\n[AES 256]")    

    for n in range(4):
        # Benchmark encryption
        cipher_enc = AES.new(key, AES.MODE_EAX)
        _, enc_time, enc_mem = benchmark(cipher_enc.encrypt, data)
        ciphertext, tag = cipher_enc.encrypt_and_digest(data)
        nonce = cipher_enc.nonce

        # Benchmark decryption
        cipher_dec = AES.new(key, AES.MODE_EAX, nonce=nonce)
        _, dec_time, dec_mem = benchmark(cipher_dec.decrypt, ciphertext)
        decrypted = cipher_dec.decrypt(ciphertext)
    
        # then (manual)
        print(f"CPU:\t{enc_time:.6f}\tms / \t{dec_time:.6f}\tms")
        print(f"RAM:\t{enc_mem:.2f}\tKB / {dec_mem:.2f}\tKB")
    


def test_blowfish_128():
    # given
    key = get_random_bytes(16)  # Blowfish 128 bit =  16 byte 
    data = testData.encode()    # 1024 bytes

    # when
    print(f"\n[Blowfish-CBC]")

    for n in range(4):
        # CBC mode needs an IV (8 bytes for Blowfish)
        iv = get_random_bytes(8)
        cipher_enc = Blowfish.new(key, Blowfish.MODE_CBC, iv)
        padded_data = pad(data, Blowfish.block_size)

        # Benchmark encryption
        def encrypt_once():
            cipher_enc = Blowfish.new(key, Blowfish.MODE_CBC, iv)
            return cipher_enc.encrypt(padded_data)

        ciphertext, enc_time, enc_mem = benchmark(encrypt_once)

        # Benchmark decryption
        def decrypt_once():
            cipher_dec = Blowfish.new(key, Blowfish.MODE_CBC, iv)
            return cipher_dec.decrypt(ciphertext)
        decrypted_padded, dec_time, dec_mem = benchmark(decrypt_once)
        decrypted = unpad(decrypted_padded, Blowfish.block_size)

        # then (manual)
        assert decrypted == data, "Decrypted data does not match original!"
        print(f"CPU:\t{enc_time:.6f}\tms / \t{dec_time:.6f}\tms")
        print(f"RAM:\t{enc_mem:.2f}\tKB / {dec_mem:.2f}\tKB")
        

def test_blowfish_448():
    # given
    key = get_random_bytes(56)  # Blowfish 256 bit =  32 byte 
    data = testData.encode()    # 1024 bytes

    # when
    print(f"\n[Blowfish-CBC]")

    for n in range(4):
        # CBC mode needs an IV (8 bytes for Blowfish)
        iv = get_random_bytes(8)
        cipher_enc = Blowfish.new(key, Blowfish.MODE_CBC, iv)
        padded_data = pad(data, Blowfish.block_size)

        # Benchmark encryption
        def encrypt_once():
            cipher_enc = Blowfish.new(key, Blowfish.MODE_CBC, iv)
            return cipher_enc.encrypt(padded_data)

        ciphertext, enc_time, enc_mem = benchmark(encrypt_once)

        # Benchmark decryption
        def decrypt_once():
            cipher_dec = Blowfish.new(key, Blowfish.MODE_CBC, iv)
            return cipher_dec.decrypt(ciphertext)
        decrypted_padded, dec_time, dec_mem = benchmark(decrypt_once)
        decrypted = unpad(decrypted_padded, Blowfish.block_size)

        # then (manual)
        assert decrypted == data, "Decrypted data does not match original!"
        print(f"CPU:\t{enc_time:.6f}\tms / \t{dec_time:.6f}\tms")
        print(f"RAM:\t{enc_mem:.2f}\tKB / {dec_mem:.2f}\tKB")
        


# ---------- ASYMMETRIC ----------

def test_rsa_2048():
    # given
    key_pair = RSA.generate(2048)
    public_key = key_pair.publickey()
    private_key = key_pair
    cipher_enc = PKCS1_OAEP.new(public_key)
    cipher_dec = PKCS1_OAEP.new(private_key)

    data = testData.encode()  # 1024 bytes

    # when
    print(f"\n[RSA-2048]")

    for n in range(4):
        # RSA can only encrypt small chunks at once
        chunk_size = 190
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

        # Benchmark encryption
        def rsa_encrypt_all(data_chunks):
            ciphertext = b''.join([cipher_enc.encrypt(chunk) for chunk in data_chunks])
            return ciphertext

        _, enc_time, enc_mem = benchmark(rsa_encrypt_all, chunks)
        ciphertext = rsa_encrypt_all(chunks)

        # Benchmark decryption
        encrypted_chunk_size = len(cipher_enc.encrypt(b'A'*chunk_size))
        chunks_ct = [ciphertext[i:i + encrypted_chunk_size]
                     for i in range(0, len(ciphertext), encrypted_chunk_size)]

        def rsa_decrypt_all(ct_chunks):
            plaintext = b''.join([cipher_dec.decrypt(chunk) for chunk in ct_chunks])
            return plaintext

        _, dec_time, dec_mem = benchmark(rsa_decrypt_all, chunks_ct)
        decrypted = rsa_decrypt_all(chunks_ct)

        # then (manual)
        print(f"CPU:\t{enc_time:.6f}\tms / \t{dec_time:.6f}\tms")
        print(f"RAM:\t{enc_mem:.2f}\tKB / {dec_mem:.2f}\tKB")

        # Optional check
        assert decrypted == data, "RSA decryption failed!"


@pytest.mark.skip(reason="this one takes somes time, to it is skipped")
def test_rsa_4096():
    # given
    key_pair = RSA.generate(4096)
    public_key = key_pair.publickey()
    private_key = key_pair
    cipher_enc = PKCS1_OAEP.new(public_key)
    cipher_dec = PKCS1_OAEP.new(private_key)

    data = testData.encode()  # 1024 bytes

    # when
    print(f"\n[RSA-4096]")

    for n in range(4):
        # RSA can only encrypt small chunks at once
        chunk_size = 446
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

        # Benchmark encryption
        def rsa_encrypt_all(data_chunks):
            ciphertext = b''.join([cipher_enc.encrypt(chunk) for chunk in data_chunks])
            return ciphertext

        _, enc_time, enc_mem = benchmark(rsa_encrypt_all, chunks)
        ciphertext = rsa_encrypt_all(chunks)

        # Benchmark decryption
        encrypted_chunk_size = len(cipher_enc.encrypt(b'A'*chunk_size))
        chunks_ct = [ciphertext[i:i + encrypted_chunk_size]
                        for i in range(0, len(ciphertext), encrypted_chunk_size)]

        def rsa_decrypt_all(ct_chunks):
            plaintext = b''.join([cipher_dec.decrypt(chunk) for chunk in ct_chunks])
            return plaintext

        _, dec_time, dec_mem = benchmark(rsa_decrypt_all, chunks_ct)
        decrypted = rsa_decrypt_all(chunks_ct)

        # then (manual)
        print(f"CPU:\t{enc_time:.6f}\tms / \t{dec_time:.6f}\tms")
        print(f"RAM:\t{enc_mem:.2f}\tKB / {dec_mem:.2f}\tKB")

        # Optional check
        assert decrypted == data, "RSA decryption failed!"


# ---------- HASHING ----------

def test_sha2_256():
    # given
    data = (testData+"1").encode()  # 1024 bytes

    # when
    print(f"\n[SHA2-256]")
    cpu = 0
    ram = 0
    iterations = 100

    for n in range(iterations):
        # Benchmark hashing
        def sha256_hash(data):
            return hashlib.sha256(data).digest()

        _, hash_time, hash_mem = benchmark(sha256_hash, data)
        digest = sha256_hash(data)
        cpu += hash_time
        ram += hash_mem

    # then (manual)
    print(f"Hash: CPU:{(cpu/iterations):.6f}ms, RAM:{(ram/iterations):.2f}KB")


def test_sha2_512():
    # given
    data = testData.encode()  # 1024 bytes

    # when
    print(f"\n[SHA2-512]")
    cpu = 0
    ram = 0
    iterations = 100

    for n in range(iterations):
        # Benchmark hashing
        def sha512_hash(data):
            return hashlib.sha512(data).digest()

        _, hash_time, hash_mem = benchmark(sha512_hash, data)
        digest = sha512_hash(data)
        cpu += hash_time
        ram += hash_mem

    # then (manual)
    print(f"Hash: CPU:{(cpu/iterations):.6f}ms, RAM:{(ram/iterations):.2f}KB")


def test_sha3_256():
    # given
    data = testData.encode()  # 1024 bytes

    # when
    print(f"\n[SHA3-256]")
    cpu = 0
    ram = 0
    iterations = 100

    for n in range(iterations):
        # Benchmark hashing
        def sha3_256_hash(data):
            return hashlib.sha3_256(data).digest()

        _, hash_time, hash_mem = benchmark(sha3_256_hash, data)
        digest = sha3_256_hash(data)
        cpu += hash_time
        ram += hash_mem

    # then (manual)
    print(f"Hash: CPU:{(cpu/iterations):.6f}ms, RAM:{(ram/iterations):.2f}KB")


def test_sha3_512():
    # given
    data = testData.encode()  # 1024 bytes

    # when
    print(f"\n[SHA3-512]")
    cpu = 0
    ram = 0
    iterations = 100

    for n in range(iterations):
        # Benchmark hashing
        def sha3_512_hash(data):
            return hashlib.sha3_512(data).digest()

        _, hash_time, hash_mem = benchmark(sha3_512_hash, data)
        digest = sha3_512_hash(data)
        cpu += hash_time
        ram += hash_mem

    # then (manual)
    print(f"Hash: CPU:{(cpu/iterations):.6f}ms, RAM:{(ram/iterations):.2f}KB")