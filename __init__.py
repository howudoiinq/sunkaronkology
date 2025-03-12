from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'
    
    db.init_app(app)

    with app.app_context():
        from . import routes, models  # Импортируем маршруты и модели
        db.create_all()  # Создаем таблицы в БД

    return app
