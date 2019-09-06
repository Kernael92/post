from quart import Quart, render_template, request, redirect, url_for, session 
from bson import ObjectId
# for ObjectId to work
from pymongo import MongoClient
import json

app = Quart(__name__)
app.config.update({
    'SECRET_KEY': b'l\x95D,R9\xbe\xea\xe6+\xbd\x1be\xf0\xf76',
    'USERNAME': 'username',
    'PASSWORD': 'default',

})

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.blog
blogs = db.blog 

@app.route('/')
async def index():
    # Displays the form
    return await render_template('index.html')

@app.route('/posts')
async def posts():
    # dispalays all blogs
    blogs_1 = blogs.find()
    return await render_template('posts.html',  blogs=blogs_1)

    


@app.route('/', methods = ['POST'])
async def create():
    form = await request.form
    
    mylist = list(form.values())

    blogs.insert_one({"title":mylist[0], "text":mylist[1]})
    print(client.list_database_names())
    return redirect(url_for('posts'))

@app.route('/login')
def login():
    session['logged_in'] = True 
    pass



if __name__ == '__main__':
    app.run(debug = True)