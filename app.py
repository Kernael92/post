import quart.flask_patch 
import flask_login 
from quart import Quart, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from bson import ObjectId
# for ObjectId to work
from pymongo import MongoClient
import json

app = Quart(__name__)
app.secret_key =b'\x85\x08\xcfu\xcd?\xff\xa9\x9a\xbfG\xd5\x9a\xa08\xf5'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.blog
blogs = db.blog 
myusers = db.users

@app.route('/', methods=['GET'])
async def index():
    # Displays the form
    return await render_template('index.html')

@app.route('/posts')
async def posts():
    # dispalays all blogs
    blogs_1 = blogs.find()
    return await render_template('posts.html',  blogs=blogs_1)

@app.route('/create', methods = ['POST'])
async def create():
    if request.method == 'POST':
        form = await request.form
    
        mylist = list(form.values())

        blogs.insert_one({"title":mylist[0], "text":mylist[1]})
        print(client.list_database_names())
        return redirect(url_for('posts'))
    return await render_template('create.html')


@app.route('/register', methods=('GET', 'POST'))
async def register():
    if request.method == 'POST':
        username = (await request.form)['username']
        password = (await request.form)['password']

        error = None
        if not username:
            error = 'username is required'
        elif not password:
            error = 'Password is required'
        elif username in myusers.find():
            error = 'User {} is already registered'.format(username)

        if error is None:
            myusers.insert_one({'username': username, 'password':password})

            return redirect(url_for('login'))

        flash(error)

    return await render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
async def login():
    if request.method == 'POST':
        username = (await request.form)['username']
        password = (await request.form)['password']

        error = None

        for user in myusers.find( ):
            if user is None:
                error = 'Incorrect username'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password'    
            if error is None:
                session.clear()
                session['user_id'] = user['id']
            return redirect(url_for('index'))

            flash(error)

    return await render_template('login.html')

# @app.before_app_request
# async def load_logged_in_user():
#     '''
#     Registers a function that runs before the view funcion
#     no matter what url is requested.
#     '''
#     user_id = await session.get('user_id')

#     if user_id is None:
#         g.user = None 
#     else:
#         g.user = myusers.find({'_id':user_id})

@app.route('/logout')
async def logout():
    session.clear()
    return redirect(url_for('index'))

async def login_required(view):
    @functools.wraps(view)
    async def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)

    return wrapped_view




if __name__ == '__main__':
    app.run(debug = True)