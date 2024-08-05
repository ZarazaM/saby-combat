from saby_combat import db, login_manager
from sqlalchemy.sql import functions
from flask_login import (UserMixin, login_required, login_user, current_user, logout_user)
from werkzeug.security import generate_password_hash, check_password_hash


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
    
    def compare_password(self, plain_text_password):
        return check_password_hash(self.password_hash, plain_text_password)

    # Получается, что эти свойства вообще не нужны, 
    # если делать все через текстовые запросы?
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = generate_password_hash(plain_text_password)


friends = db.Table('friends',
                   db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
                   db.Column('friend_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')))


class Upgrades(db.Model):
    __tablename__ = 'upgrades'
    id = db.Column(db.Integer(), primary_key=True)
    upgrade_name = db.Column(db.String(100), unique=True, nullable=False)
    upgrade_image = db.Column(db.String(255))
    base_cost = db.Column(db.BigInteger(), nullable=False)
    coins_per_second = db.Column(db.BigInteger(), nullable=False)
    cost_multiplier = db.Column(db.Integer(), nullable=False)


user_upgrades = db.Table('user_upgrades',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
                         db.Column('upgrade_id', db.Integer, db.ForeignKey('upgrades.id', ondelete='CASCADE')),
                         db.Column('quantity', db.Integer, default=0))


class UserVerification(db.Model):
    __tablename__ = 'user_verification'
    user_id = db.Column(db.Integer(), primary_key=True)
    email_verified = db.Column(db.Boolean(), default=False)
    verified_on = db.Column(db.DateTime())


class Levels(db.Model):
    __tablename__ = 'levels'
    id = db.Column(db.Integer(), primary_key=True)
    level_name = db.Column(db.String(50), nullable=False)
    coins_required = db.Column(db.BigInteger(), nullable=False)
    coins_per_click = db.Column(db.Integer(), nullable=False)


class UserCoins(db.Model):
    __tablename__ = 'user_coins'
    user_id = db.Column(db.Integer(), primary_key=True)
    total_coins = db.Column(db.BigInteger(), default=0)
    current_coins = db.Column(db.BigInteger(), default=0)
    click_count = db.Column(db.Integer(), default=0)
    coins_per_second = db.Column(db.BigInteger(), default=0)
    level_id = db.Column(db.Integer(), db.ForeignKey('levels.id', ondelete='SET NULL'))


class UserInfo(db.Model):
    __tablename__ = 'user_info'
    user_id = db.Column(db.Integer(), primary_key=True)
    status = db.Column(db.String(30))
    description_profile = db.Column(db.String(120))
    profile_picture = db.Column(db.String(255))
    age = db.Column(db.SmallInteger())
    city = db.Column(db.String(30))
    gender = db.Column(db.SmallInteger())


class Clans(db.Model):
    __tablename__ = 'clans'
    id = db.Column(db.Integer(), primary_key=True)
    clan_name = db.Column(db.String(100), unique=True, nullable=False)
    leader_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    is_open = db.Column(db.Boolean(), default=True)


clan_invitations = db.Table('clan_invitations',
                            db.Column('invitation_id', db.Integer, primary_key=True),
                            db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
                            db.Column('clan_id', db.Integer, db.ForeignKey('clans.id', ondelete='CASCADE')),
                            db.Column('sender_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
                            db.Column('status', db.String(20), default='pending'))


@login_manager.user_loader
def load_user(user_id):
    # Возможно переписать получение пользователя через чистый SQL запрос
    return db.session.query(Users).get(user_id)
