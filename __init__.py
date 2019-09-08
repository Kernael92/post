import os 

from quart import Quart 

def create_app(test_config=None):
    #  Create and configure the app 
    app = Quart(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=b'v\xe2\x8e\x0cI\xff\x16\x8c\xf3\x8e9\xfb\xcf0[\xad',
        DATABASE=os.path.join(app.instance_path, 'app.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing 
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    async def hello():
        return 'Hello'

    return app