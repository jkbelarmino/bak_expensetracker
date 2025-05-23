from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import bcrypt  # Import bcrypt for password hashing

app = Flask(__name__)
app.secret_key = "your_secret_key"

DATABASE = 'expense_tracker.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        g._database = db
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user'] = user['username']
            return redirect(url_for('tracker'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user'] = user['username']
            return redirect(url_for('tracker'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")

        db = get_db()
        # Check if username already exists
        if db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone():
            return render_template('register.html', error="Username already exists")

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user into the database
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        db.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    expenses = db.execute('SELECT * FROM expenses WHERE username = ?', (session['user'],)).fetchall()
    total = sum(expense['amount'] for expense in expenses)
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        db.execute('INSERT INTO expenses (username, description, amount) VALUES (?, ?, ?)',
                   (session['user'], description, amount))
        db.commit()
        return redirect(url_for('tracker'))
    return render_template('tracker.html', username=session['user'], expenses=expenses, total=total)


@app.route('/edit_expense', methods=['POST'])
def edit_expense():
    if 'user' not in session:
        return redirect(url_for('login'))

    expense_id = request.form['expense_id']
    new_description = request.form['new_description']
    new_amount = float(request.form['new_amount'])

    db = get_db()
    db.execute('UPDATE expenses SET description = ?, amount = ? WHERE id = ?',
               (new_description, new_amount, expense_id))
    db.commit()

    return redirect(url_for('tracker'))



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()  # Explicitly initialize the database
    app.run(debug=True)
