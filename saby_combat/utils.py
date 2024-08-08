import uuid
from flask import jsonify
from flask_login import current_user
from flask_mail import Message
from datetime import datetime
from saby_combat import db, app, mail
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

def get_all_levels():
    """Получить все уровни из таблицы levels"""
    result = db.session.execute(text("SELECT id, level_name, coins_required, coins_per_click FROM levels ORDER BY id")).fetchall()
    return result

def get_data_for_main_page():
    """Получить все нужные данные для главной страницы"""
    result = db.session.execute(
        text(
            """
            SELECT 
                uc.current_coins, 
                uc.coins_per_second, 
                l.coins_per_click, 
                l.level_name, 
                l.coins_required, 
                l.id,
                (SELECT MAX(id) FROM levels) AS max_level
            FROM user_coins uc
            JOIN levels l ON uc.level_id = l.id
            WHERE uc.user_id = :user_id
            """
        ).params(
            user_id=current_user.id
        )
    ).fetchone()

    if result:
        return {
             'current_coins': result[0],
             'coins_per_second': result[1],
             'coins_per_click': result[2],
             'name_current_level': result[3],
             'goal_level': result[4],
             'current_level': result[5],
             'max_level': result[6]
        }
    else:
        return {
            'current_coins': 0,
            'coins_per_second': 0,
            'coins_per_click': 0,
            'name_current_level': 'Дрон',
            'goal_level': 0,
            'current_level': 1,
            'max_level': 1
        }


def submit_clicks_to_db(data):
    clicks = int(data.get('clicks', 0))
    money = float(data.get('money', 0))
    coinsPerSecondAccumulated = float(data.get('coinsPerSecondAccumulated', 0))

    # рекорд за секунду 16 кликов, умножаем на 30 секунд
    if clicks > 480:
        return jsonify({'status': 'error', 'message': 'Too many clicks'}), 400  # бан

    user_coins = get_data_for_main_page()
    # проверяем было ли вытащено user_coins
    if user_coins is not None:
        # Проверяем не было ли изменений в local Storage
        # Клики считаются проверенными, главное чтобы были в пределе нормы; Проверяем чтобы доход пассивный был меньше равен доходу за секунду из бд * 30 (меньше равно, так как за 30 секунд пассивный доход мог измениться)
        # Также проверяем чтобы количество монет старое из бд + доход * 30 + клики умноженное на вес были больше равно кличеству монет из local storage (Больше равно, так как за 30 секунд и вес клика и доход могли увеличиться)
        if (coinsPerSecondAccumulated <= 30*user_coins['coins_per_second'] and user_coins['current_coins'] + user_coins['coins_per_second'] * 30 + clicks * user_coins['coins_per_click']  >= money):
            # Обновляем данные в бд
            db.session.execute(
                text(
                    """
                    UPDATE user_coins
                    SET total_coins = total_coins + :totalmoney, current_coins=:money, click_count= click_count + :clicks
                    WHERE user_id = :user_id
                    """
                ).params(
                    totalmoney=coinsPerSecondAccumulated + clicks*user_coins['coins_per_click'],
                    money=money,
                    clicks=clicks,
                    user_id=current_user.id
                )
            )
            db.session.commit()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'User менял local Storage'}), 400  # бан
    else:
        print(f"User {current_user.id} not found.")
        return jsonify({'status': 'error', 'message': 'User not found'}), 404