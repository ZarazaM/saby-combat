from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from saby_combat import db

# Нужно по id пользователя из таблицы Users найти его друзей из таблицы friends
# из полученных результатов сформировать таблицу с возможностью прокрутки
# Решение написать запрос на ORM SQLAlchemy:
# Select friend_id, user_name, surname, name, patronymic, clicks_count, total_coins
# FROM Users as u JOIN user_coins ON user_coins.user_id = u.id JOIN friends ON friends.user_id = u.id
# Where u.id = <идентификатор пользователя, для которого выбираем друзей>
# Оформить html код страницы для отображения все пользователей

app = Flask(__name__)

engine = db.create_engine("postgresql+psycopg2://postgres:qwerty@localhost:5432/saby_combat", echo=True)
engine.connect()
Session = db.sessionmaker(bind=engine)
session = db.Session()

@app.route('/community/<int:user_id>')
def get_friends(user_id):
    try:
        friends_list = (
            session.query(
                db.friends.c.friend_id,
                db.Users.username,
                db.Users.surname,
                db.Users.name,
                db.Users.patronymic,
                db.UserCoins.click_count,
                db.UserCoins.total_coins
            )
            .join(db.Users, db.friends.c.friend_id == db.Users.id)
            .join(db.UserCoins, db.UserCoins.user_id == db.Users.id)
            .filter(db.friends.c.user_id == user_id)
            .all()
        )
        return render_template('friends.html', friends=friends_list)
    except Exception as e:
        return f"Произошла ошибка: {e}"


if __name__ == '__main__':
    app.run(debug=True)


# @app.route('/community')
# def list_friends():
#
#     return


# Необходимо разобраться с работой ORM SQL Alchemy. +
# Необходимо разобраться с работой python flask. +
# Реализовать базовый функционал: список друзей, добавление в друзья (по ссылке и через профиль пользователя).
# Проверить работу с базой данных: добавление, удаление, изменение, создание запросов.
# Создать ORM SQLAlchemy для таблицы friends и clans (если нужно).
# Написать скрипты на Flask: отображение базы данных с друзьями (корректное, т.е. можно без стиля).
# Написать скрипт на добавление пользователя по ссылке (т.е. создание уникальной ссылки по индентификатору
# пользователя).
# Добавление пользователей по кнопке (не мой функционал -- скорее всего не нужно).

