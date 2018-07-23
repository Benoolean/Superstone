from flask import Flask, Blueprint, request
from werkzeug.datastructures import ImmutableDict
from bson import json_util, ObjectId
from pymongo import MongoClient
import json
import uuid

db_stone = Blueprint('db_user', __name__)

client = MongoClient('localhost', 27017)
database = client.superstone
collection = database.user

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
