from flask import Flask, Blueprint, render_template, request, jsonify, Response, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, NumberRange

from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import secure_filename
from bson import json_util
from pymongo import MongoClient
import os
import json
import pymongo
import gridfs
import pandas as pd

import dbhandler
import main

client = MongoClient('localhost', 27017)
database = client.superstone

templater = Blueprint('templater', __name__)


class new_stone_form(FlaskForm):
    series = StringField('Series', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    sub_description = StringField('Sub Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[NumberRange(min=0)])
    detail_description = StringField('Description', validators=[DataRequired()])
    photo = FileField('Photo', validators=[FileRequired(), FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')])


class new_csv_upload_form(FlaskForm):
    csv = FileField('CSV', validators=[FileRequired(), FileAllowed(['csv'], 'CSV only!')])


class new_csv_multi_edit_form(FlaskForm):
    series = StringField('Series', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    sub_description = StringField('Sub Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[NumberRange(min=0)])
    detail_description = StringField('Description', validators=[DataRequired()])
    photo = FileField('Photo', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')])


class new_login_form(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])


'''
Template Render
'''


@templater.route('/')
def main_page():
    return render_template('index.html')


@templater.route('/admin/login', methods=['GET'])
def admin_login_page():
    if 'username' in session:
        return redirect('/admin/insert_stone', code=302)
    return render_template('login.html', new_login_form=new_login_form())


@templater.route('/admin/insert_stone', methods=['GET'])
def insert_stone_page():
    if 'username' not in session:
        return redirect('/admin/login', code=302)
    return render_template('insert_stone.html', new_stone_form=new_stone_form())


@templater.route('/admin/insert_stone_csv', methods=['GET'])
def insert_stone_csv_page():
    if 'username' not in session:
        return redirect('/admin/login', code=302)
    return render_template('insert_stone.html', new_csv_upload_form=new_csv_upload_form())


@templater.route('/products', methods=['GET'])
def product_page():
    return redirect('/stone/list', code=302)


@templater.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')

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
    query_return = dbhandler.find_one('stone', {'stoneid': str(stoneid)})
    if query_return == None:
        return redirect('http://www.google.com', code=302)

    img_urls = []
    for image_count in range(1, query_return['image_count'] + 1):
        url = '/stone/photo/static/view/' + stoneid + '/' + str(image_count)
        img_urls.append(str(url))

    if query_return == None:
        return redirect("http://www.google.com", code=302)

    return render_template('stone-detail.html', json=query_return, img_urls=img_urls)


@templater.route('/stone/list', methods=['GET'])
def stone_list():
    query_return = dbhandler.find_many('stone', {})  # returns everything
    if query_return == None:
        return redirect("http://www.google.com", code=302)

    return render_template('stone-list.html', json=query_return)


@templater.route('/stone/photo/static/view/<linkid>/<count>', methods=['GET'])
def stone_photo(linkid, count):
    fs = gridfs.GridFS(database)

    query_return = dbhandler.find_one_image({'linkid': linkid, 'img_count': int(count)})
    if query_return == None:
        return redirect('http://www.google.com', code=302)

    print query_return
    return Response(query_return, mimetype='image/jpeg')


'''
End of GET Method
'''
