from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import connect_db
import pymysql

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверка пользователя в БД
        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username=%s AND password=%s"
                cursor.execute(sql, (username, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return redirect(url_for('home.home'))
                else:
                    flash('Неверное имя пользователя или пароль')
        finally:
            connection.close()
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # Вставка нового пользователя в БД
        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, email, password))
                connection.commit()
                flash('Регистрация успешна, теперь можно войти!')
                return redirect(url_for('auth.login'))
        except pymysql.MySQLError:
            flash('Ошибка при регистрации')
        finally:
            connection.close()
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
