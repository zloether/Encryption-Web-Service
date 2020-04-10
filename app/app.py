#!/usr/bin/env python

#########################################################################################
# NAME: app.py
# 
# Website: https://github.com/zloether/Encryption-Web-Service
#
# Description: Web service that provides encryption services
#########################################################################################



# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from utils.file_handlers import store_file, delete_file
from utils import crypto
from flask import Flask, request, render_template, Markup, url_for, send_from_directory
import markdown
import os



# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
app = Flask(__name__)
app_path = os.path.dirname(os.path.realpath(__file__))
templates_folder = os.path.join(app_path, 'templates')
unencrypted_uploads_folder = os.path.join(app_path, 'uploads_unencrypted')
encrypted_output_folder = os.path.join(app_path, 'outputs_encrypted')
encrypted_uploads_folder = os.path.join(app_path, 'uploads_encrypted')
decrypted_output_folder = os.path.join(app_path, 'outputs_decrypted')



# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    index_md = os.path.join(templates_folder, 'index.md')
    with open(index_md, 'r') as f:
        content = f.read()
    #content = Markup(markdown.markdown(content, extensions=['markdown.extensions.tables']))
    content = Markup(markdown.markdown(content))
    return render_template('index.html', **locals())



@app.route("/encrypt", methods=['POST'])
def path_encrypt():
    # Take provided file and encrypt it
    # Default values:
    #   Encryption algorithm: AES-256-CBC
    
    # get form data
    if request.form.get('algorithm'):
        print(request.form.get('algorithm'))

    # write file to disk
    stored_file = store_file(request.files, unencrypted_uploads_folder)
    if stored_file[0] == False:
        error_message = stored_file[1]
        error_code = stored_file[2]
        return error_message, error_code
    
    encrypted_file, key, iv, password, salt = crypto.encrypt_aes_cbc(stored_file, encrypted_output_folder)
    
    # delete unencrypted file
    delete_file(stored_file)

    output = {
        'download url': url_for('path_encrypt_download', id=encrypted_file),
        'key': key,
        'initialization vector': iv,
        'password': password,
        'salt': salt,
        'sha2-256': crypto.sha2_256(os.path.join(encrypted_output_folder, encrypted_file)),
        'sha3-256': crypto.sha3_256(os.path.join(encrypted_output_folder, encrypted_file))
        }
    
    return output




@app.route("/encrypt/<id>", methods=['GET'])
def path_encrypt_download(id):
    try:
        return send_from_directory(encrypted_output_folder, filename=id, as_attachment=True)
    except FileNotFoundError:
        abort(404)




@app.route("/decrypt", methods=['POST'])
def path_decrypt():

    # get password
    if request.form.get('password'):
        password = request.form.get('password')
    else:
        error_message = {'error': 'missing password parameter'}
        error_code = 400
        return error_message, error_code
    print(password)
    # write file to disk
    stored_file = store_file(request.files, encrypted_uploads_folder)
    if stored_file[0] == False:
        error_message = stored_file[1]
        error_code = stored_file[2]
        return error_message, error_code
    
    output_file = crypto.decrypt_aes_cbc(stored_file, decrypted_output_folder, password)

    output = {
        'download url': url_for('path_decrypt_download', id=output_file)
    }

    return output
    




@app.route("/decrypt/<id>", methods=['GET'])
def path_decrypt_download(id):
    try:
        return send_from_directory(decrypted_output_folder, filename=id, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# -----------------------------------------------------------------------------
# helper methods
# -----------------------------------------------------------------------------







# -----------------------------------------------------------------------------
# runner
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0')