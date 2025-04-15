import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///absolute/path/to/blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Ensure you set a secret key for sessions
db = SQLAlchemy(app)

# Создание модели Article для SQLAlchemy
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Article {self.title}>'

# Функция для получения роли пользователя из базы данных
def get_user_role(username, password):
    with sqlite3.connect('db/blog.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT id, role, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and check_password_hash(result[2], password):  # Проверка пароля
            return result[0], result[1]  # Возвращаем user_id и role
    return None, None

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/uslugi')
def uslugi():
    return render_template("uslugi.html")

@app.route('/contacts')
def contacts():
    return render_template("contacts.html")

# Обработчик для страницы логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_id, role = get_user_role(username, password)
        
        if user_id:
            session['username'] = username
            session['role'] = role
            session['user_id'] = user_id  # Сохраняем user_id в сессии
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif role == 'patient':
                return redirect(url_for('patient_dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template("login.html")  # Отображаем форму логина при GET запросе

# Панели для разных ролей
@app.route('/admin')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')

@app.route('/doctor')
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('home'))
    return render_template('doctor_dashboard.html')

@app.route('/patient')
def patient_dashboard():
    if 'role' not in session or session['role'] != 'patient':
        return redirect(url_for('home'))
    return render_template('patient_dashboard.html')

@app.route('/tickets')
def tickets():
    return render_template('ticket.html')

@app.route('/create_article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "error"
    return render_template('create_article.html')

# Бронирование записи
@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    service_id = request.form['service_id']
    user_id = session['user_id']  # Получаем user_id из сессии

    # Добавляем пациента в очередь
    with sqlite3.connect('db/blog.db') as con:
        cursor = con.cursor()
        cursor.execute("INSERT INTO queue (user_id, service_id) VALUES (?, ?)", (user_id, service_id))
        con.commit()

    return redirect(url_for('patient_dashboard'))

# Уведомление пациента, что его очередь подошла
@app.route('/notify_patient/<int:queue_id>', methods=['POST'])
def notify_patient(queue_id):
    with sqlite3.connect('db/blog.db') as con:
        cursor = con.cursor()
        cursor.execute("UPDATE queue SET status = 'served' WHERE id = ?", (queue_id,))
        con.commit()

    # Здесь можно добавить уведомление пациенту, например, через email или пуш-уведомления
    return redirect(url_for('doctor_dashboard'))
def book_appointment():
    service_id = request.form['service_id']
    user_id = session['user_id']
    
    # Создаем запись в очереди
    new_appointment = Queue(user_id=user_id, service_id=service_id)

    try:
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('patient_dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error occurred: {e}"

@app.route('/notify_patient_doctor/<int:queue_id>', methods=['POST'])
def notify_patient_doctor(queue_id):
    # Логика уведомления для врача
    pass

@app.route('/notify_patient_patient/<int:queue_id>', methods=['POST'])
def notify_patient_patient(queue_id):
    # Логика уведомления для пациента
    pass

if __name__ == '__main__':
    app.run(debug=True)
