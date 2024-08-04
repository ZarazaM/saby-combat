import uuid
from flask_mail import Message
from datetime import datetime
from saby_combat import db, app, mail
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from .models import Users


# Отправляет email сообщение со ссылкой для подтверждения аккаунта
# на электронную почту с адресом 'to'
def send_confirmation_email(to, subject, html_template) -> None:
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
def is_user_confirmed(user) -> bool:
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
def confirm_user_email(user) -> None:
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
    

def get_user_by_username(username) -> Users:
    user = db.session.query(Users).from_statement(
        text("SELECT * FROM users where username=:uname").params(uname=username)
    ).first()
    return user


def get_user_by_email(email_adress) -> Users:
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