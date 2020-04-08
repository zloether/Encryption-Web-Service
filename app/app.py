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
from flask import Flask, request, render_template, Markup #, url_for
import markdown
import os.path
#import passgenerator



# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
app = Flask(__name__)
app_path = os.path.dirname(os.path.realpath(__file__))
templates_folder = os.path.join(app_path, 'templates')



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







# -----------------------------------------------------------------------------
# helper methods
# -----------------------------------------------------------------------------





# -----------------------------------------------------------------------------
# runner
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0')