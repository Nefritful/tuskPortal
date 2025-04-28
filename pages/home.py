from flask import Blueprint, render_template, session, redirect, url_for
from db import connect_db

home_bp = Blueprint('home', __name__, url_prefix='/home')


@home_bp.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM courses"
            cursor.execute(sql)
            courses = cursor.fetchall()
    finally:
        connection.close()

    return render_template('home.html', courses=courses)
