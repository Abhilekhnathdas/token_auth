from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
import secrets
import string

app = Flask(__name__)

DATABASE = 'tokens.db'

def create_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def execute_query(query, args=()):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    conn.close()

def fetch_query(query, args=()):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return rows

def init_database():
    with app.app_context():
        conn = create_connection()
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS tokens (
                        id INTEGER PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        token TEXT NOT NULL,
                        status TEXT DEFAULT 'active')''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_token', methods=['GET', 'POST'])
def generate_token():
    if request.method == 'POST':
        email = request.form['email']
        existing_token = fetch_query("SELECT token, status FROM tokens WHERE email = ?", (email,))
        if existing_token:
            token, status = existing_token[0]
            return render_template('show_token.html', token=token, status=status)
        else:
            alphabet = string.ascii_letters + string.digits
            token = ''.join(secrets.choice(alphabet) for _ in range(16))
            execute_query("INSERT INTO tokens (email, token) VALUES (?, ?)", (email, token))
            return redirect(url_for('show_token', email=email))
    return render_template('generate_token.html')

@app.route('/show_token/<email>')
def show_token(email):
    rows = fetch_query("SELECT token FROM tokens WHERE email = ?", (email,))
    if rows:
        token = rows[0][0]
        return render_template('show_token.html', token=token)
    else:
        return 'Token not found for this email'

@app.route('/validate_token', methods=['POST'])
def validate_token():
    token_value = request.json.get('token')
    rows = fetch_query("SELECT * FROM tokens WHERE token = ? AND status = 'active'", (token_value,))
    if rows:
        execute_query("UPDATE tokens SET status = 'inactive' WHERE token = ?", (token_value,))
        return jsonify({'message': 'Token validated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid token'}), 400

@app.route('/reactivate_token_page')
def reactivate_token_page():
    return render_template('reactivate_token.html')

@app.route('/reactivate_token', methods=['POST'])
def reactivate_token():
    email = request.form.get('email')
    existing_token = fetch_query("SELECT token FROM tokens WHERE email = ?", (email,))
    if existing_token:
        token = existing_token[0][0]
        if token:
            execute_query("UPDATE tokens SET status = 'active' WHERE email = ?", (email,))
            return render_template('message.html', message=f'Token reactivated successfully'), 200
        else:
            return render_template('message.html', message='No token found for this email'), 400
    else:
        return render_template('message.html', message='Email not found'), 400


if __name__ == '__main__':
    init_database()
    app.run()
