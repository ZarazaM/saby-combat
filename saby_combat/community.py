from flask import Flask, render_template, request, redirect, url_for
# from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired

# Переход на страницу друзья доступен только для зарегистрированных пользователей.
# Добавить оформление списка друзей как на слайдах.
#
# О добавлении друзей по ссылке: если пользователь перешёл по ней, то он перенаправлен на страницу регистрации или
# входа. После нужно создать запись в таблице friends. После нужно (возможно реактивно) отобразить новый список друзей.
#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123poi098@localhost:5432/saby_combat'
db = SQLAlchemy(app)

engine = db.create_engine("postgresql+psycopg2://postgres:123poi098@localhost:5432/saby_combat", echo=False)
conn = engine.connect()
Session = db.sessionmaker(bind=engine)
session = db.Session()


# Добавь функцию, что ник каждого пользователя на странице является реферальной ссылкой.
@app.route('/community/<string:referral_link>')
# @login_required
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
    return render_template('friends.html', friends=fr_date, referral_link=referral_link)


# Нужно отследить действия пользователя: при переходе на страницу регистрации или входа и валидации данных добавляется\
# запить в таблицу friends. А в случае перехода на страницу регистрации и валидации данных там, пользователь получит\
# дополнительно 10 000 монет.
@app.route('/community/<string:referral_link>')
# @login_required
def invite_link(referral_link):
    return render_template('friends.html', referral_link=referral_link)


# Отображение списка кланов пользователя. Нужно сделать отдельные запросы на получение clan_id пользователя,
# статистики по клану пользователя и всех участников клана.
# Далее нужно отобразить всех пользователей клана в одной ячейке таблицы в виде списка.
# И отобразить остальные данные статистики по клану.
# !!!!!!!!!!!! Добавить возможность перехода на страницу профиля пользователя при нажатии на ник.!!!!!!!!!!!!!!!!!1!!!
@app.route('/community/<string:referral_link>')
# @login_required
def table_clans(referral_link):
    # тут запрос на получение clan_id пользователя -- возвращает одно значение
    query_clan_id = text("""
    SELECT cl.id FROM clans AS cl JOIN users AS us ON us.clan_id = cl.id
    WHERE us.referral_link = :referral_link;
    """)
    select_clan_id = conn.execute(query_clan_id, {'referral_link': str(referral_link)})
    row_clan = str(select_clan_id.fetchall()[0][0])  # clan_id для нашего пользователя
    # тут запрос для клана пользователя -- возвращает одномерный массив
    query_clans = text("""
    SELECT cl.clan_name,
    (SELECT u.username FROM users AS u JOIN clans AS cl ON cl.id = u.clan_id WHERE cl.id = :clan_id AND u.id 
    = cl.leader_id) AS leader, CAST(SUM(uc.click_count) AS varchar(30)) AS total_click, CAST(SUM(uc.total_coins) AS 
    varchar(30)) AS total_coins FROM clans AS cl JOIN users AS u ON u.clan_id = cl.id
    JOIN user_coins AS uc ON uc.user_id = u.id
    WHERE cl.id = :clan_id
    GROUP BY cl.clan_name;
    """)
    # Содержит строку: наименование клана, его лидера, общее количество заработанных монет и кликов.
    select_clans = conn.execute(query_clans, {'clan_id': str(row_clan)})
    clan_info = list(select_clans.fetchall()[0])
    # получение всех пользователей, состоящих в клане -- возвращает одномерный массив
    query_users = text("""
    SELECT us.username FROM users AS us JOIN clans AS cl ON cl.id = us.clan_id
    WHERE cl.id = :clan_id;
    """)
    select_users = conn.execute(query_users, {'clan_id': str(row_clan)}).fetchall()
    members = [select_users[i][0] for i in range(len(select_users))]
    return render_template('friends.html', referral_link=referral_link, clan_info=clan_info,
                           members=members)


# проверка, что пользователь с referral_link в клане !!!!!!!!!!! не проверял работу этой функции.
def is_in_clan(referral_link):
    in_clan = text("""
        SELECT cl.id FROM clan AS cl JOIN users AS u ON u.clan_id = cl.id
        WHERE u.referral_link = :referral_link;
        """).params(referral_link=referral_link)
    select_in_clan = conn.execute(in_clan).fetchall()
    if len(select_in_clan) == 0:
        return False
    return True


# Приглашение пользователей в клан. Если пользователь не принадлежит клану, то у него высвечивается список/таблица
# приглашений с сообщениями: "{username} приглашает вас в клан {clan_name}", далее следуют две кнопки: "Отказаться"
# (она красная) и "Вступить" (она зелёная). Если пользователь отказывается от вступления, то это приглашение
# исчезает и удаляется соответствующая запись из таблицы clan_invitations. Если пользователь соглашается вступить в
# клан, то все приглашения исчезают, а данные из таблицы clan_invitations удаляются, при этом появляется таблица со
# статистикой клана, в который вступил пользователь.


# В этой функции я не уверен.!!!!!!!!!!!
# Статусы: 'pending', 'accepted', 'rejected'
@app.route('/community/<string:referral_link>')
# @login_required
def clan_invitations_view(referral_link):
    if is_in_clan(referral_link):
        return table_clans(referral_link)
    else:
        if request.method == 'POST':
            select_user_id = text("""
            SELECT id FROM users WHERE referral_link = :referral_link
            """).params(referral_link=referral_link)
            user_id = conn.execute(select_user_id).fetchone()
            select_view_invitation = text("""
            SELECT u.username, cl.clan_name
            FROM users AS u JOIN clans AS cl ON cl.id = u.clan_id
            JOIN clan_invitations AS cl_in ON cl_in.clan_id = cl.id
            WHERE cl_in.user_id = :user_id AND u.id = cl.leader_id
            """).params(user_id=user_id)
            view_invitation = conn.execute(select_view_invitation).fetchall()
            # return community(view_invitation)
            return render_template('friends.html', view_invitation=view_invitation)

    return render_template('friends.html', referral_link=referral_link)


def clan_invitation_from_user(referral_link, action, invitation_id):
    if action == 'accept':  # если пользователь согласился вступить в клан, добавляем его, соблюдая численность.
        # ID клана
        select_clan_id = conn.execute(text("""
        SELECT cl.id FROM clans AS cl JOIN clan_invitations AS cl_in ON cl_in.clan_id = cl.id
        WHERE cl_in.id = :invitation_id
        """).params(invitation_id=invitation_id)).fetchone()
        is_open = conn.execute(text("""
        SELECT COUNT(*) FROM users AS u JOIN clans AS cl ON cl.id = u.clan_id
        WHERE cl.id = :cl_id
        """).params(cl_id=select_clan_id)).fetchone()
        if is_open < 4:
            # Добавляем пользователя в клан
            conn.execute(text("""
            UPDATE users SET clan_id = :clan_id
            WHERE referral_link = :referral_link
            """).params(clan_id=select_clan_id, referral_link=referral_link))
            # удаляем все приглашения для пользователя в другие кланы
            conn.execute(text("""
            DELETE FROM clan_invitations WHERE user_id = (SELECT id FROM users WHERE referral_link = :referral_link)
            """).params(referral_link=referral_link))
            conn.commit()
        elif is_open == 4:
            # Добавляем пользователя в клан
            conn.execute(text("""
            UPDATE users SET clan_id = :clan_id
            WHERE referral_link = :referral_link
            """).params(clan_id=select_clan_id, referral_link=referral_link))
            # удаляем все приглашения для пользователя в другие кланы
            conn.execute(text("""
            DELETE FROM clan_invitations WHERE user_id = (SELECT id FROM users WHERE referral_link = :referral_link)
            """).params(referral_link=referral_link))
            # удаляем все приглашения в кланы у пользователя
            conn.execute(text("""
            DELETE FROM clan_invitations AS cl_in JOIN users AS u ON u.id = cl_in.user_id
            WHERE u.referral_link = :referral_link;
            """).params(referral_link=referral_link))
            # добавляем пользователя в клан
            conn.execute(text("""
            UPDATE clans SET is_open = FALSE
            WHERE clan_id = :clan_id;
            """).params(clan_id=select_clan_id))
            # Нужно удалить сообщение из видимой области в friends.html !!!!!!!!!!!!!!!!!!!!!!!!!!
            conn.commit()
        else:
            raise Exception('Sorry, but that clan is full')
    elif action == 'decline':
        # Нужно удалить сообщение из видимой области в friends.html !!!!!!!!!!!!!!!!!!!!!!!!!!
        conn.execute(text("""
                    DELETE FROM clan_invitations WHERE id = :invitation_id
                    """).params(invitation_id=invitation_id))
        conn.commit()
    return redirect(url_for('friends_page'))  # в этом я не уверен !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# Создание кланов.
# Если пользователь не находится в клане, то он может создать клан, при этом на странице community у пользователя
# появится таблица "Клан", при этом автоматический удалятся все приглашения.
# Изменения на странице должны происходить реактивно.
# Проверь эту функцию!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
@app.route('/community/<string:referral_link>', methods='POST')
# @login_required
def create_clan(referral_link):  # если пользователь находится в клане => отображаем таблицу "Клан"
    if is_in_clan(referral_link):
        return table_clans(referral_link)
    else:  # В противоположном случае при нажатии на соответствующую кнопку пользователь создаёт клан
        if request.method == 'POST':
            if 'Создать клан' in request.form:
                clan_name = StringField("Имя клана: ", validators=[DataRequired()])
                insert_in_clan = text("""
                INSERT INTO clans(clan_name, leader_id, is_open)
                VALUES (:clan_name, (SELECT id FROM users WHERE referral_link = :referral_link), TRUE)
                """).params(clan_name=clan_name, referral_link=referral_link)
                conn.execute(insert_in_clan)
                conn.commit()
                return redirect(url_for('friends_page'))  # в этом я не уверен !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return render_template('friends.html',
                               referral_link=referral_link, in_clan=is_in_clan(referral_link))


def is_leader(referral_link):
    leader_select = conn.execute(text("""
    SELECT cl.leader_id FROM clans AS cl JOIN users AS u ON u.clan_id = cl.id
    WHERE cl.leader_id = (SELECT id FROM users WHERE referral_link = :referral_link)
    """).params(referral_link=referral_link)).fetchone()
    if len(leader_select) == 0:
        return False
    else:
        return True


# для получения клана пользователя
def is_clan_id(referral_link):
    cl_id = conn.execute(text("""
    SELECT clan_id FROM users WHERE referral_link = :referral_link
    """).params(referral_link=referral_link))
    return cl_id


# Управление кланом.
# Лидер клана может пригашать других пользователей, если количество пользователей в клане не более 5.
# Лидер клана может удалить клан. Лидер клана может при переходе на страницу профиля пользователя добавить его в клан.
@app.route('/community/<string:referral_link>')
# @login_required
def clan_management(referral_link):
    # Тут присутствует модуль проверки на то, что пользователь является лидером клана.
    # Возможно это отсутствует или является лишним по причине, что эта функция будет вызываться в интерфейсе страницы\
    # community.
    if is_leader(referral_link):
        clan_id = is_clan_id(referral_link)
        if request.method == 'POST':
            if request.form == 'delete_user':
                user_to_delete = request.form['delete_user']
                delete_user(user_to_delete)
                return redirect(url_for('community'))
            elif request.form == 'delete_clan':
                delete_clan(clan_id)
                return redirect(url_for('community'))  # перенаправление на страницу друзья
            elif request.form == 'add_user':
                user_to_add = request.form['add_user']
                invite_user(user_to_add, clan_id)
                return redirect(url_for('community'))
    return render_template('friends.html', referral_link=referral_link)


# Добавим проверку, что добавляемый пользователь не находится в клане, в противном случае функция вернёт False.
# Если пользователь не находится в клане, то у него формируется уведомление о приглашении в клан.
# А администратор нажимает на кнопку в профиле пользователя и создаёт приглашение в клан
def invite_user(referral_link, clan_id):
    if not is_in_clan(referral_link):
        conn.execute(text("""
        UPDATE users SET clan_id = :clan_id
        WHERE referral_link = :referral_link
        """).params(referral_link=referral_link, clan_id=clan_id))
        conn.commit()
    else:
        return False


# При удалении пользователя происходит изменение в таблице users: clan_id is Null
def delete_user(referral_link):
    if not is_in_clan(referral_link):
        conn.execute(text("""
        DELETE users SET clan_id = :clan_id
        WHERE referral_link = :referral_link
        """).params(clan_id=None, referral_link=referral_link))
    else:
        return False


def delete_clan(clan_id):
    try:
        # получим id всех пользователей, входящих в клан
        users_in_clans = conn.execute(text("""
        SELECT u.id FROM users AS u JOIN clans AS cl ON cl.id = u.clan_id
        WHERE clan_id = :clan_id
        """).params(clan_id=clan_id)).fetchmany(5)
        # по полученным id произведём операции удаления пользователей из кланов
        for user in users_in_clans:
            conn.execute(text("""
            UPDATE users SET clan_id = :clan_id WHERE id = :id""").params(clan_id=None, id=user))
        conn.commit()
    except RuntimeError:
        raise Exception('Something went wrong')


if __name__ == '__main__':
    app.run(debug=True)

# Необходимо разобраться с работой ORM SQL Alchemy. +
# Необходимо разобраться с работой python flask. +
# Реализовать базовый функционал: список друзей, добавление в друзья (по ссылке и через профиль пользователя).
# Проверить работу с базой данных: добавление, удаление, изменение, создание запросов.
# Создать ORM SQLAlchemy для таблицы friends и clans (если нужно).
# Написать скрипты на Flask: отображение базы данных с друзьями (корректное, т.е. можно без стиля). +
# Написать скрипт на добавление пользователя по ссылке (т.е. создание уникальной ссылки по индентификатору
# пользователя).
# Добавление пользователей по кнопке (не мой функционал -- скорее всего не нужно).
