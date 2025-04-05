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

if __name__ == "__main__":
    init_db()  # Explicitly initialize the database
    app.run(debug=True)
