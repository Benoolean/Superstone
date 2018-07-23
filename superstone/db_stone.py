from flask import Flask, Blueprint, request
from werkzeug.datastructures import ImmutableDict
from bson import json_util, ObjectId
from pymongo import MongoClient
import json
import uuid
import gridfs

db_stone = Blueprint('db_stone', __name__)

client = MongoClient('localhost', 27017)
database = client.superstone
collection = database.stone

fs = gridfs.GridFS(database)

stone = {
    "name"          : "This is a test stone",
    "picture_url"   : "www.stoneurl.com",
    "price"         : 100,
    "description"   : "this is the description of the stone, testing of how this actually works"
}

#collection.insert_one(stone)

'''
Main Database Operations
'''

def insert_one(query):
    if collection.insert_one(query).acknowledged:
        return True
    else:
        return 'Failed to insert_one into databse: ' + query
    
    return 'Unable to insert into database'

def insert_many(query):
    return collection.insert_many(query)

def delete_one(query):
    return collection.delete_one(query)

def find_one(query):
    return json.loads(json_util.dumps(collection.find_one(query))) 
    #returns None is nothing is there

def find_many(query):
    return json.loads(json_util.dumps(collection.find(query))) 


def get_uuid():
    return str(uuid.uuid4())

'''
End of Main Database Operations
'''

'''
Image Processing with GridFS
'''

def insert_image(datafile, imageName, linkId, img_count):
    fs = gridfs.GridFS(database)
    stored = fs.put(datafile, fileName=imageName, linkid=linkId, img_count=img_count)

    # This is used for storing images in /static/img/upload/ IF ENABLED MAKE SURE THE DIR EXISTS
    #for result in fs.find({'fileName':imageName}):
    #    newfile = open('static/img/uploads/' + result.fileName, 'a')
    #    newfile.write(result.read())

def find_one_image(query):
    #collection = database.fs.files
    return fs.find_one(query)

'''
End of Image Processing with GridFS
'''