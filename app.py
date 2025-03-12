from flask import Flask, render_template, url_for, request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):

        return f'<Article {self.title}>'



@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)


@app.route('/posts/<int:id>')
def posts_detail(id):
    article = Article.query.get_or_404(id)
    return render_template("post_detail.html", article=article)


@app.route('/delete_article/<int:id>')
def delete_article(id):
    article = Article.query.get_or_404(id)  # Получаем статью по ID или выдаем ошибку 404

    try:
        db.session.delete(article)  # Удаляем статью
        db.session.commit()  # Сохраняем изменения в БД
        return redirect('/posts')  # После удаления возвращаемся на страницу "Статьи"
    except:
        return "Ошибка при удалении статьи"



@app.route('/uslugi')
def uslugi():
    return render_template("uslugi.html")

@app.route('/contacts')
def contacts():
    return render_template("contacts.html")

@app.route('/submit', methods=['POST'])
def submit():
    # Получаем данные из формы (если нужно)
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    
    # Здесь можно сохранить данные в БД или обработать их

    # Перенаправляем на страницу tickets
    return redirect(url_for('tickets'))

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

    else:
        return render_template('create_article.html')


@app.route('/patient')
def patient_dashboard():
    if session.get('role') == 'patient':
        return render_template('patient_dashboard.html')
    return redirect(url_for('index'))


@app.route('/doctor')
def doctor_dashboard():
    if session.get('role') == 'doctor':
        return render_template('doctor_dashboard.html')
    return redirect(url_for('index'))


@app.route('/admin')
def admin_dashboard():
    if session.get('role') == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(debug=True)
