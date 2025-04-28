from flask import Flask
from pages.auth import auth_bp
from pages.home import home_bp
from pages.my_courses import my_courses_bp
from pages.course import course_bp
from pages.tasks import tasks_bp
from pages.profile import profile_bp
from pages.tests import tests_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на реальное секретное значение!

# Регистрируем блюпринты
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(my_courses_bp)
app.register_blueprint(course_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(tests_bp)
if __name__ == '__main__':
    app.run(debug=True)
