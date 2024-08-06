from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


# Нужно по id пользователя из таблицы Users найти его друзей из таблицы friends
# из полученных результатов сформировать таблицу с возможностью прокрутки
# Решение написать запрос на ORM SQLAlchemy:
# Select friend_id, user_name, surname, name, patronymic, clicks_count, total_coins
# FROM Users as u JOIN user_coins ON user_coins.user_id = u.id JOIN friends ON friends.user_id = u.id
# Where u.id = <идентификатор пользователя, для которого выбираем друзей>
# Оформить html код страницы для отображения все пользователей
# Добить разработанный функционал


# Разобраться с работой HTML, CSS, добить Alchemy и Flask
# Нужно сделать защиту: переход на страницу друзья доступен только для зарегистрированных пользователей.
# Пользователи, у которых нет друзей видят таблицу пустой.
# Добавить оформление списка друзей как на слайдах.
#
# О добавлении друзей по ссылке: если пользователь перешёл по ней, то он перенаправлен на страницу регистрации или
# входа. После нужно создать запись в таблице friends. После нужно (возможно реактивно) отобразить новый список друзей.
#
#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123poi098@localhost:5432/saby_combat'
db = SQLAlchemy(app)

engine = db.create_engine("postgresql+psycopg2://postgres:123poi098@localhost:5432/saby_combat", echo=False)
conn = engine.connect()
Session = db.sessionmaker(bind=engine)
session = db.Session()


@app.route('/community/<string:referral_link>')
def community(referral_link):
    query_friend = text('''
    SELECT ui.profile_picture, u.username, u.surname, u.name, u.patronymic, uc.click_count, uc.total_coins
    FROM users as u JOIN friends as fr ON fr.user_id = u.id
    JOIN user_coins as uc ON uc.user_id = u.id
    JOIN user_info as ui ON ui.user_id = u.id
    WHERE u.referral_link = :referral_link;
    ''')
    sql_select = conn.execute(query_friend, {'referral_link': str(referral_link)})
    if len(sql_select.fetchall()) == 0:
        fr_date = {key: None for key in sql_select.keys()}
        print(fr_date)
    else:
        fr_date = {key: [] for key in conn.execute(query_friend, {'referral_link': str(referral_link)}).keys()}
        for row in conn.execute(query_friend, {'referral_link': str(referral_link)}).fetchall():
            for key, value in zip(fr_date.keys(), row):
                fr_date[key].append(value)
    return render_template('friends.html', friends=fr_date)


# Нужно отследить действия пользователя: при переходе на страницу регистрации или входа и валидации данных добавляется\
# запить в таблицу friends. А в случае перехода на страницу регистрации и валидации данных там, пользователь получит\
# дополнительно 10 000 монет.
@app.route('/community/<string:referral_link>')
def invite_link(referral_link, methods='POST'):

    return render_template('friends.html', referral_link=referral_link)


# отображение списка кланов пользователя
@app.route('/community/<string:referral_link>')
def table_clans(referral_link):
    return render_template('friends.html', referral_link=referral_link)


# приглашение пользователей в клан
@app.route('/community/<string:referral_link>')
def clan_invations(referral_link):
    return render_template('friends.html', referral_link=referral_link)


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
