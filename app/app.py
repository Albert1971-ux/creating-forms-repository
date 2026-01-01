from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ваш-секретный-ключ-тут'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Создаём таблицы при первом запуске
with app.app_context():
    db.create_all()

    # Создаём тестового пользователя если нет
    if not User.query.filter_by(email='test@example.com').first():
        test_user = User(name='Иван', email='test@example.com')
        test_user.set_password('123456')
        db.session.add(test_user)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def edit_profile():
    # Для примера берём первого пользователя
    user = User.query.first()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        # Проверяем пароль если меняем данные
        if not user.check_password(current_password):
            flash('Неверный текущий пароль!', 'danger')
            return redirect(url_for('edit_profile'))

        # Обновляем данные
        user.name = name
        user.email = email

        # Если ввели новый пароль
        if new_password:
            user.set_password(new_password)

        try:
            db.session.commit()
            flash('Профиль успешно обновлён!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')

        return redirect(url_for('edit_profile'))

    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)