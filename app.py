from flask import Flask, render_template, request, redirect
from collections import defaultdict
import sqlite3

app = Flask(__name__)

# Initialize DB
def init_db():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    amount REAL,
                    category TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses")
    data = cur.fetchall()
    conn.close()
    return render_template('index.html', expenses=data)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']

        conn = sqlite3.connect('expenses.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (title, amount, category) VALUES (?, ?, ?)",
                    (title, amount, category))
        conn.commit()
        conn.close()

        return redirect('/')
    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']

        cur.execute("""
            UPDATE expenses
            SET title=?, amount=?, category=?
            WHERE id=?
        """, (title, amount, category, id))

        conn.commit()
        conn.close()
        return redirect('/')

    # GET request (load existing data)
    cur.execute("SELECT * FROM expenses WHERE id=?", (id,))
    expense = cur.fetchone()
    conn.close()

    return render_template('edit.html', expense=expense)

@app.route('/analytics')
def analytics():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("SELECT category, amount FROM expenses")
    data = cur.fetchall()
    conn.close()

    category_totals = defaultdict(float)
    total = 0

    for category, amount in data:
        category_totals[category] += amount
        total += amount

    return render_template('analytics.html',
                           total=total,
                           categories=list(category_totals.keys()),
                           amounts=list(category_totals.values()))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
