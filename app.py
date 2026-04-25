from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
# База данных создастся автоматически в папке проекта
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Таблица для хранения трат
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), default="📦 Другое")
    date = db.Column(db.DateTime, default=datetime.utcnow)


# Инициализация базы данных
with app.app_context():
    db.create_all()


@app.route('/', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']
        try:
            new_expense = Expense(title=title, amount=float(amount), category=category)
            db.session.add(new_expense)
            db.session.commit()
        except:
            pass
        return redirect('/')

    expenses = Expense.query.order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)

    # Данные для графика (группировка по категориям)
    cat_data = db.session.query(Expense.category, func.sum(Expense.amount)).group_by(Expense.category).all()
    labels = [row[0] for row in cat_data]
    values = [row[1] for row in cat_data]

    max_exp = db.session.query(func.max(Expense.amount)).scalar() or 0
    avg_bill = round(total / len(expenses), 2) if expenses else 0

    return render_template('index.html', expenses=expenses, total=total,
                           max_exp=max_exp, avg=avg_bill,
                           labels=labels, values=values)


@app.route('/delete/<int:id>')
def delete(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect('/')


# ТОТ САМЫЙ КУСОК ДЛЯ ЗАПУСКА - БЕЗ НЕГО ССЫЛКИ НЕ БУДЕТ
if __name__ == "__main__":
    app.run(debug=True)