import quart.flask_patch 
import flask_login 
from quart import Quart, render_template, request, redirect, url_for, session, flash
from secrets import compare_digest 
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

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# @login_manager.request_loader
# def request_loader(request):
#     username = request.form.get('username')
#     password = request.form.get('password', '')
#     if username not in users:
#         return 

#     user = User()
#     user.id = username 
#     user.is_authenticated = compare_digest(password, users[username]['password'])
#     return user 

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'unauthorized'


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

# @app.route('/login/', methods = ['GET', 'POST'])
# async def login():
#     error = None 
#     form = await request.form 
#     if request.method == 'POST':
#         user = User()
#         flask_login.login_user(user)
#         myusers = list(form.values())
#         users.insert_one({'_id':user_id,'username': myusers[0], 'password':myusers[1]})
#         await flash('You are logged in')
#         return redirect(url_for('create'))
#     return await render_template('login.html', form=form)   
#     #     if form['username'] != app.config['USERNAME']:
#     #         error = 'Invalid username'
#     #     elif form['password'] != app.config['PASSWORD']:
#     #         error = 'Invalid password'
#     #     else:
#     #         session['logged_in'] = True
#     #         await flash('You are logged in')
#     #         return redirect(url_for('posts'))
#     # return await render_template('login.html', error = error)
@app.route('/register', methods=('GET', 'POST'))
async def register():
    if request.method == 'POST':
        username = await request.form['username']
        password = await request.form['password']

        error = None
        if not username:
            error = 'username is required'
        elif not password:
            error = 'Password is required'
        elif username in users.find():
            error = 'User {} is already registered'.format(username)

        if error is None:
            users.insert_one({'username': username, 'password':password})

            return redirect(url_for('login'))

        flash(error)
        
    return await render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
async def login():
    if request.method == 'POST':
        username = await request.form['username']
        password = await request.form['password']

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











@app.route('/logout/')
async def logout():
    flask_login.logout_user()
    await flash('You are logged out')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug = True)