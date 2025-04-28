from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import connect_db

tasks_bp = Blueprint('tasks', __name__, url_prefix='/course')


@tasks_bp.route('/<int:course_id>/tasks')
def tasks(course_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # Проверяем, что курс куплен пользователем
            sql = "SELECT * FROM user_courses WHERE user_id = %s AND course_id = %s"
            cursor.execute(sql, (user_id, course_id))
            purchase = cursor.fetchone()
            if not purchase:
                flash('У вас нет доступа к этому курсу')
                return redirect(url_for('home.home'))

            # Получаем задания курса
            sql_tasks = "SELECT * FROM tasks WHERE course_id = %s"
            cursor.execute(sql_tasks, (course_id,))
            tasks = cursor.fetchall()
    finally:
        connection.close()

    return render_template('tasks.html', tasks=tasks, course_id=course_id)


# Новый маршрут для подробного отображения отдельного задания
@tasks_bp.route('/task/<int:task_id>')
def task_detail(task_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM tasks WHERE id = %s"
            cursor.execute(sql, (task_id,))
            task = cursor.fetchone()
            if not task:
                flash('Задание не найдено.')
                return redirect(url_for('home.home'))
    finally:
        connection.close()

    return render_template('task_detail.html', task=task)
