from flask import Flask, render_template, request, jsonify, Response, session, redirect
from datetime import timedelta
from templater import templater
from db_stone import db_stone

import datetime, os

#test
app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'upload/'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.register_blueprint(templater)
app.register_blueprint(db_stone)

app.secret_key= 'secretpassword'
app.permanent_session_lifetime = timedelta(minutes=5)


if __name__ == '__main__':
    print app.url_map
    app.run()
