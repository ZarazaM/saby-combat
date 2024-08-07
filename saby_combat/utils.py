from sqlalchemy import text
import uuid
from flask import jsonify, abort
from flask_login import current_user
from flask_mail import Message
from datetime import datetime
from saby_combat import db, app, mail, db_engine
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from .models import Users, UserCoins
from flask import Request


def get_upgrades(request: Request):
    query_text = 'SELECT * FROM upgrades '
    if request.args and 'id' in request.args:
        upgrade_ids = request.args.getlist('id')
        if all(value.isdigit() for value in upgrade_ids):
            query_text += f'WHERE id IN ({", ".join(upgrade_ids)})'
        else:
            return {'message': 'Incorrect request, ids are not numeric'}, 400
    with db_engine.connect() as connection:
        query = text(query_text)
        result = connection.execute(query)
        return {'data': [row._asdict() for row in result]}, 200


def delete_upgrades(request: Request):
    if request.args and 'id' in request.args:
        upgrade_ids = request.args.getlist('id')
        if all(value.isdigit() for value in upgrade_ids):
            with db_engine.connect() as connection:
                query = text(f'DELETE FROM upgrades WHERE id IN ({", ".join(upgrade_ids)}) RETURNING *')
                result = connection.execute(query)
                connection.commit()
                return {'message': 'deleted successfully', 'data': [row._asdict() for row in result]}, 200
        return {'message': 'Incorrect request, ids are not numeric'}, 400
    return {'message': 'You are not specified entries to delete'}, 400


def patch_upgrades(request: Request):
    if request.is_json:
        upgrade_modification = request.json
        valid_fields = {'id', 'upgrade_name', 'upgrade_image', 'base_cost', 'coins_per_second', 'cost_multiplier'}
        invalid_fields = set(upgrade_modification.keys()) - valid_fields
        sensitive_fields = {'id', 'base_cost', 'coins_per_second', 'cost_multiplier'}
        valid_values = all(upgrade_modification[f'{field}'].isdigit() if field in sensitive_fields else True
                           for field in upgrade_modification.keys())
        if (not invalid_fields and valid_values and
                'id' in upgrade_modification.keys() and len(upgrade_modification) >= 2):
            upgrade_id = upgrade_modification.pop('id')
            updates = ', '.join([f'{key} = :{key}' for key in upgrade_modification.keys()])
            with db_engine.connect() as connection:
                query = text(f'UPDATE upgrades SET {updates} WHERE id = {upgrade_id} RETURNING *')
                result = connection.execute(query, upgrade_modification)
                connection.commit()
                return {'message': 'updated successfully', 'data': [row._asdict() for row in result]}, 200
        return {'message': f'Incorrect request, bad datatypes or invalid parameters: {", ".join(invalid_fields)}'}, 400
    return {'message': 'Incorrect request, request body is not json'}, 400

  
def create_upgrades(request: Request):
    if request.is_json:
        upgrade = request.json
        valid_fields = {'upgrade_name', 'upgrade_image', 'base_cost', 'coins_per_second', 'cost_multiplier'}
        invalid_fields = set(upgrade.keys()) - valid_fields
        filled_fields = valid_fields - set(upgrade.keys()) <= {'upgrade_image'}
        sensitive_fields = {'id', 'base_cost', 'coins_per_second', 'cost_multiplier'}
        valid_values = all(upgrade[f'{field}'].isdigit() for field in sensitive_fields)
        if not invalid_fields and filled_fields and valid_values:
            columns = ', '.join(upgrade.keys())
            placeholders = ', '.join([':' + key for key in upgrade.keys()])
            with db_engine.connect() as connection:
                query = text(f'INSERT INTO upgrades({columns}) '
                         f'VALUES ({placeholders}) RETURNING *')
                result = connection.execute(query, upgrade)
                connection.commit()
                return {'message': 'created successfully', 'data': [row._asdict() for row in result]}, 201
        return {'message': f'Incorrect request, invalid parameters: {", ".join(invalid_fields)}'}, 400
    return {'message': 'Incorrect request, request body is not json'}, 400


def get_user_upgrades(request: Request):
    query_text = (f'''
    SELECT *, CAST(up.base_cost*POWER(CAST(up.cost_multiplier AS FLOAT)/CAST(100 AS FLOAT)+1, 
    user_upgrades.quantity) AS BIGINT) as purchase_cost FROM user_upgrades JOIN (SELECT * FROM upgrades) as up ON 
    (user_upgrades.upgrade_id = up.id) ''')
    if (request.args and 'user_id' in request.args and request.args['user_id'].isdigit() and
            'upgrade_id' in request.args and request.args['upgrade_id'].isdigit()):
        query_text += (f'''WHERE user_upgrades.user_id = {request.args["user_id"]} AND 
                       user_upgrades.upgrade_id = {request.args["upgrade_id"]}''')
    elif request.args and 'user_id' in request.args and request.args['user_id'].isdigit():
        query_text += f'WHERE user_upgrades.user_id = {request.args["user_id"]}'
    with db_engine.connect() as connection:
        query = text(query_text)
        result = connection.execute(query)
        return {'data': [row._asdict() for row in result]}, 200


def patch_user_upgrades(request: Request):
    if request.is_json:
        modification = request.json
        valid_fields = {'user_id', 'upgrade_id', 'quantity'}
        invalid_fields = set(modification) - valid_fields
        valid_values = all(modification[f'{field}'].isdigit() for field in modification)
        if not invalid_fields and (set(modification) & valid_fields) == valid_fields and valid_values:
            with db_engine.connect() as connection:
                query = text(f'''UPDATE user_upgrades SET quantity = {modification["quantity"]} WHERE 
                             user_id = {modification["user_id"]} AND 
                             upgrade_id = {modification["upgrade_id"]} RETURNING *''')
                result = connection.execute(query)
                connection.commit()
                return {'message': 'successfully updated', 'data': [row._asdict() for row in result]}
        return {'message': f'Incorrect request, invalid parameters: {", ".join(invalid_fields)}'}
    return {'message': 'Incorrect request, request body is not json'}, 400


def purchase_user_upgrades(request: Request):
    if (request.args and 'user_id' in request.args and request.args['user_id'].isdigit() and
            'upgrade_id' in request.args and request.args['upgrade_id'].isdigit()):
        with db_engine.connect() as connection:
            select_query = text(
                f'''SELECT user_coins.user_id, user_coins.current_coins, user_coins.coins_per_second as 
                user_coins_per_second, us_up.quantity, up.base_cost, up.cost_multiplier, up.upgrade_name, 
                up.coins_per_second FROM user_coins JOIN(SELECT * FROM user_upgrades WHERE 
                upgrade_id = {request.args["upgrade_id"]}) as us_up ON(user_coins.user_id = us_up.user_id) 
                JOIN(SELECT * FROM upgrades) as up ON(us_up.upgrade_id = up.id) 
                WHERE(user_coins.user_id = {request.args["user_id"]})''')
            result = connection.execute(select_query).first()
            if result.current_coins >= result.base_cost * (result.cost_multiplier / 100 + 1) ** result.quantity:
                update_quantity_query = text(
                    f'''UPDATE user_upgrades SET quantity = {result.quantity + 1} WHERE 
                    (user_id = {request.args["user_id"]} AND upgrade_id = {request.args["upgrade_id"]})''')
                quantity_result = connection.execute(update_quantity_query)
                update_coins_query = text(
                    f'''UPDATE user_coins SET coins_per_second = {result.user_coins_per_second+result.coins_per_second}, 
                    current_coins = {result.current_coins - result.base_cost * (result.cost_multiplier / 100 + 1) ** 
                                     result.quantity} WHERE user_id = {request.args["user_id"]}''')
                coins_result = connection.execute(update_coins_query)
                connection.commit()
                return {'message': f'Upgrade "{result.upgrade_name}" purchased by user with id {result.user_id} for '
                                   f'{result.base_cost * (result.cost_multiplier / 100 + 1) ** result.quantity}'}, 200
            return {'message': 'Недостаточно средств для осуществления покупки'}, 400
    return {'message': 'Incorrect request, you are not specified parameters or ids are not numeric'}, 400


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

      

