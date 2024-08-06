from saby_combat import db_engine
from sqlalchemy import text
import uuid
from flask import jsonify
from flask_login import current_user
from flask_mail import Message
from datetime import datetime
from saby_combat import db, app, mail
from werkzeug.security import generate_password_hash
from .models import Users, UserCoins
from . import db


def get_upgrades(upgrade_ids: list[str] = None):

    with db_engine.connect() as connection:
        query_text = 'SELECT * FROM upgrades'
        if upgrade_ids is not None:
            if all(value.isdigit() for value in upgrade_ids):
                query_text += f'WHERE id IN ({", ".join(upgrade_ids)})'
            else:
                return {'message': 'Incorrect request, ids are not numeric'}

        query = text(query_text)
        result = connection.execute(query)
        return {'data': [row._asdict() for row in result]}


def delete_upgrades(upgrade_ids: list[str]):

    if all(value.isdigit() for value in upgrade_ids):
        with db_engine.connect() as connection:
            query = text(f'DELETE FROM upgrades WHERE id IN ({", ".join(upgrade_ids)}) RETURNING *')
            result = connection.execute(query)
            connection.commit()
            return {'message': 'deleted successfully', 'data': [row._asdict() for row in result]}

    return {'message': 'Incorrect request, ids are not numeric'}


def patch_upgrades(upgrade_modification: dict[str, any]):

    valid_fields = {'id', 'upgrade_name', 'upgrade_image', 'base_cost', 'coins_per_second', 'cost_multiplier'}
    invalid_fields = set(upgrade_modification.keys()) - valid_fields
    # TODO проверять значения на подходящесть
    if not invalid_fields:
        with db_engine.connect() as connection:
            upgrade_id = upgrade_modification.pop('id')
            updates = ', '.join([f'{key} = :{key}' for key in upgrade_modification.keys()])
            query = text(f'UPDATE upgrades SET {updates} WHERE id = {upgrade_id} RETURNING *')
            result = connection.execute(query, upgrade_modification)
            connection.commit()
            return {'message': 'updated successfully', 'data': [row._asdict() for row in result]}
    return {'message': f'Incorrect request, invalid parameters: {", ".join(invalid_fields)}'}


def create_upgrades(upgrade: dict[str, any]):

    valid_fields = {'upgrade_name', 'upgrade_image', 'base_cost', 'coins_per_second', 'cost_multiplier'}
    invalid_fields = set(upgrade.keys()) - valid_fields
    # TODO проверять значения на подходящесть
    if not invalid_fields:
        with db_engine.connect() as connection:
            columns = ', '.join(upgrade.keys())
            placeholders = ', '.join([':' + key for key in upgrade.keys()])
            query = text(f'INSERT INTO upgrades({columns}) '
                         f'VALUES ({placeholders}) RETURNING *')
            result = connection.execute(query, upgrade)
            connection.commit()
            return {'message': 'created successfully', 'data': [row._asdict() for row in result]}
    return {'message': f'Incorrect request, invalid parameters: {", ".join(invalid_fields)}'}


def get_user_upgrades(user_id: str = None, upgrade_id: str = None):

    with db_engine.connect() as connection:
        query_text = (f'SELECT *, CAST(up.base_cost*POWER(CAST(up.cost_multiplier AS FLOAT)/CAST(100 AS FLOAT)+1, user_upgrades.quantity) AS BIGINT) as purchase_cost FROM user_upgrades '
                      f'JOIN (SELECT * FROM upgrades) as up ON (user_upgrades.upgrade_id = up.id)')
        if user_id is not None and user_id.isdigit() and upgrade_id is not None and upgrade_id.isdigit():
            query_text += f'WHERE user_upgrades.user_id = {user_id} AND user_upgrades.upgrade_id = {upgrade_id}'
        elif user_id is not None and user_id.isdigit():
            query_text += f'WHERE user_upgrades.user_id = {user_id}'
        query = text(query_text)
        result = connection.execute(query)
        return {'data': [row._asdict() for row in result]}


def delete_user_upgrades(user_id: str = None, upgrade_id: str = None):

    if user_id is not None and user_id.isdigit() and upgrade_id is not None and upgrade_id.isdigit():
        with db_engine.connect() as connection:
            query = text(f'DELETE FROM user_upgrades WHERE user_id = {user_id} AND upgrade_id = {upgrade_id} RETURNING *')
            result = connection.execute(query)
            connection.commit()
            return {'message': 'entry deleted', 'data': [row._asdict() for row in result]}

    return {'message': 'Incorrect request, ids are not numeric'}


def patch_user_upgrades(modification: dict[str, any]):

    valid_fields = {'user_id', 'upgrade_id', 'quantity'}
    invalid_fields = set(modification) - valid_fields
    if not invalid_fields and (set(modification) & valid_fields) == valid_fields:
        with db_engine.connect() as connection:
            query = text(f'UPDATE user_upgrades SET quantity = {modification["quantity"]} WHERE user_id = {modification["user_id"]} AND upgrade_id = {modification["upgrade_id"]} RETURNING *')
            result = connection.execute(query)
            connection.commit()
            return {'message': 'successfully updated', 'data': [row._asdict() for row in result]}
    return {'message': f'Incorrect request, invalid parameters: {", ".join(invalid_fields)}'}


def purchase_user_upgrades(user_id: str = None, upgrade_id: str = None):

    if user_id is not None and user_id.isdigit() and upgrade_id is not None and upgrade_id.isdigit():
        with db_engine.connect() as connection:
            select_query = text(
                f'SELECT user_coins.user_id, user_coins.current_coins, us_up.quantity, up.base_cost, up.cost_multiplier, up.upgrade_name, up.coins_per_second FROM user_coins '
                f'JOIN(SELECT * FROM user_upgrades WHERE upgrade_id = {upgrade_id}) as us_up ON(user_coins.user_id = us_up.user_id) '
                f'JOIN(SELECT * FROM upgrades) as up ON(us_up.upgrade_id = up.id)'
                f'WHERE(user_coins.user_id = {user_id})')
            result = connection.execute(select_query).first()
            if result.current_coins >= result.base_cost * (result.cost_multiplier / 100 + 1) ** result.quantity:
                update_quantity_query = text(
                    f'UPDATE user_upgrades SET quantity = {result.quantity + 1} WHERE (user_id = {user_id} AND upgrade_id = {upgrade_id})')
                quantity_result = connection.execute(update_quantity_query)
                update_coins_query = text(
                    f'UPDATE user_coins SET coins_per_second = {result.coins_per_second}, current_coins = {result.current_coins - result.base_cost * (result.cost_multiplier / 100 + 1) ** result.quantity} WHERE user_id = {user_id}')
                coins_result = connection.execute(update_coins_query)
                connection.commit()
                return {'message': f'Upgrade "{result.upgrade_name}" purchased by user with id {result.user_id} for {result.base_cost * (result.cost_multiplier / 100 + 1) ** result.quantity}'}
            return {'message': 'Недостаточно средств для осуществления покупки'}
    return {'message': 'Incorrect request, ids are not numeric'}


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
