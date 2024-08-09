from flask import Flask, render_template, request, config
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.sql import functions
from sqlalchemy import create_engine
from flask_login import (UserMixin)
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123poi098@localhost:5432/saby_combat'
db = SQLAlchemy(app)

engine = db.create_engine("postgresql+psycopg2://postgres:123poi098@localhost:5432/saby_combat", echo=False)
conn = engine.connect()
Session = db.sessionmaker(bind=engine)
session = db.Session()

# db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.get('/')
def index():
    return render_template('admin.html')

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    patronymic = db.Column(db.String(30))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), server_default=functions.now())
    blocked = db.Column(db.Boolean(), default=False)
    clan_id = db.Column(db.Integer())
    referral_link = db.Column(db.String(40), nullable=False)

class Upgrades(db.Model):
    __tablename__ = 'upgrades'
    id = db.Column(db.Integer(), primary_key=True)
    upgrade_name = db.Column(db.String(100), unique=True, nullable=False)
    upgrade_image = db.Column(db.String(255))
    base_cost = db.Column(db.BigInteger(), nullable=False)
    coins_per_second = db.Column(db.BigInteger(), nullable=False)
    cost_multiplier = db.Column(db.Integer(), nullable=False)

class Levels(db.Model):
    __tablename__ = 'levels'
    id = db.Column(db.Integer(), primary_key=True)
    level_name = db.Column(db.String(50), nullable=False)
    coins_required = db.Column(db.BigInteger(), nullable=False)
    coins_per_click = db.Column(db.Integer(), nullable=False)


admin = Admin(app, name='Панель администратора', template_mode='bootstrap3')
admin.add_view(ModelView(Users, db.session, name='Пользователи'))
admin.add_view(ModelView(Upgrades, db.session, name='Магазин'))
admin.add_view(ModelView(Levels, db.session, name='Уровни'))


if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)

