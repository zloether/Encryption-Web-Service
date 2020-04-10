#!/usr/bin/env python


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import requests
import sys
import os
import hashlib



# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
target = 'http://localhost:5000/'
out_dirname = 'testing_output'
app_path = os.path.dirname(os.path.realpath(__file__))
out_dir = os.path.join(app_path, out_dirname)
s = requests.Session()
chunk_size = 8192




# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------
def encrypt_file(input_file):
    url = target + '/encrypt'
    files = {'data': open(input_file, 'rb')}
    r = s.post(url, files=files)

    # make sure we have a valid response code
    validate_response(r)

    # get JSON from response
    j = r.json()

    # pull out what we need from the JSON
    dl_url = target + j['download url']
    password = j['password']
    sha2_256 = j['sha2-256']
    sha3_256 = j['sha3-256']

    # download the file
    full_path_for_file, filename = download_file(dl_url)

    # make sure the hashes match
    validate_hashes(full_path_for_file, sha2_256, sha3_256)

    print('Filename: ' + filename)
    print('Password: ' + password)
    
    return full_path_for_file, password


def decrypt_file(input_file, password):
    print(input_file)
    url = target + '/decrypt'
    payload = {'password': password}
    files = {'data': open(input_file, 'rb')}
    r = s.post(url, files=files, data=payload)

    # make sure we have a valid response code
    validate_response(r)

    # get JSON from response
    j = r.json()

    # pull out what we need from the JSON
    dl_url = target + j['download url']
    sha2_256 = j['sha2-256']
    sha3_256 = j['sha3-256']

    # download the file
    full_path_for_file, filename = download_file(dl_url)

    # make sure the hashes match
    validate_hashes(full_path_for_file, sha2_256, sha3_256)

    print('Filename: ' + filename)




def download_file(url):
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    filename = url.split('/')[-1] # get everything after the last /
    file_target = os.path.join(out_dir, filename)
    with s.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_target, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    
    return file_target, filename


def validate_hashes(target_file, sha2_256, sha3_256):
    with open(target_file, 'rb') as f:
        file_bytes = f.read()
    
    local_sha2_256 = hashlib.sha256(file_bytes).hexdigest()
    local_sha3_256 = hashlib.sha3_256(file_bytes).hexdigest()

    if local_sha2_256 == sha2_256 and local_sha3_256 == sha3_256:
        return
    else:
        print('Error! Hashes do not match')
        print('Local hashes:')
        print('SHA2-256: ' + str(local_sha2_256))
        print('SHA3-256: ' + str(local_sha3_256))
        print('Expected hashes:')
        print('SHA2-256: ' + str(sha2_256))
        print('SHA3-256: ' + str(sha3_256))
        exit()


def validate_response(response):
    if response.status_code == 200:
        return True
    else:
        print('Error')
        print('Status code: ' + str(response.status_code))
        print(response.text)




def file_exists(input_file):
    if os.path.isfile(input_file):
        return True
    else:
        return False



# -----------------------------------------------------------------------------
# runner
# -----------------------------------------------------------------------------
def runner(input_file):
    if not file_exists(input_file):
        print('Cannot find file: ' + str(input_file))
        exit()
    
    encrypted_file, password = encrypt_file(input_file)
    decrypt_file(encrypted_file, password)






if __name__ == "__main__":
    input_file = sys.argv[1]

    runner(input_file)