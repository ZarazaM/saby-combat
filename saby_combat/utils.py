#utils.py
from flask import jsonify
from flask_login import current_user
from .models import UserCoins
from sqlalchemy import text
from . import db

def get_user_coins():
    """Получить или создать запись с монетами для текущего пользователя"""
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

    #рекорд за секунду 16 кликов, умножаем на 30 секунд
    if clicks > 480:
        return jsonify({'status': 'error', 'message': 'Too many clicks'}), 400 #бан

    user_coins = get_user_coins()
    #проверяем было ли вытащено user_coins
    if user_coins is not None:
        #Проверяем не было ли изменений в local Storage
        if (user_coins == money - clicks * 1 ):
            #Обновляем данные в бд
            db.session.execute(
                text(
                    """
                    UPDATE user_coins
                    SET total_coins = total_coins + :totalmoney, current_coins=:money, click_count= click_count + :clicks
                    """
                ).params(
                    totalmoney = clicks * 1,
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



