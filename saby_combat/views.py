from saby_combat import app, db
from flask import render_template, request, redirect, url_for, flash, make_response, session
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Upgrades, UserVerification, Levels, UserCoins, UserInfo, Clans
from .forms import LoginForm, RegisterForm


@app.route('/')
def click_page():
    return render_template('click_page.html')


@app.route('/rating')
def rating_page():
    return render_template('rating.html')


@app.route('/upgrade')
def upgrade_page():
    return render_template('upgrade.html')


@app.route('/friends')
def friends_page():
    return render_template('friends.html')


@app.route('/admin')
def admin_page():
    return render_template('admin.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login_page():
#     if request.method == 'POST':
#         username = request.form.get('login')
#         password = request.form.get('password')
#         hash_password = hash(password)
#         return f'ure logged as {username} with password {password} hashed as {hash_password}'
#     else:
#         return render_template('login.html')

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



