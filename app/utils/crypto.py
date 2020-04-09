#/usr/bin/env python


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import passgenerator
import os
from .file_handlers import read_file_bytes, write_file_bytes, write_file_base64, read_file_base64, write_file_text
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes, aead
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib



# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
rand_filename_string = 64
kdf_iterations=100000
default_password_length = 32



# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------

def sha2_256(destination):
    file_bytes = read_file_bytes(destination)
    out_hash = hashlib.sha256(file_bytes).hexdigest()
    return out_hash



def sha3_256(destination):
    file_bytes = read_file_bytes(destination)
    out_hash = hashlib.sha3_256(file_bytes).hexdigest()
    return out_hash



def encrypt_aes_cbc(input_file, destination, encryption_bits=256, password='', outform='base64', salt_in_output=True, iv_in_output=True):
    backend = default_backend() # set encryption backend

    if password == '':
        password = passgenerator.complexpass(default_password_length, special=False)
    
    salt = passgenerator.complexpass(encryption_bits//16).encode() # defaults to 128 bits (half the key size)
    
    # setup key derivation function
    kdf = PBKDF2HMAC(
        algorithm = hashes.SHA256(),
        length = encryption_bits//8, # encryption bits expressed as bytes (8 bits per byte)
        salt = salt,
        iterations = kdf_iterations,
        backend = backend
    )

    key = kdf.derive(password.encode())

    # generate key if it was not provided
    #if encryption_key == '':
    #    decoded_key = passgenerator.complexpass(encryption_bits//8)
    #    key = decoded_key.encode()
    #else:
    #    key = encryption_key.encode()
    
    # create initialization vector
    iv = passgenerator.complexpass(encryption_bits//16).encode()

    # instantiate cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)

    # instantiate padder
    padder = PKCS7(128).padder() # AES uses 128 bit blocks

    # get bytes from input file
    file_bytes = read_file_bytes(input_file)

    # do the padding
    padded_data = padder.update(file_bytes) + padder.finalize()

    # instantiate the encryptor
    encryptor = cipher.encryptor()

    # do the encryption
    cipher_text = encryptor.update(padded_data) + encryptor.finalize()

    # write output file
    if outform == 'bytes':
        output_file = write_file_bytes(cipher_text, destination)
    else:
        output_file = write_file_base64(cipher_text, salt, iv, destination)
    

    base64_key = base64.urlsafe_b64encode(key).decode()
    base64_iv = base64.urlsafe_b64encode(iv).decode()
    base64_salt = base64.urlsafe_b64encode(salt).decode()

    return output_file, base64_key, base64_iv, password, base64_salt



def decrypt_aes_cbc(input_file, destination, password, encryption_bits=256, iv='', salt=''):
    backend = default_backend() # set encryption backend

    # get salt, initialization vector, and ciphertext
    salt, iv, ciphertext = read_file_base64(input_file)

    # setup key derivation function
    kdf = PBKDF2HMAC(
        algorithm = hashes.SHA256(),
        length = encryption_bits//8, # encryption bits expressed as bytes (8 bits per byte)
        salt = salt,
        iterations = kdf_iterations,
        backend = backend
    )

    key = kdf.derive(password.encode())

    # instantiate cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    
    # instantiate the encryptor
    decryptor = cipher.decryptor()

    # do the encryption
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # instantiate unpadder
    unpadder = PKCS7(128).unpadder() # AES uses 128 bit blocks

    # undo the padding
    outdata = unpadder.update(plaintext) + unpadder.finalize()

    # write output file
    output_file = write_file_text(outdata.decode(), destination)

    return output_file