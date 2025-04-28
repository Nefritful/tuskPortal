from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import connect_db

course_bp = Blueprint('course', __name__, url_prefix='/course')


@course_bp.route('/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM courses WHERE id = %s"
            cursor.execute(sql, (course_id,))
            course = cursor.fetchone()
            if not course:
                flash('Курс не найден')
                return redirect(url_for('home.home'))
    finally:
        connection.close()

    return render_template('course.html', course=course)
