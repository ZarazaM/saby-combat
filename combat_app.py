from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__.split('.')[0])


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


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')
        hash_password = hash(password)
        return f'ure logged as {username} with password {password} hashed as {hash_password}'
    else:
        return render_template('login.html')


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


if __name__ == '__main__':
    app.run(debug=True)
