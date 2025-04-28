from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from db import connect_db

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, username, email FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
    finally:
        connection.close()

    return render_template('profile.html', user=user)


@profile_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    connection = connect_db()

    if request.method == 'POST':
        # Получаем новые данные из формы
        username = request.form.get('username')
        email = request.form.get('email')

        try:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET username = %s, email = %s WHERE id = %s"
                cursor.execute(sql, (username, email, user_id))
                connection.commit()
                flash('Настройки успешно обновлены')
        except Exception as e:
            flash('Ошибка при обновлении настроек')
        finally:
            connection.close()

        return redirect(url_for('profile.settings'))

    else:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id, username, email FROM users WHERE id = %s"
                cursor.execute(sql, (user_id,))
                user = cursor.fetchone()
        finally:
            connection.close()

    return render_template('settings.html', user=user)
