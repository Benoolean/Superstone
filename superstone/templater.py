from flask import Flask, Blueprint, render_template, request, jsonify, Response, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, NumberRange

from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import secure_filename
from bson import json_util
from pymongo import MongoClient
import os, json, pymongo, gridfs

import db_stone, db_user, main

client = MongoClient('localhost', 27017)
database = client.superstone

templater = Blueprint('templater', __name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class new_stone_form(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    sub_description = StringField('Sub Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[NumberRange(min=0)])
    detail_description = StringField('Description', validators=[DataRequired()])
    photo = FileField('Photo', validators=[FileRequired()])

class new_login_form(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])

'''
Template Render
'''

@templater.route('/')
def main_page():
    return render_template('index.html')

@templater.route('/admin/login', methods=['POST', 'GET'])
def admin_login():
    if 'username' in session:
        return redirect('http://www.google.com', code=200)
        
    form = new_login_form()
    if request.method == 'POST':
        if form.validate():
            query_check = {
                'username' : request.form['username'],
                'password' : request.form['password']
            }

            result = db_user.find_one({'username' : query_check['username']})
            if result == None:
                return render_template('login.html', form=form, error='Username or password is invalid')

            if result['password'] == query_check['password']:
                print 'Password is correct'
                session.permanent = True
                session['username'] = query_check['username']
            else:
                print 'Wrong password'
                return render_template('login.html', form=form, error='Username or password is invalid')
        else:
            print 'All the form fields are required.'

    return render_template('login.html', form=form)

@templater.route('/admin/insert_stone', methods=['POST', 'GET'])
def contact_page():
    form = new_stone_form()
    if request.method == 'POST':
        if form.validate():
            query_insert = {
                'name' : request.form['name'],
                'stoneid' : db_stone.get_uuid(),
                'sub_description' : request.form['sub_description'],
                'price' : request.form['price'],
                'detail_description' : request.form['detail_description'],
            }

            img_count = 0
            for photo in request.files.getlist('photo'):
                img_count = img_count + 1
                print photo
                filename = secure_filename(photo.filename)
                datafile = photo.read()
                db_stone.insert_image(datafile, filename , query_insert['stoneid'], img_count)

            query_insert['image_count'] = img_count
            db_stone.insert_one(query_insert)
            '''
            file = request.files['photo']
            filename = secure_filename(file.filename)
            
            datafile = file.read()
            db_stone.insert_image(datafile, filename, query_insert['stoneid'])
            db_stone.insert_one(query_insert)
            '''
        else:
            print 'All the form fields are required.'

    return render_template('insert_stone.html', form=form)

@templater.route('/products')
def product_page():
    return render_template('projects.html')

'''
End of Template Render
'''

'''
POST Method
'''

'''
End of POST Method
'''

'''
GET Method
'''

@templater.route('/stone/detail/<stoneid>', methods=['GET'])
def stone_details(stoneid):
    query_return = db_stone.find_one({'stoneid' : str(stoneid)})
    if query_return == None:
        return redirect('http://www.google.com', code=302)

    img_urls = []
    for image_count in range(1,query_return['image_count'] + 1):
        url = '/stone/photo/static/view/' + stoneid + '/' + str(image_count)
        img_urls.append(str(url))

    if query_return == None:
        return redirect("http://www.google.com", code=302)

    return render_template('stone-detail.html', json=query_return, img_urls=img_urls)

@templater.route('/stone/list', methods=['GET'])
def stone_list():
    query_return = db_stone.find_many({}) #returns everything
    if query_return == None:
        return redirect("http://www.google.com", code=302)

    return render_template('stone-list.html', json=query_return)

@templater.route('/stone/photo/static/view/<linkid>/<count>', methods=['GET'])
def stone_photo(linkid, count):
    fs = gridfs.GridFS(database)
    
    query_return = db_stone.find_one_image({'linkid': linkid, 'img_count': int(count)})
    if query_return == None:
        return redirect('http://www.google.com', code=302)

    print query_return
    return Response(query_return, mimetype='image/jpeg')

'''
End of GET Method
'''

