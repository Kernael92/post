
from quart import Quart, render_template, request, redirect, url_for, session, flash
from bson import ObjectId
# for ObjectId to work
from pymongo import MongoClient
import json
import flask_login  



app = Quart(__name__)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.blog
blogs = db.blog 
myusers = db.users

db.init_app(app)

class User(db.document, login.UserMixin):
    id = db.IntergerField(primary_key=True)
    username = db.StringField(max_length=40, required=True)
    password = db.StringField(max_length=40)

    # Relationships
    roles = db.ListField(db.StringField(), defaul=[])

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

    def str(self):
        return self.username



