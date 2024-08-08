import secrets

from flask import Flask, render_template, request, redirect, url_for, abort
# from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.sql import text
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired, Length


# Переход на страницу друзья доступен только для зарегистрированных пользователей.
# Добавить оформление списка друзей как на слайдах.
#
# О добавлении друзей по ссылке: если пользователь перешёл по ней, то он перенаправлен на страницу регистрации или
# входа. После нужно создать запись в таблице friends. После нужно (возможно реактивно) отобразить новый список друзей.



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123poi098@localhost:5432/saby_combat'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)

engine = db.create_engine("postgresql+psycopg2://postgres:123poi098@localhost:5432/saby_combat", echo=False)
conn = engine.connect()
Session = db.sessionmaker(bind=engine)
session = db.Session()

referral_link = 'zmuipswjy'
# referral_link = 'tosjchekg'
# referral_link = 'sgyjlkjty'


class ClanForm(FlaskForm):
    clan_name = StringField("Имя клана: ", validators=[DataRequired(), Length(min=5, max=30)])
    submit = SubmitField("Создать клан")


# Это основной интерфейс для взаимодействия со страницей друзья.
@app.route('/community', methods=['GET', 'POST'])
# @login_required
def community():
    fr_data = table_friends(referral_link)  # друзья
    clan__id = is_in_clan(referral_link)  # клан пользователя
    clan_info = None
    members = None
    clan_form = ClanForm()
    if clan__id:  # если пользователь находится в клане, то получим информацию о его клане
        clan_info, members = table_clans(referral_link)
    view_invitations = clan_invitations_view(referral_link)  # информация о приглашениях в клан
    if clan__id is None and is_leader(referral_link) is None and clan_form.validate_on_submit():
        action_clan = clan_form.submit.data
        print('Что-то')
        print(f'action_clan = {clan_form.clan_name.data}')
        if clan_form.clan_name.data is not None:
            create_clan(referral_link, clan_form.clan_name.data)
            print(f'clan_info = {clan_info}')
            return redirect(url_for('community'))

    if request.method == 'POST' and is_leader(referral_link) is None:
        action = request.form.get('do_user')  # информация о действии пользователя относительно приглашений в кланы
        clan_name = request.form.get('invitation_id')
        clan_id1 = for_name(clan_name)
        invitation_id = id_invitations(clan_id1, referral_link)
        if action == 'accept':
            clan_invitation_from_user(referral_link, 'accept', invitation_id)
        elif action == 'decline':
            clan_invitation_from_user(referral_link, 'decline', invitation_id)
        return redirect(url_for('community'))

    # управление кланом: есть клан, пользователь -- лидер и это POST запрос.
    if clan__id is not None and is_leader(referral_link) is not None and request.method == 'POST':
        action_leader = request.form.get('management')
        if action_leader == 'delete_clan':
            delete_clan(clan__id)
            return redirect(url_for('community'))
        elif action_leader == 'add_user':
            invite_user(referral_link, clan__id)
            return redirect(url_for('community'))
    if clan__id:
        leader_id = is_leader(referral_link)
        if leader_id:
            return render_template('friends.html',
                                   friends=fr_data, referral_link=referral_link, clan_id=clan__id, clan_info=clan_info,
                                   members=members, invitations=view_invitations, is__leader=True, form=clan_form)
        else:
            return render_template('friends.html',
                                   friends=fr_data, referral_link=referral_link, clan_id=clan__id, clan_info=clan_info,
                                   members=members, invitations=view_invitations, is__leader=False, form=clan_form)
    else:
        return render_template('friends.html',
                               friends=fr_data, referral_link=referral_link, clan_id=clan__id, clan_info=clan_info,
                               members=members, invitations=view_invitations, form=clan_form)


def id_invitations(clan_id1, referral_link1):
    id_invitation = conn.execute(text("""
    SELECT cl_in.invitation_id FROM clan_invitations AS cl_in JOIN users AS u ON u.id = cl_in.user_id
    WHERE cl_in.clan_id = :cl_id AND u.referral_link = :ref_link;
    """).params(cl_id=clan_id1, ref_link=referral_link1)).scalar()
    return id_invitation


# Добавь функцию, что ник каждого пользователя на странице является реферальной ссылкой -- это не нужно уже.
def table_friends(referral_link):
    query_friend = text('''
    SELECT ui.profile_picture, u.username, u.surname, u.name, u.patronymic, uc.click_count, uc.total_coins
    FROM users as u JOIN friends as fr ON fr.friend_id = u.id
    JOIN user_coins as uc ON uc.user_id = u.id
    JOIN user_info as ui ON ui.user_id = u.id
    WHERE fr.user_id = (SELECT id FROM users WHERE referral_link = :referral_link);
    ''')
    sql_select = conn.execute(query_friend, {'referral_link': str(referral_link)})
    if len(sql_select.fetchall()) == 0:
        fr_date = {key: None for key in sql_select.keys()}
    else:
        fr_date = {key: [] for key in conn.execute(query_friend, {'referral_link': str(referral_link)}).keys()}
        for row in conn.execute(query_friend, {'referral_link': str(referral_link)}).fetchall():
            for key, value in zip(fr_date.keys(), row):
                fr_date[key].append(value)
    return fr_date


# Нужно отследить действия пользователя: при переходе на страницу регистрации или входа и валидации данных добавляется\
# запить в таблицу friends. А в случае перехода на страницу регистрации и валидации данных там, пользователь получит\
# дополнительно 10 000 монет.
def for_name(clan_name):
    id_clan = conn.execute(text("""
    SELECT id FROM clans WHERE clan_name = :cl_name
    """).params(cl_name=clan_name)).scalar()
    return id_clan


# Отображение списка кланов пользователя. Нужно сделать отдельные запросы на получение clan_id пользователя,
# статистики по клану пользователя и всех участников клана.
# Далее нужно отобразить всех пользователей клана в одной ячейке таблицы в виде списка.
# И отобразить остальные данные статистики по клану.
# !!!!!!!!!!!! Добавить возможность перехода на страницу профиля пользователя при нажатии на ник.!!!!!!!!!!!!!!!!!1!!!
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
    return clan_info, members


# если пользователь не в клане, возвращает False, иначе возвращает id клана.
def is_in_clan(referral_link):
    in__clan = text("""
            SELECT cl.id FROM clans AS cl JOIN users AS u ON u.clan_id = cl.id
            WHERE u.referral_link = :referral_link;
            """).params(referral_link=referral_link)
    select_in__clan = conn.execute(in__clan).scalar()
    if select_in__clan is None:
        return None
    return select_in__clan


# Приглашение пользователей в клан. Если пользователь не принадлежит клану, то у него высвечивается список/таблица
# приглашений с сообщениями: "{username} приглашает вас в клан {clan_name}", далее следуют две кнопки: "Отказаться"
# (она красная) и "Вступить" (она зелёная). Если пользователь отказывается от вступления, то это приглашение
# исчезает и удаляется соответствующая запись из таблицы clan_invitations. Если пользователь соглашается вступить в
# клан, то приглашение в клан, в который вступил пользователь исчезает и удаляется соответствующая запись из таблицы
# clan_invitations. Но все остальные приглашения остаются, так как пользователь может перейти в другой клан.


# Добавить кнопку выхода из клана!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# В этой функции я не уверен.!!!!!!!!!!!
# Отображение приглашений в кланы
# Статусы: 'pending', 'accepted', 'rejected'
def clan_invitations_view(referral_link):
    # добавить проверку на приглашения в кланы

    # Получаем ID пользователя
    user_id = conn.execute(text("""
                SELECT id FROM users WHERE referral_link = :referral_link
                """).params(referral_link=referral_link)).scalar()
    is_clan_invitations = conn.execute(text("""
        SELECT cl_in.clan_id FROM clan_invitations AS cl_in
        JOIN users AS u ON u.id = cl_in.user_id
        WHERE u.referral_link = :referral_link; """).params(referral_link=referral_link)).scalar()
    # Получаем все приглашения в кланы: лидер, клан.
    if is_clan_invitations is not None:  # результат возвращается в виде списка из двух кортежей
        view_invitation = conn.execute(text("""
        SELECT u.username, cl.clan_name
        FROM users AS u JOIN clans AS cl ON cl.id = u.clan_id
        JOIN clan_invitations AS cl_in ON cl_in.clan_id = cl.id
        WHERE cl_in.user_id = :user_id AND u.id = cl.leader_id
        """).params(user_id=user_id)).fetchall()
        # return community(view_invitation)
        return view_invitation
    return None


# Логика работы с кланами со стороны пользователя: вступить в клан, отказаться.
def clan_invitation_from_user(referral_link, action, invitation_id):
    if action == 'accept':  # если пользователь согласился вступить в клан, добавляем его, соблюдая численность.
        # ID клана
        select_clan_id = conn.execute(text("""
                SELECT cl.id FROM clans AS cl JOIN clan_invitations AS cl_in ON cl_in.clan_id = cl.id
                WHERE cl_in.invitation_id = :invitation_id;""").params(invitation_id=invitation_id)).scalar()
        is_open = conn.execute(text("""
        SELECT COUNT(*) FROM users AS u JOIN clans AS cl ON cl.id = u.clan_id
        WHERE cl.id = :cl_id
        """).params(cl_id=select_clan_id)).scalar()
        if select_clan_id != is_in_clan(referral_link) and is_leader(referral_link) is None:
            if is_open < 4:
                # Добавляем пользователя в клан
                conn.execute(text("""
                UPDATE users SET clan_id = :clan_id
                WHERE referral_link = :referral_link""").params(clan_id=select_clan_id, referral_link=referral_link))
                # удаляем приглашение пользователя в этот клан
                conn.execute(text("""
                DELETE FROM clan_invitations WHERE invitation_id = :invitation_id;
                """).params(invitation_id=invitation_id))
                conn.commit()
            elif is_open == 4:
                # Добавляем пользователя в клан
                conn.execute(text("""
                UPDATE users SET clan_id = :clan_id
                WHERE referral_link = :referral_link;""").params(clan_id=select_clan_id, referral_link=referral_link))
                # удаляем приглашение пользователя в этот клан
                conn.execute(text("""
                DELETE FROM clan_invitations WHERE invitation_id = 
                :invitation_id;""").params(invitation_id=invitation_id))
                # закрываем клан для вступления других пользователей
                conn.execute(text("""
                UPDATE clans SET is_open = FALSE WHERE clan_id = :clan_id;""").params(clan_id=select_clan_id))
                # Нужно удалить сообщение из видимой области в friends.html !!!!!!!!!!!!!!!!!!!!!!!!!!
                conn.commit()
            else:  # Возможно достаточно выводить уведомление!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                raise abort(400, desctiption='Sorry, but that clan is full')
    elif action == 'decline':
        # Нужно удалить сообщение из видимой области в friends.html !!!!!!!!!!!!!!!!!!!!!!!!!!
        conn.execute(text("""
                    DELETE FROM clan_invitations WHERE invitation_id = 
                    :invitation_id;""").params(invitation_id=invitation_id))
        conn.commit()
    return None


# Проверяет, является ли введённый пользователь лидером клана/////////// проверил
def is_leader(referral_link):
    leader__select = conn.execute(text("""
    SELECT cl.leader_id FROM clans AS cl JOIN users AS u ON u.clan_id = cl.id
    WHERE cl.leader_id = (SELECT id FROM users WHERE referral_link = :referral_link)
    """).params(referral_link=referral_link)).scalar()
    if leader__select is None:
        return None
    return leader__select


# Создание кланов.
# Если пользователь не находится в клане, то он может создать клан, при этом на странице community у пользователя
# появится таблица "Клан", при этом автоматический удалятся все приглашения.
# Изменения на странице должны происходить реактивно.
# Проверь эту функцию!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
def create_clan(referral_link, clan_name):
    # В противоположном случае при нажатии на соответствующую кнопку пользователь создаёт клан
    count_clan = conn.execute(text("""SELECT COUNT(*) FROM clans;""")).scalar()
    conn.execute(text("""
    INSERT INTO clans(id, clan_name, leader_id, is_open)
    VALUES (:id_clan,:clan_name, (SELECT id FROM users WHERE referral_link = :referral_link), TRUE)
    """).params(id_clan=count_clan + 1, clan_name=clan_name, referral_link=referral_link))
    # Добавляем лидера в клан
    conn.execute(text("""
    UPDATE users SET clan_id = :clan 
    WHERE referral_link = :referral_link;
    """).params(clan=count_clan + 1, referral_link=referral_link))
    conn.execute(text("""
    DELETE FROM clan_invitations
    WHERE user_id = (SELECT id FROM users WHERE referral_link = :referral_link)
    """).params(referral_link=referral_link))
    conn.commit()
    return None


# Управление кланом.
# Лидер клана может пригашать других пользователей, если количество пользователей в клане не более 5.
# Лидер клана может удалить клан. Лидер клана может при переходе на страницу профиля пользователя добавить его в клан.
def clan_management(referral_link):
    # Тут присутствует модуль проверки на то, что пользователь является лидером клана.
    # Возможно это отсутствует или является лишним по причине, что эта функция будет вызываться в интерфейсе страницы\
    # community.
    if is_leader(referral_link):
        clan_id = is_in_clan(referral_link)
        if request.method == 'POST':
            if request.form == 'delete_clan':
                delete_clan(clan_id)
                return redirect(url_for('community'))  # перенаправление на страницу друзья
            elif request.form == 'add_user':
                user_to_add = request.form['add_user']
                invite_user(user_to_add, clan_id)
                return redirect(url_for('community'))
    return referral_link


# Добавим проверку, что добавляемый пользователь не находится в клане, в противном случае функция вернёт False.
# Если пользователь не находится в клане, то у него формируется уведомление о приглашении в клан.
# А лидер нажимает на кнопку в профиле пользователя, и создаёт приглашение в клан.
# Лидер клана может добавлять в клан только друзей.

# Проверь SQL запросы.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
def invite_user(referral_link, clan_id):
    leader_id = conn.execute(text("""
    SELECT u.id FROM users AS u JOIN clans AS cl ON cl.id = u.clan_id
    WHERE cl.id = :clan_id AND u.id = cl.leader_id;
    """).params(clan_id=clan_id)).scalar()
    is_friend = conn.execute(text("""
    SELECT u.id FROM users AS u JOIN friends AS fr ON fr.user_id = u.id
    WHERE fr.user_id = :leader AND u.id = (SELECT id FROM users WHERE referral_link = :referral_link);
    """).params(leader=leader_id, referral_link=referral_link)).scalar()
    if is_in_clan(referral_link) is False and is_friend is not None:
        conn.execute(text("""
        INSERT INTO clan_invitations(user_id, clan_id, sender_id, status) 
        VALUES ((SELECT id FROM users WHERE referral_link = :referral_link), :clan__id, :sender__id, :status_str)
        """).params(referral_link=referral_link, clan__id=clan_id, sender__id=leader_id, status__str='pending'))
        conn.commit()
    else:
        return False


# убрать блок try:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
def delete_clan(clan_id):
    try:
        # получим id всех пользователей, входящих в клан
        users_in_clans = conn.execute(text("""
        SELECT u.id FROM users AS u JOIN clans AS cl ON cl.id = u.clan_id
        WHERE clan_id = :clan_id
        """).params(clan_id=clan_id)).fetchall()
        users = [users_in_clans[i][0] for i in range(len(users_in_clans))]
        # по полученным id произведём операции удаления пользователей из кланов
        for user in users:
            conn.execute(text("""
            UPDATE users SET clan_id = :clan_id WHERE id = :id""").params(clan_id=None, id=user))
        conn.execute(text("""
        DELETE FROM clans WHERE id = :cl_id
        """).params(cl_id=clan_id))
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
