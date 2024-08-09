from saby_combat import app, db, db_engine
from flask import render_template, request, redirect, url_for, flash, make_response, session, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Upgrades, UserVerification, Levels, UserCoins, UserInfo, Clans
from .forms import LoginForm, RegisterForm
from .utils import (get_all_levels, add_new_user, get_user_by_username, get_user_by_email, is_user_confirmed,
                    confirm_user_email, send_confirmation_email, get_data_for_main_page, submit_clicks_to_db, 
                    send_referral_prize, add_friend_by_uuid, is_existing_uuid, get_upgrades, delete_upgrades,
                    patch_upgrades, create_upgrades, get_user_upgrades, patch_user_upgrades, purchase_user_upgrades)
from .verification_token import generate_verification_token, confirm_verification_token
from .decorators import logout_required, confirm_your_email, admin_required


@app.route('/', methods=['GET'])
@login_required
# @confirm_your_email
def click_page():
    user_data = get_data_for_main_page()
    levels = get_all_levels()

    # Проверка, если goal_level равен 0, подставляем знак бесконечности (0 - цель у максимального уровня)
    if user_data['goal_level'] == 0:
        goal_level = '∞'
    else:
        goal_level = user_data['goal_level']
    levels[-1] = (*levels[-1][:2], '∞', *levels[-1][3:])
    return render_template(
        'click_page.html',
        money=user_data['current_coins'],
        coins_per_click=user_data['coins_per_click'],
        coins_per_second=user_data['coins_per_second'],
        goal_level=goal_level,
        name_current_level=user_data['name_current_level'],
        current_level=user_data['current_level'],
        max_level=user_data['max_level'],
        levels=levels
    )


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
    return render_template('upgrade.html', user_id=current_user.id)


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
            flash('Неверный логин или пароль, попробуйте еще раз.', category="login-fail")
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register_page():
    form = RegisterForm()
    referrer_uuid = request.args.get("ref")
    if form.validate_on_submit():
        if referrer_uuid and is_existing_uuid(referrer_uuid):
            user = add_new_user(form)
            send_referral_prize(referrer_uuid=referrer_uuid)
            add_friend_by_uuid(user, referrer_uuid)
        else:
            user = add_new_user(form)
        # Оптравка сообщения с подтверждением на почту
        token = generate_verification_token(user.email)
        confirm_url = url_for('confirm_email', verification_token=token, _external=True)
        html_template = render_template('confirm_email.html', confirm_url=confirm_url)
        subject = "Пожалуйста, подтвердите регистрацию аккаунта Saby Combat"
        # Закомментил, чтобы останых не смущала ошибка почты
        #send_confirmation_email(user.email, subject, html_template)
        return redirect(url_for('login_page'))
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


@app.route('/api/upgrades', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def manage_upgrades():
    if request.method == 'POST':
        response, status_code = create_upgrades(request)
        return jsonify(response), status_code
    elif request.method == 'PATCH':
        response, status_code = patch_upgrades(request)
        return jsonify(response), status_code
    elif request.method == 'DELETE':
        response, status_code = delete_upgrades(request)
        return jsonify(response), status_code
    else:
        response, status_code = get_upgrades(request)
        return jsonify(response), status_code


@app.route('/api/user_upgrades', methods=['GET', 'POST', 'PATCH'])
def manage_user_upgrades():
    if request.method == 'POST':
        response, status_code = purchase_user_upgrades(request)
        return jsonify(response), status_code
    elif request.method == 'PATCH':
        response, status_code = patch_user_upgrades(request)
        return jsonify(response), status_code
    else:
        response, status_code = get_user_upgrades(request)
        return jsonify(response), status_code
