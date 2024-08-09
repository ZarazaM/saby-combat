from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os, config
from flask_caching import Cache
from sqlalchemy import create_engine

app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.DevelopmentConfig')

db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
db_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
cache = Cache(app)
from . import views
