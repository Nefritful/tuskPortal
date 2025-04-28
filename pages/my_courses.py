from flask import Blueprint, render_template, session, redirect, url_for
from db import connect_db

my_courses_bp = Blueprint('my_courses', __name__, url_prefix='/my_courses')


@my_courses_bp.route('/')
def my_courses():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT courses.* FROM courses
            JOIN user_courses ON courses.id = user_courses.course_id
            WHERE user_courses.user_id = %s
            """
            cursor.execute(sql, (user_id,))
            courses = cursor.fetchall()
    finally:
        connection.close()

    return render_template('my_courses.html', courses=courses)
