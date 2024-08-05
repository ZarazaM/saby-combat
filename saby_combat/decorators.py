from functools import wraps

from flask import redirect, url_for, flash
from flask_login import current_user

from .utils import is_user_confirmed


def logout_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('click_page'))
        return func(*args, **kwargs)
    
    return decorated_function


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.role:
            flash("Добрый день, Администратор!")
        else:
            flash("Вы не являетесь администратором Saby Combat.")
            # Тоже надо подумать, может Тане, куда перенаправлять
            return redirect(url_for('click_page'))
        return func(*args, **kwargs)
    
    return decorated_function


# Будет использоваться для вывода сообщения с просьбой подтвердить аккаунт
def confirm_your_email(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            if not is_user_confirmed(current_user):
                flash("Пожалуйста, подтвердите ваш аккаунт! \
                      Вам на почту было отправлено письмо со ссылкой для подтверждения.")
        except Exception as ex:
            flash(ex.__str__())
            # Или на страницу "Пользователь не найден"
            return redirect(url_for('login_page'))
        return func(*args, **kwargs)

    return decorated_function