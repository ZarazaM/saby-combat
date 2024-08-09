from saby_combat import app, db
from flask import render_template, request, redirect, url_for, flash, make_response, session, jsonify
from flask_login import login_required, login_user, current_user, logout_user

from .community import table_friends, is_in_clan, ClanForm, table_clans, clan_invitations_view, is_leader, \
    create_clan, for_name, id_invitations, clan_invitation_from_user, delete_clan, invite_user
from .models import Users, Upgrades, UserVerification, Levels, UserCoins, UserInfo, Clans
from .forms import LoginForm, RegisterForm
from .utils import (add_new_user, get_user_by_username, get_user_by_email, is_user_confirmed, 
                    confirm_user_email, send_confirmation_email, get_user_coins, submit_clicks_to_db, 
                    send_referral_prize, add_friend_by_uuid, is_existing_uuid)
from .verification_token import generate_verification_token, confirm_verification_token
from .decorators import logout_required, confirm_your_email, admin_required


@app.route('/', methods=['GET'])
@login_required
@confirm_your_email
def click_page():
    user_current_coins = get_user_coins()
    return render_template('click_page.html', money=user_current_coins)


@app.route('/submit_clicks', methods=['GET','POST'])
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


@app.route('/community', methods=['GET', 'POST'])
@login_required
def community():
    form = LoginForm()
    user = get_user_by_username(form.username.data)
    # referral_link = user.referral_link
    referral_link = 'de01097f-b090-41d9-9f5d-06f3035440db'
    fr_data = table_friends(referral_link)  # друзья
    clan__id = is_in_clan(referral_link)  # клан пользователя
    clan_info = None
    members = None
    clan_form = ClanForm()
    if clan__id:  # если пользователь находится в клане, то получим информацию о его клане
        clan_info, members = table_clans(referral_link)
    view_invitations = clan_invitations_view(referral_link)  # информация о приглашениях в клан
    if clan__id is None and is_leader(referral_link) is None and clan_form.validate_on_submit():
        action_clan = clan_form.submit.data
        print('Что-то')
        print(f'action_clan = {clan_form.clan_name.data}')
        if clan_form.clan_name.data is not None:
            create_clan(referral_link, clan_form.clan_name.data)
            print(f'clan_info = {clan_info}')
            return redirect(url_for('community'))

    if request.method == 'POST' and is_leader(referral_link) is None:
        action = request.form.get('do_user')  # информация о действии пользователя относительно приглашений в кланы
        clan_name = request.form.get('invitation_id')
        clan_id1 = for_name(clan_name)
        invitation_id = id_invitations(clan_id1, referral_link)
        if action == 'accept':
            clan_invitation_from_user(referral_link, 'accept', invitation_id)
        elif action == 'decline':
            clan_invitation_from_user(referral_link, 'decline', invitation_id)
        return redirect(url_for('community'))

    # управление кланом: есть клан, пользователь -- лидер и это POST запрос.
    if clan__id is not None and is_leader(referral_link) is not None and request.method == 'POST':
        action_leader = request.form.get('management')
        if action_leader == 'delete_clan':
            delete_clan(clan__id)
            return redirect(url_for('community'))
        elif action_leader == 'add_user':
            invite_user(referral_link, clan__id)
            return redirect(url_for('community'))
    if clan__id:
        leader_id = is_leader(referral_link)
        if leader_id:
            return render_template('friends.html',
                                   friends=fr_data, referral_link=referral_link, clan_id=clan__id, clan_info=clan_info,
                                   members=members, invitations=view_invitations, is__leader=True, form=clan_form)
        else:
            return render_template('friends.html',
                                   friends=fr_data, referral_link=referral_link, clan_id=clan__id, clan_info=clan_info,
                                   members=members, invitations=view_invitations, is__leader=False, form=clan_form)
    else:
        return render_template('friends.html',
                               friends=fr_data, referral_link=referral_link, clan_id=clan__id, clan_info=clan_info,
                               members=members, invitations=view_invitations, form=clan_form)


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



