from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache  # important!

app = Flask(__name__)
app.config.from_object(Config)

### CACHE set up
cache = Cache(config={
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 0 # set to 0 to get always the latest files from download
})
cache.init_app(app)
###
db = SQLAlchemy(app)
migrate = Migrate(app,db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models

