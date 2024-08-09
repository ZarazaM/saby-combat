from saby_combat import app, db, db_engine,cache
from flask import render_template, request, redirect, url_for, flash, make_response, session, jsonify
from flask_login import login_required, login_user, current_user, logout_user

from .community import table_friends, is_in_clan, ClanForm, table_clans, clan_invitations_view, is_leader, \
    create_clan, for_name, id_invitations, clan_invitation_from_user, delete_clan, invite_user
from .models import Users, Upgrades, UserVerification, Levels, UserCoins, UserInfo, Clans
from .forms import LoginForm, RegisterForm
from .utils import *
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



@app.route('/submit_clicks', methods=['GET','POST'])
@login_required
def submit_clicks():
    data = request.json
    return submit_clicks_to_db(data)


@app.route('/rating')
@login_required
@cache.cached(timeout=60*10)
def rating_page():
    result_1, result_2, result_3, result_4 = show_ratings()
    return (render_template('rating.html',
             user_all_coins=result_1,
             user_all_clicks=result_2,
             clan_all_coins=result_3,
             clan_all_clicks=result_4))


@app.route('/upgrade')
@login_required
def upgrade_page():
    return render_template('upgrade.html', user_id=current_user.id)


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
