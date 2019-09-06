from quart import Quart, render_template, request, redirect, url_for, session, flash
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

@app.route('/login/', methods = ['GET', 'POST'])
async def login():
    error = None 
    if request.method == 'POST':
        form = await request.form 
        if form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            return redirect(url_for('posts'))
    return await render_template('login.html', error = error)


@app.route('/logout/')
async def logout():
    session.po('logged_in', None)
    await flash('You are logged out')
    return redirect(url_for('posts'))



if __name__ == '__main__':
    app.run(debug = True)