import uuid
from flask import jsonify, abort
from flask_login import current_user
from flask_mail import Message
from datetime import datetime
from saby_combat import db, app, mail, db_engine
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from .models import Users, UserCoins
from . import db

# Отправляет email сообщение со ссылкой для подтверждения аккаунта
# на электронную почту с адресом 'to'
def send_confirmation_email(to: str, subject: str, html_template: str) -> None:
    message = Message(
        subject=subject,
        recipients=[to],
        html=html_template,
        sender=app.config["MAIL_DEFAULT_SENDER"]
    )
    mail.send(message)
    return


def send_referral_prize(referrer_uuid: str) -> None:
    query_status = db.session.execute(
        text(
            """
            UPDATE user_coins
            SET total_coins = total_coins + :prize, current_coins = current_coins + :prize
            WHERE user_id = (SELECT id FROM users WHERE referral_link = :referrer)
            RETURNING user_id
            """
        ).params(
            prize=10000,
            referrer=referrer_uuid
        )
    ).scalar()
    if query_status != None:
        db.session.commit()
        return
    else:
        abort(404, description="Некорректная реферальная ссылка")
        #raise Exception(f"Пользователь c uuid = {referrer_uuid} не найден")


def add_friend_by_uuid(user: Users, uuid: str) -> None:
    query_status = db.session.execute(
        text(
            """
            INSERT INTO friends(user_id, friend_id)
            (SELECT id, :user_id as friend
            FROM users
            WHERE referral_link = :user_uuid)
            RETURNING user_id
            """
        ).params(
            user_id=user.id,
            user_uuid=uuid
        )
    ).scalar()
    if query_status != None:
        db.session.commit()
        return
    else:
        abort(404, description=f"Пользователь c uuid = {uuid} не найден")
        #raise Exception(f"Пользователь c uuid = {uuid} не найден")


# Возвращает 'True', если пользователь подтвержден,
# иначе - 'False'
def is_user_confirmed(user: Users) -> bool:
    is_confirmed = db.session.execute(
        text(
            """
            SELECT email_verified
            FROM user_verification
            WHERE user_id=:user_id 
            """
        ).params(user_id=user.id)
    ).scalar()
    if is_confirmed != None:
        return is_confirmed
    else:
        raise Exception(f"Пользователь c id = {user.id} не найден")


# Задает значения, соответствующие подтвержденному пользователю
# в таблице 'user_verification' 
def confirm_user_email(user: Users) -> None:
    query_status = db.session.execute(
        text(
            """
            UPDATE user_verification
            SET email_verified=:verified, verified_on=:timestamp
            WHERE user_id=:user_id
            RETURNING user_id
            """
        ).params(
            verified=True,
            timestamp=datetime.now(),
            user_id=user.id
        )
    ).scalar()
    if query_status != None:
        db.session.commit()
        return
    else:
        raise Exception(f"Пользователь c id = {user.id} не найден")
    

def get_user_by_username(username: Users) -> Users:
    user = db.session.query(Users).from_statement(
        text("SELECT * FROM users where username=:uname").params(uname=username)
    ).first()
    return user


def get_user_by_email(email_adress: str) -> Users:
    user = db.session.query(Users).from_statement(
        text("SELECT * FROM users where email=:email").params(email=email_adress)
    ).first()
    return user


def is_existing_uuid(uuid: str) -> bool:
    query_status = db.session.execute(
        text(
            """
            SELECT id FROM users WHERE referral_link = :current_uuid
            """
        ).params(
            current_uuid=uuid
        )
    ).scalar()
    if query_status is None:
        return False
    return True



# Создает запись о новом пользователе по данным
# из 'form' во всех связанных с пользователем таблицах
# ('users', 'user_verification', 'user_coins', 'user_info').
def add_new_user(form) -> Users:
    # Инсерт нового пользователя в бд
    insert_user_query = text(
        """
        INSERT INTO users(username, name, surname, patronymic, email, password_hash, role, blocked, referral_link)
        values(:username, :name, :surname, :patronymic, :email, :pass_hash, :role, :blocked, :referral_link)
        """
    ).params(
        name=form.name.data,
        username=form.username.data,
        surname=form.surname.data,
        patronymic=form.patronymic.data,
        email=form.email_adress.data,
        pass_hash=generate_password_hash(form.password.data),
        role=False,
        blocked=False,
        referral_link=uuid.uuid4()
    )
    db.session.execute(insert_user_query)

    # Создаю локального пользователя для работы с сессиями 
    user = get_user_by_username(form.username.data)

    # Создание записи о верефикации пользователя в бд
    insert_user_verification_query = text(
        """
        INSERT INTO user_verification(user_id, email_verified)
        VALUES(:user_id, :email_verified)
        """
    ).params(
        user_id=user.id,
        email_verified=False
    )
    db.session.execute(insert_user_verification_query)

    # Создание записи о монетах пользователя в бд
    insert_user_coins_query = text(
        """
        INSERT INTO user_coins(user_id, total_coins, current_coins, click_count, coins_per_second, level_id)
        VALUES(:user_id, :total_coins, :current_coins, :click_count, :coins_per_second, :level_id)
        """
    ).params(
        user_id=user.id,
        total_coins=0,
        current_coins=0,
        click_count=0,
        coins_per_second=0,
        level_id=1
    )
    db.session.execute(insert_user_coins_query)

    # Создание записи в таблице с информацией о пользователе
    insert_user_info_query = text(
        """
        INSERT INTO user_info(user_id) VALUES(:user_id)
        """
    ).params(
        user_id=user.id
    )
    db.session.execute(insert_user_info_query)
    db.session.commit()
    return user


def get_user_coins():
    """Получить запись с монетами для текущего пользователя"""
    user_current_coins = db.session.execute(
        text(
            """
            SELECT current_coins FROM user_coins WHERE user_id=:user_id
            """
        ).params(
            user_id = current_user.id
        )
    ).scalar()
    return user_current_coins

def submit_clicks_to_db(data):
    clicks = int(data.get('clicks', 0))
    money = int(data.get('money', 0))
    money_per_click = 1

    #рекорд за секунду 16 кликов, умножаем на 30 секунд
    if clicks > 480:
        return jsonify({'status': 'error', 'message': 'Too many clicks'}), 400 #бан

    user_coins = get_user_coins()
    #проверяем было ли вытащено user_coins
    if user_coins is not None:
        #Проверяем не было ли изменений в local Storage
        if (user_coins == money - clicks * money_per_click ):
            #Обновляем данные в бд
            db.session.execute(
                text(
                    """
                    UPDATE user_coins
                    SET total_coins = total_coins + :totalmoney, current_coins=:money, click_count= click_count + :clicks
                    """
                ).params(
                    totalmoney = clicks * money_per_click,
                    money = money,
                    clicks = clicks
                )
            )
            db.session.commit()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'User менял local Storage'}), 400 #бан
    else:
        print(f"User {current_user.id} not found.")
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

def show_ratings():
    with (db_engine.connect() as conn):
        result_1 = conn.execute(text("SELECT ROW_NUMBER() OVER(ORDER BY user_coins.total_coins DESC), "
                            "CONCAT(users.surname, ' ', users.name, ' ', users.patronymic), user_coins.total_coins "
                            "FROM users JOIN user_coins ON users.id = user_coins.user_id "
                            "ORDER BY user_coins.total_coins DESC LIMIT 100"))

        result_2 = conn.execute(text("SELECT ROW_NUMBER() OVER(ORDER BY user_coins.click_count DESC), "
                                     "CONCAT(users.surname, ' ', users.name, ' ', users.patronymic), user_coins.click_count "
                                     "FROM users JOIN user_coins ON users.id = user_coins.user_id "
                                     "ORDER BY user_coins.click_count DESC LIMIT 100"))

        result_3s = conn.execute(text("SELECT ROW_NUMBER() OVER(ORDER BY SUM(user_coins.total_coins) DESC), "
                                      "clans.clan_name, SUM(user_coins.total_coins) "
                                      "FROM user_coins JOIN users ON user_coins.user_id = users.id "
                                      "JOIN clans ON users.clan_id = clans.id "
                                      "GROUP BY clans.id "
                                      "ORDER BY SUM(user_coins.total_coins) DESC LIMIT 100"))
        result_help = []
        result_3 = []
        for row in result_3s:
            k = row[2]
            k = int(k)
            result_help = list((row[0], row[1], k))
            result_3.append(result_help)
        # for row in result_3:
        # print(row[0], row[1], row[2])

        result_4 = conn.execute(text("SELECT ROW_NUMBER() OVER(ORDER BY SUM(user_coins.click_count) DESC), "
                                     "clans.clan_name, SUM(user_coins.click_count) "
                                     "FROM user_coins JOIN users ON user_coins.user_id = users.id "
                                     "JOIN clans ON users.clan_id = clans.id "
                                     "GROUP BY clans.id "
                                     "ORDER BY SUM(user_coins.click_count) DESC LIMIT 100"))
        return result_1, result_2, result_3, result_4
