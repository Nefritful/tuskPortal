from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from db import connect_db

tests_bp = Blueprint('tests', __name__, url_prefix='/tests')

def get_user_courses(user_id):
    """Получаем список курсов, купленных пользователем, для тестирования."""
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT courses.id, courses.title, courses.logo 
            FROM courses 
            JOIN user_courses ON courses.id = user_courses.course_id 
            WHERE user_courses.user_id = %s
            """
            cursor.execute(sql, (user_id,))
            courses = cursor.fetchall()
    finally:
        connection.close()
    return courses

def get_course_tests(course_id):
    """Получаем список тестов для указанного курса (отсортированных по id)."""
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM tests WHERE course_id = %s ORDER BY id"
            cursor.execute(sql, (course_id,))
            tests = cursor.fetchall()
    finally:
        connection.close()
    return tests

@tests_bp.route('/')
def select_course():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    courses = get_user_courses(user_id)
    return render_template('tests_courses.html', courses=courses)

@tests_bp.route('/<int:course_id>/start')
def start_tests(course_id):
    """Инициализируем тестирование для курса: устанавливаем course_id и обнуляем счетчик правильных ответов."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    tests = get_course_tests(course_id)
    if not tests:
        flash("Для данного курса тесты отсутствуют.")
        return redirect(url_for('tests.select_course'))
    # Обнуляем счетчик
    session['correct_count'] = 0
    # Сохраняем текущий курс в сессии
    session['course_id'] = course_id
    return redirect(url_for('tests.test_question', course_id=course_id, index=0))

@tests_bp.route('/<int:course_id>/question/<int:index>', methods=['GET', 'POST'])
def test_question(course_id, index):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # Загружаем тесты из базы для заданного курса
    tests = get_course_tests(course_id)
    if not tests:
        flash("Для данного курса тесты отсутствуют.")
        return redirect(url_for('tests.select_course'))
    # Проверяем, что сохраненный course_id совпадает с переданным
    if int(course_id) != session.get('course_id'):
        flash("Ошибка инициализации тестирования: выбран неверный курс.")
        return redirect(url_for('tests.select_course'))

    # Если индекс превышает количество тестов – тестирование закончено
    if index >= len(tests):
        total = len(tests)
        correct = session.get('correct_count', 0)
        # Очищаем сессионные данные по тестированию
        session.pop('course_id', None)
        session.pop('correct_count', None)
        return render_template('test_finished.html', total=total, correct=correct)

    current_test = tests[index]

    if request.method == 'POST':
        user_answer = request.form.get('user_answer', '').strip()
        correct_answer = current_test.get('correct_answer')
        is_correct = (user_answer.lower() == correct_answer.lower())
        # Сохраняем результат в БД
        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO test_result (user_id, test_id, course_id, user_answer, is_correct)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (session['user_id'], current_test.get('id'),
                                       course_id, user_answer, is_correct))
                connection.commit()
        finally:
            connection.close()
        if is_correct:
            session['correct_count'] = session.get('correct_count', 0) + 1
        # Переходим к следующему вопросу
        next_index = index + 1
        return redirect(url_for('tests.test_question', course_id=course_id, index=next_index))

    return render_template('test_question.html', test=current_test, index=index, total=len(tests))

@tests_bp.route('/<int:course_id>/question/<int:index>/navigate', methods=['POST'])
def navigate_question(course_id, index):
    """Обработка навигации по тесту: кнопки Назад, Дальше."""
    btn = request.form.get('btn')
    new_index = index
    if btn == "back":
        new_index = max(0, index - 1)
    elif btn == "next":
        new_index = index + 1
    return redirect(url_for('tests.test_question', course_id=course_id, index=new_index))
