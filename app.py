from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from encryption import encrypt_password, decrypt_password

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production


def init_db():
    with sqlite3.connect("passwords.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY, site TEXT, username TEXT, password TEXT)")
        # Create default user if needed
        user = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
        if not user:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))


@app.route('/')
def login():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect("passwords.db")
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    conn.close()
    if user:
        session['user'] = username
        return redirect('/dashboard')
    else:
        return "❌ Invalid credentials"


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    conn = sqlite3.connect("passwords.db")
    rows = conn.execute("SELECT * FROM passwords").fetchall()
    conn.close()
    # Decrypt passwords before display
    decrypted = [(id, site, username, decrypt_password(password)) for id, site, username, password in rows]
    return render_template("index.html", passwords=decrypted)


@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect('/')
    site = request.form['site']
    username = request.form['username']
    password = encrypt_password(request.form['password'])  # encrypt here
    with sqlite3.connect("passwords.db") as conn:
        conn.execute("INSERT INTO passwords (site, username, password) VALUES (?, ?, ?)", (site, username, password))
    return redirect('/dashboard')


@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/')
    with sqlite3.connect("passwords.db") as conn:
        conn.execute("DELETE FROM passwords WHERE id=?", (id,))
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
