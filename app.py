import quart.flask_patch 
import flask_login 
from quart import Quart, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from bson import ObjectId
# from . import login_required
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

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id', '_id')

    if user_id is None:
        g.user = None 
    else:
        g.user = myusers.find_one()
    print("before_request is running!")
    print(g.user)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)

    return wrapped_view


@app.route('/logout')
async def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/', methods=['GET'])
async def index():
    # Displays posts
    blogs_1 = blogs.find()
    users = myusers.find()
    print(db.list_collection_names())
    
    
    
    return await render_template('index.html', blogs=blogs_1, users=myusers)



@app.route('/create', methods = ['GET','POST'])
@login_required
async def create():
    if request.method == 'POST':
        title = (await request.form)['title']
        body = (await request.form)['body']
        error = None 

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            blogs.insert_one({'title': title, 'body': body})

            return redirect(url_for('index'))

    return await render_template('create.html')

def get_post(id, check_author=True):
    '''
    The function gets a blog post and calls it from both 
    the delete and update views 
    '''
    # blog = blogs.find_one()
    # user = myusers.find_one()
    for blog in blogs.find():
        if blog is None:
            abort(404, "Blog id {0} doesn't exist.".format(id))

    for user in myusers.find():
        if check_author and user['username'] != g.user['username']:
            abort (403)
    return blog

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
async def update(id):
    blog = get_post(id)

    if request.method == 'POST':
        title = (await request.form)['title']
        body = (await request.form)['body']
        error = None 

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            blogs.find_one_and_update({'title':{'$regex':blog['title']}, 'body':{'$regex':blog['body']}}, {'$set':{'title':title}, '$set':{'body':body}})
            return redirect(url_for('index'))
    return await render_template('update.html', blog=blog)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
async def delete(id):
    get_post(id)
    blogs.find_one_and_delete()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug = True)