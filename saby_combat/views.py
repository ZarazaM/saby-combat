from saby_combat import app, db, db_engine
from flask import render_template, request, redirect, url_for, flash, make_response, session, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Upgrades, UserVerification, Levels, UserCoins, UserInfo, Clans
from .forms import LoginForm
from sqlalchemy import text
from .utils import (get_upgrades, delete_upgrades, patch_upgrades, create_upgrades, get_user_upgrades,
                    delete_user_upgrades, patch_user_upgrades, purchase_user_upgrades)


@app.route('/')
def click_page():
    return render_template('click_page.html')


@app.route('/rating')
def rating_page():
    return render_template('rating.html')


@app.route('/upgrade')
@login_required
def upgrade_page():
    return render_template('upgrade.html', user_id=current_user.id)


@app.route('/friends')
def friends_page():
    return render_template('friends.html')


@app.route('/admin')
def admin_page():
    return render_template('admin.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('admin_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter(Users.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('admin_page'))
        flash('invalid username/password', 'error')
        return redirect(url_for('login_page'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        # логика регистрации пользователя
        email = request.form.get('email')
        username = request.form.get('login')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        return f'created account {username} with email {email} and password {password}, confirm password {password == confirm_password}'
    else:
        return render_template('register.html')


@app.route('/profile')
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
