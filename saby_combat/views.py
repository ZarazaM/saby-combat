from saby_combat import app, db
from flask import render_template, request, redirect, url_for, flash, make_response, session
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Upgrades, UserVerification, Levels, UserCoins, UserInfo, Clans
from .forms import LoginForm, RegisterForm
from .utils import add_new_user, get_user_by_username


@app.route('/')
@login_required
def click_page():
    return render_template('click_page.html')


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
def admin_page():
    return render_template('admin.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user and user.compare_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('click_page'))
        flash('Неверный логин или пароль, попробуйте еще раз.')
        return redirect(url_for('login_page'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user = add_new_user(form)
        return redirect('/login')
    else:
        for error in form.errors.values():
            flash(f"Ошибка при регистрации: {error}")
    return render_template('register.html', form=form)


@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')



