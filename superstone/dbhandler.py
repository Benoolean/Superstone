from flask import Flask, Blueprint, request, session, render_template, redirect, jsonify
from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import secure_filename
from bson import json_util, ObjectId
from pymongo import MongoClient
import json
import uuid
import gridfs
import pandas as pd

import templater
import main

dbhandler = Blueprint('dbhandler', __name__)

client = MongoClient('localhost', 27017)
database = client.superstone
collection = database.stone  # default collection set to stone

fs = gridfs.GridFS(database)  # init gridfs collection


'''
Operations
'''


def insert_one(collection_name, query):
    collection = database[collection_name]
    if collection.insert_one(query).acknowledged:
        return True
    else:
        return 'Failed to insert_one into databse: ' + query

    return 'Unable to insert into database'


def insert_many(collection_name, query):
    collection = database[collection_name]
    return collection.insert_many(query)


def delete_one(collection_name, query):
    collection = database[collection_name]
    return collection.delete_one(query)


def find_one(collection_name, query):
    collection = database[collection_name]
    return json.loads(json_util.dumps(collection.find_one(query)))
    # returns None is nothing is there


def find_many(collection_name, query):
    collection = database[collection_name]
    return json.loads(json_util.dumps(collection.find(query)))


def get_uuid():
    return str(uuid.uuid4())


def insert_image(datafile, imageName, linkId, img_count):
    fs = gridfs.GridFS(database)
    stored = fs.put(datafile, fileName=imageName,
                    linkid=linkId, img_count=img_count)

    # This is used for storing images in /static/img/upload/ IF ENABLED MAKE SURE THE DIR EXISTS
    # for result in fs.find({'fileName':imageName}):
    #    newfile = open('static/img/uploads/' + result.fileName, 'a')
    #    newfile.write(result.read())


def find_one_image(query):
    #collection = database.fs.files
    return fs.find_one(query)


'''
End of Operations
'''


@dbhandler.route('/admin/login', methods=['POST'])
def admin_login():
    if templater.new_login_form(request.form).validate_on_submit():
        query_check = {
            'username': request.form['username'],
            'password': request.form['password']
        }

        result = find_one('user', {'username': query_check['username']})

        if result == None:
            return render_template('login.html', form=templater.new_login_form(), error='Username or password is invalid')

        if result['password'] == query_check['password']:
            print 'Password is correct'
            session.permanent = True
            session['username'] = query_check['username']
            return redirect('/admin/insert_stone', code=302)

        else:
            print 'Wrong password'
            return render_template('login.html', form=templater.new_login_form(), error='Username or password is invalid')
    else:
        print 'All the form fields are required.'


@dbhandler.route('/admin/insert_stone', methods=['POST'])
def insert_stone():
    if 'username' not in session:
        return redirect('/admin/login', code=302)

    if templater.new_stone_form(request.form).validate_on_submit():

        query_insert = {
            'series': request.form['series'],
            'name': request.form['name'],
            'stoneid': get_uuid(),
            'sub_description': request.form['sub_description'],
            'price': request.form['price'],
            'detail_description': request.form['detail_description'],
        }

        img_count = 0
        for photo in request.files.getlist('photo'):
            img_count = img_count + 1
            filename = secure_filename(photo.filename)
            datafile = photo.read()
            insert_image(datafile, filename,
                         query_insert['stoneid'], img_count)

        query_insert['image_count'] = img_count
        insert_one('stone', query_insert)
    else:
        return jsonify({'status': 'All fields must be filled'})


@dbhandler.route('/admin/insert_stone_csv', methods=['POST'])
def insert_stone_csv():
    if 'username' not in session:
        return redirect('/admin/login', code=302)

    df = pd.read_csv(request.files['csv'])

    form_list = []
    for stone in range(0, df.count().series):
        # return file upload per stone
        form_csv = {
            'series':  df.loc[[stone], ['series']].values[0][0],
            'name':  df.loc[[stone], ['name']].values[0][0],
            'sub_description': df.loc[[stone], ['sub_description']].values[0][0],
            'price': df.loc[[stone], ['price']].values[0][0],
            'detail_description': df.loc[[stone], ['detail_description']].values[0][0],
            'form': templater.new_csv_multi_edit_form()
        }

        # send the stone to the data base with imgcount of NONE. Update imgcount later with other form.
        # didnt make it yet because the CSV file is off.
        form_list.append(form_csv)

    return render_template('insert_stone.html', new_csv_multi_edit_form=form_list)

@dbhandler.route('/admin/insert_stone_csv/confirm', methods=['POST'])
def insert_stone_csv_confirm():
    if 'username' not in session:
        return redirect('/admin/login', code=302)

    print request.files.getlist('photo')

    if templater.new_csv_multi_edit_form(request.form).validate_on_submit() and len(request.files.getlist('photo')) > 0:
        query_insert = {
            'series': request.form['series'],
            'name': request.form['name'],
            'stoneid': get_uuid(),
            'sub_description': request.form['sub_description'],
            'price': len(request.form['price']),
            'detail_description': request.form['detail_description'],
        }

        img_count = 0
        for photo in request.files.getlist('photo'):
            img_count = img_count + 1
            filename = secure_filename(photo.filename)
            datafile = photo.read()
            insert_image(datafile, filename,
                         query_insert['stoneid'], img_count)

        query_insert['image_count'] = img_count
        insert_one('stone', query_insert)
        return jsonify({'status': 'Success', 'Inserted' : str(query_insert)})

    else: 
        return jsonify({'status': 'All fields must be filled'})