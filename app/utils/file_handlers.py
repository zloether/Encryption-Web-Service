#/usr/bin/env python


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import passgenerator
import os
from werkzeug.utils import secure_filename
import base64



# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
rand_filename_string = 64




# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------

# saves a file and returns the path to it
def store_file(request_files, destination):

    # make sure only a file was uploaded
    if len(request_files) < 1:
        error_message = {'error': 'missing file to encrypt'}
        error_code = 400
        return False, error_message, error_code

    # make sure only 1 file is uploaded
    if len(request_files) > 1:
        error_message = {'error': 'more than one file uploaded'}
        error_code = 400
        return False, error_message, error_code
    
    # get file from request
    for upload in request_files:
        if type(upload) == str: # only for field keys
            uploaded_file = request_files[upload] # get the file

            # generate a random string to prepend to the filename to minimize collisions
            random_string = passgenerator.complexpass(length=rand_filename_string, upper=True, lower=True, numbers=True, special=False)

            # generate filename
            uploaded_filename = random_string + ' ' + secure_filename(uploaded_file.filename)


    # make sure destination directory exists
    validate_directory(destination)

    # full path of saved file
    uploaded_file_path = os.path.join(destination, uploaded_filename)
    
    # save file to destination directory
    try:
        uploaded_file.save(uploaded_file_path)
    except IOError as e:
        print('Error: ' + str(e.filename) + ' - ' + str(e.strerror))
        error_message = {'error': 'server error'}
        error_code = 500
        return False, error_message, error_code

    return uploaded_file_path



# deletes a file
def delete_file(file_path):
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print('Error: ' + str(e.filename) + ' - ' + str(e.strerror))



# reads file in byte mode
def read_file_bytes(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
    else:
        print('Unable to read file' + str(file_path))
        error_message = {'error': 'server error'}
        error_code = 500
        return False
    
    return file_bytes




# write output file in byte mode
def write_file_bytes(file_bytes, destination):
    while True:
        # generate a random filename to minimize guesses
        out_file_name = passgenerator.complexpass(length=rand_filename_string, upper=True, lower=True, numbers=True, special=False)
        out_file = os.path.join(destination, out_file_name)
        
        # loop to make sure there are not filename collisions
        if not os.path.isfile(out_file):
            break
        
    # make sure destination directory exists
    validate_directory(destination)

    with open(out_file, 'wb') as f:
        f.write(file_bytes)

    return out_file_name # return name of written file




# write output file in as text
def write_file_text(outdata, destination):
    while True:
        # generate a random filename to minimize guesses
        out_file_name = passgenerator.complexpass(length=rand_filename_string, upper=True, lower=True, numbers=True, special=False)
        out_file = os.path.join(destination, out_file_name)
        
        # loop to make sure there are not filename collisions
        if not os.path.isfile(out_file):
            break
        
    # make sure destination directory exists
    validate_directory(destination)

    with open(out_file, 'w') as f:
        f.write(outdata)

    return out_file_name # return name of written file



# write output file in as base64
def write_file_base64(file_bytes, salt, iv, destination):
    while True:
        # generate a random filename to minimize guesses
        out_file_name = passgenerator.complexpass(length=rand_filename_string, upper=True, lower=True, numbers=True, special=False)
        out_file = os.path.join(destination, out_file_name)
        
        # loop to make sure there are not filename collisions
        if not os.path.isfile(out_file):
            break
        
    # make sure destination directory exists
    validate_directory(destination)

    output = ''
    output = output + base64.b64encode(salt).decode() + '.'
    output = output + base64.b64encode(iv).decode() + '.'
    output = output + base64.b64encode(file_bytes).decode()

    with open(out_file, 'w') as f:
        f.write(output)

    return out_file_name # return name of written file



# read file in as base64
def read_file_base64(destination):
    if validate_file(destination):
        with open(destination, 'r') as f:
            content = f.read()
            b64_salt, b64_iv, b64_ciphertext = content.split('.', 2)
        
        salt = base64.b64decode(b64_salt.encode())
        iv = base64.b64decode(b64_iv.encode())
        ciphertext = base64.b64decode(b64_ciphertext.encode())

        return salt, iv, ciphertext

    else:
        print('Error, file not found')
        return False



# create directory if it does not exist
def validate_directory(destination):
    if not os.path.isdir(destination):
        os.makedirs(destination)



# validate that file exists
def validate_file(destination):
    if not os.path.isfile(destination):
        return False
    else:
        return True