import quart.flask_patch 
import flask_login 
from flask_login import current_user, login_required, login_user, logout_user
from quart import Quart, render_template, request, redirect, url_for, session, flash, g, abort
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from bson import ObjectId
# from . import login_required
# for ObjectId to work
from pymongo import MongoClient
import json
from blog import User


app = Quart(__name__)
app.secret_key =b'\x85\x08\xcfu\xcd?\xff\xa9\x9a\xbfG\xd5\x9a\xa08\xf5'




client = MongoClient("mongodb://127.0.0.1:27017")
db = client.blog
blogs = db.blog 
myusers = db.users
roles = db.roles

# initialize flask-login 

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# create user loader function 
# @login_manager.user_loader
# def load_user(username):
#     user_id = User('username')
#     return user_id

@login_manager.user_loader
def user_loader(username):
    if username not in myusers.find():
        return

    user = User()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    password = request.form.get('password', '')
    access = request.form.get('access')
    if username not in myusers.find():
        return

    user = User()
    user.id = username
    user.is_authenticated = compare_digest(password, myusers[username]['password'])
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'unauthorized'





@app.route('/register', methods=('GET', 'POST'))
async def register():
    if request.method == 'POST':
        username = (await request.form)['username']
        password = (await request.form)['password']
        access = (await request.form)['access']


        error = None
        if not username:
            error = 'username is required'
        elif not password:
            error = 'Password is required'
        elif not access:
            error = 'Access is required'
        elif username in myusers.find():
            error = 'User {} is already registered'.format(username)

        if error is None:
            myusers.insert_one({'username':username, 'password':password, 'access':access})

            return redirect(url_for('login'))

        await flash(error)
        
    return await render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
async def login():
    if request.method == 'POST':
        # user = User()
        username = (await request.form)['username']
        password = (await request.form)['password']
        access = (await request.form)['access']


        error = None

        for user in myusers.find( ):
            if user is None:
                error = 'Incorrect username'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password'    
            elif not user['access']:
                error = 'Incorrect access'
            if error is None:
                flask_login.login_user(user)
                session.clear()
                session[user_id] = user['_id']
            await flash('Logged in successfully')
            return redirect(url_for('members'))

        await flash(error)       
    return await render_template('login.html')

@app.route('/logout')
async def logout():
    flask_login.logout_user()
    # session.clear()
    myusers.delete_one({})
    return redirect(url_for('index'))

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


@app.route('/roles')
async def roles():
    if request.method == 'POST':
        name = (await request.form)['admin']
        error = None

        if not name:
            error = 'name is required'
        if error is not None:
            await flash(error)
        else:
            roles.insert({'admin':name})
            return redirect (url_for('index'))
            
    return await render_template('roles.html')


@app.before_request
def load_logged_in_role():
    role_id = session.get('role_id', '_id')

    if role_id is None:
        g.role = None 
    else:
        g.role = roles
        print(g.role)

def role_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.role is None:
            return redirect(url_for('roles'))
        return view(**kwargs)

    return wrapped_view




@app.route('/', methods=['GET'])
async def index():
    # Displays posts
    blogs_1 = blogs.find()
    users = myusers.find()
    print(db.list_collection_names())
    

    # for blog in blogs.find():
    #     print(blog)

    
    
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
            await flash(error)
        else:
            blogs.insert_one({'title': title, 'body': body})

            return redirect(url_for('members'))

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
            print(myusers.find())
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
            await flash(error)
        elif  g.user['access'] == 'admin':
            blogs.find_one_and_update({'title':{'$regex':blog['title']}, 'body':{'$regex':blog['body']}}, {'$set':{'title':title}, '$set':{'body':body}})
            return redirect(url_for('index'))
        else:
            await flash('Only admin can edit a post')
            return redirect(url_for('index'))
    return await render_template('update.html', blog=blog)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
async def delete(id):
    get_post(id)
    blogs.find_one_and_delete()
    return redirect(url_for('index'))

# The home page is accessible to anyone
@app.route('/home')
async def home():
    return await render_template('home.html')


# The user page is accessible to authenticated users(users that have logged in)
@app.route('/members')
@login_required
async def members():
    if not g.user:
        return redirect(url_for('register'))
    return await render_template('members.html')


# The admin page is to users with the 'admin' role
@app.route('/admin')
@role_required
async def admin():
    # for user in myusers.find():
    if not g.user['access'] == 'admin':
        await flash("You do not have access to that page. Sorry!")
        return redirect(url_for('members'))   
    return await render_template('admin.html')


# @app.route('/comment/<int:id>', methods = ['GET', 'POST'])
# async def comment(id):
#     blog = get_post(id)

#     if request.method == 'POST':
#         text = (await request.form)['text']



        








if __name__ == '__main__':
    app.run(debug = True)