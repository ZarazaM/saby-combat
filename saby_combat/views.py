from saby_combat import app, db
from flask import render_template, request, redirect, url_for, flash, make_response, session, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Upgrades, UserVerification, Levels, UserCoins, UserInfo, Clans
from .forms import LoginForm, RegisterForm
from .utils import add_new_user, get_user_by_username, get_user_by_email, is_user_confirmed, confirm_user_email, send_confirmation_email, get_user_coins, submit_clicks_to_db
from .verification_token import generate_verification_token, confirm_verification_token
from .decorators import logout_required, confirm_your_email, admin_required

@app.route('/', methods=['GET'])
@login_required
@confirm_your_email
def click_page():
    user_current_coins = get_user_coins()
    return render_template('click_page.html', money=user_current_coins)

@app.route('/submit_clicks', methods=['POST'])
@login_required
def submit_clicks():
    data = request.json
    return submit_clicks_to_db(data)

@app.route('/rating')
@login_required
def rating_page():
    return render_template('rating.html')


@app.route('/upgrade')
@login_required
def upgrade_page():
    return render_template('upgrade.html')


@app.route('/friends')
@login_required
def friends_page():
    return render_template('friends.html')


@app.route('/admin')
@login_required
@admin_required
def admin_page():
    return render_template('admin.html')


@app.route("/confirm/<verification_token>")
@login_required
def confirm_email(verification_token):
    try:
        # Аккаунт пользователя уже подтвержден
        if is_user_confirmed(current_user):
            flash("Ваш аккаунт уже подтвержден.")
            return redirect(url_for('click_page'))

        # Аккаунт еще не был подтвержден -> проверка по токену
        email_adress = confirm_verification_token(verification_token)
        user = get_user_by_email(email_adress)
        if user is None:
            raise Exception(f"Пользователь с email = {email_adress} не найден." )
        # Если токен действителен и почта совпала, то аккаунт подтверждается
        if email_adress == user.email:
            confirm_user_email(user)
            flash("Ваш аккаунт успешно подтвержден! Теперь вам доступно больше возможностей.")
        else:
            flash("Ссылка для подтверждения электронной почты устарела или недействительна.")
        return redirect(url_for('click_page'))
    except Exception as ex:
        flash(ex.__str__())
        # Надо добавить html страницу "Пользователь не найден", пока что
        # будет перекидывать на страницу входа
        return redirect(url_for('login_page'))


@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user and user.compare_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('click_page'))
        #return redirect(url_for('login_page'))
    else:
        for error in form.errors.values():
            flash('Неверный логин или пароль, попробуйте еще раз.')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user = add_new_user(form)
        token = generate_verification_token(user.email)
        confirm_url = url_for('confirm_email', verification_token=token, _external=True)
        html_template = render_template('confirm_email.html', confirm_url=confirm_url)
        subject = "Пожалуйста, подтвердите регистрацию аккаунта Saby Combat"
        send_confirmation_email(user.email, subject, html_template)
        return redirect(url_for('login_page'))
    else:
        # Вывод сообщений изменится, когда будет готов html страницы регистрации
        for error in form.errors.values():
            flash(f"Ошибка при регистрации: {error}")
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')



