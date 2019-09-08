
# from quart import Quart, render_template, request, redirect, url_for, session, flash
# from bson import ObjectId
# # for ObjectId to work
# from pymongo import MongoClient
# import json

# app = Quart(__name__)
# app.config.update({
#     'SECRET_KEY':b'\x85\x08\xcfu\xcd?\xff\xa9\x9a\xbfG\xd5\x9a\xa08\xf5',
#     'USERNAME': 'admin',
#     'PASSWORD': 'default',
# })





# client = MongoClient("mongodb://127.0.0.1:27017")
# db = client.blog
# blogs = db.blog 

# @app.route('/', methods=['GET'])
# async def index():
#     # Displays the form
#     return await render_template('index.html')

# @app.route('/posts')
# async def posts():
#     # dispalays all blogs
#     blogs_1 = blogs.find()
#     return await render_template('posts.html',  blogs=blogs_1)

    


# @app.route('/', methods = ['POST'])
# async def create():
#     if not session.get('logged_in'):
#         abort(401)
#     form = await request.form
    
#     mylist = list(form.values())

#     blogs.insert_one({"title":mylist[0], "text":mylist[1]})
#     print(client.list_database_names())
#     return redirect(url_for('posts'))

# @app.route('/login/', methods = ['GET', 'POST'])
# async def login():
#     error = None 
#     if request.method == 'POST':
#         form = await request.form 
#         if form['username'] != app.config['USERNAME']:
#             error = 'Invalid username'
#         elif form['password'] != app.config['PASSWORD']:
#             error = 'Invalid password'
#         else:
#             session['logged_in'] = True
#             await flash('You are logged in')
#             return redirect(url_for('index'))
#     return await render_template('login.html', error = error)


# @app.route('/logout/')
# async def logout():
#     session.po('logged_in', None)
#     await flash('You are logged out')
#     return redirect(url_for('/'))



# if __name__ == '__main__':
#     app.run(debug = True)