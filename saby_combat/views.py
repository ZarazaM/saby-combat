from saby_combat import app, db, db_engine
from flask import render_template, request, redirect, url_for, flash, make_response, session, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Upgrades, UserVerification, Levels, UserCoins, UserInfo, Clans
from .forms import LoginForm, RegisterForm
from .utils import (add_new_user, get_user_by_username, get_user_by_email, is_user_confirmed, confirm_user_email,
                    send_confirmation_email, get_user_coins, submit_clicks_to_db, get_upgrades, delete_upgrades,
                    patch_upgrades, create_upgrades, get_user_upgrades,
                    delete_user_upgrades, patch_user_upgrades, purchase_user_upgrades)
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


@app.route('/api/upgrades', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def manage_upgrades():
    if request.method == 'POST':
        if request.is_json:
            upgrade = request.json
            creation_data = create_upgrades(upgrade)
            return jsonify(creation_data), 201
        return jsonify({'message': 'Incorrect request, request body is not json'}), 400
    elif request.method == 'PATCH':
        if request.is_json:
            upgrade_modification = request.json
            patching_data = patch_upgrades(upgrade_modification)
            return jsonify(patching_data), 200
        return jsonify({'message': 'Incorrect request, request body is not json'}), 400
    elif request.method == 'DELETE':
        if request.args and 'id' in request.args:
            upgrade_ids = request.args.getlist('id')
            deletion_data = delete_upgrades(upgrade_ids)
            return jsonify(deletion_data), 200
        return jsonify({'message': 'You are not specified entries to delete'}), 400
    else:
        if request.args and 'id' in request.args:
            upgrade_ids = request.args.getlist('id')
            specified_upgrades = get_upgrades(upgrade_ids)
            return jsonify(specified_upgrades), 200
        all_upgrades = get_upgrades()
        return jsonify(all_upgrades), 200


@app.route('/api/user_upgrades', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def manage_user_upgrades():
    if request.method == 'POST':
        if request.args and 'user_id' in request.args and 'upgrade_id' in request.args:
            purchase_data = purchase_user_upgrades(user_id=request.args['user_id'], upgrade_id=request.args['upgrade_id'])
            return jsonify(purchase_data), 200
        return {'message': 'You are not specified parameters'}, 400
    elif request.method == 'PATCH':
        if request.is_json:
            modification = request.json
            patching_data = patch_user_upgrades(modification)
            return jsonify(patching_data), 200
        return jsonify({'message': 'Incorrect request, request body is not json'}), 400
    elif request.method == 'DELETE':
        if request.args and 'user_id' in request.args and 'upgrade_id' in request.args:
            deletion_data = delete_user_upgrades(user_id=request.args['user_id'], upgrade_id=request.args['upgrade_id'])
            return jsonify(deletion_data), 200
        return jsonify({'message': 'You are not specified entry to delete'}), 400
    else:
        if request.args and 'user_id' in request.args and 'upgrade_id' in request.args:
            single_entry = get_user_upgrades(user_id=request.args['user_id'], upgrade_id=request.args['upgrade_id'])
            return jsonify(single_entry), 200
        elif request.args and 'user_id' in request.args:
            all_upgrades = get_user_upgrades(user_id=request.args['user_id'])
            return jsonify(all_upgrades), 200
        all_entries = get_user_upgrades()
        return jsonify(all_entries), 200
