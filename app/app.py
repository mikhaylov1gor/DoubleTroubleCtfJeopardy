from flask import Flask, request, session, render_template_string, redirect
import mysql.connector
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_CONFIG = {
    'user': 'root',
    'password': 'secret',
    'host': 'db',
    'database': 'ctf_db'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>HITSecure v2.0</title>
    <style>
        .security-banner {
            background: #1a237e;
            color: white;
            padding: 10px;
            text-align: center;
            font-family: Arial, sans-serif;
        }
        /* SECURITY NOTE: Все запросы фильтруются через AI-модуль (код 0x7E3FA1) */
    </style>
</head>
<body>
    <div class="security-banner">
        🔒 Protected by CyberShield 9000 (v2.3.1)
    </div>
    <h1>Corporate Login</h1>
    <!-- DEBUG: Login handler @ /login (POST) -->
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>
    <!-- [DEV MEMO] SQL запросы используют legacy auth system -->
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        .security-watermark {
            position: fixed;
            opacity: 0.1;
            bottom: 10px;
            right: 10px;
            font-size: 24px;
        }
    </style>
</head>
<body>
    <div class="security-banner">
        🛡️ Active Threat Protection: Blocked 127 intrusion attempts today
    </div>
    <h1>Welcome, {{ user }}!</h1>

    <!-- DEBUG: Content loader ver 0.4.2 -->
    <nav>
        <a href="?page=profile">Profile</a>
        <a href="?page=stats">Statistics</a>
        <!-- [SYSTEM] Все файлы проверяются через sandbox -->
    </nav>

    <div class="content">
        {{ content|safe }}
    </div>

    <div class="security-watermark">
        HITSECURE-PROTECTED
    </div>
</body>
</html>
'''


@app.route('/', methods=['GET'])
def index():
    if 'user' in session:
        return redirect('/dashboard')
    return render_template_string(LOGIN_TEMPLATE)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        if cursor.fetchone():
            session['user'] = username
            return redirect('/dashboard')
    except Exception as e:
        pass
    return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials!")


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    page = request.args.get('page', 'profile')
    allowed_pages = ['profile', 'stats']

    try:
        if not any(page.startswith(allowed) for allowed in allowed_pages):
            raise ValueError("Blocked by CyberShield: this page is not allowed")

        try:
            with open(os.path.join('/app/pages', f'{page}.txt'), 'r') as f:
                content = f.read()
        except FileNotFoundError:
            normalized_path = os.path.normpath(os.path.join('/app', f'{page}.txt'))
            with open(normalized_path, 'r') as f:
                content = f.read()

    except Exception as e:
        content = f"Error: {str(e)}"

    return render_template_string(DASHBOARD_TEMPLATE,
                                  user=session['user'],
                                  content=content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)