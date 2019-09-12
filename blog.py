
from quart import Quart, render_template, request, redirect, url_for, session, flash
from bson import ObjectId

# for ObjectId to work
from pymongo import MongoClient
import json
import flask_login
from flask_login import UserMixin  
from wtforms  import form, fields


# create application
app = Quart(__name__)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.blog
blogs = db.blog 
myusers = db.users

# db.init_app(app)

ACCESS = {
    'guest': 0,
    'user': 1,
    'admin': 2,
}

class User(UserMixin):
    def __init__(self, id, username, password, access=ACCESS['user']):
        self.id = id
        self.username = username
        self.password = password
        self.access = access

    # Flask-login integration 
    # Note: is_authenticated, is_active, and is_anonymous are
    # methods in Flask-login

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False 

    @property 
    def get_id(self):
        return self.id 

    def is_admin(self):
        return self.access == ACCESS['admin']

    def allowed(self, access_level):
        return self.access > access_level


    def str(self):
        return self.username



