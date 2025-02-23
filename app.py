from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_babel import Babel, _  # 确保导入正确，无拼写错误
import os
import json
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key'  # 替换为安全的密钥
app.config['UPLOAD_FOLDER'] = 'cat_data'
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
DATA_FILE = os.path.join(app.config['UPLOAD_FOLDER'], 'cat_records.json')

# 简单用户数据（实际应用应使用数据库）
USERS = {'admin': 'password123'}  # 初始用户
USER_EMAILS = {}  # 存储用户名和邮箱的映射

babel = Babel(app)  # 确保实例化正确

# 获取浏览器语言（使用 localeselector 装饰器）
def get_locale():
    if 'locale' in session:
        return session['locale']
    return request.accept_languages.best_match(['zh', 'en']) or 'zh'

babel.localeselector_func = get_locale  # 使用 localeselector_func 替代 localeselector

# 切换语言
@app.route('/switch-language/<lang>')
def switch_language(lang):
    if lang in ['zh', 'en']:
        session['locale'] = lang
    return redirect(request.referrer or url_for('index'))

# 切换主题（明暗模式）
@app.route('/switch-theme/<theme>')
def switch_theme(theme):
    if theme in ['light', 'dark']:
        session['theme'] = theme
    return redirect(request.referrer or url_for('index'))

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"weight": [], "vaccine": [], "sterilization": [], "treatment": [],
                "insurance": [], "supplements": [], "grooming": [], "cleaning": [],
                "medicine": [], "books": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error=_("用户名或密码错误"))
    return render_template('login.html', error=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if username in USERS:
            return render_template('register.html', error=_("用户名已存在"))
        if email in USER_EMAILS:
            return render_template('register.html', error=_("邮箱已注册"))
        USERS[username] = password
        USER_EMAILS[email] = username
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('register.html', error=None)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', today=str(datetime.date.today()))

@app.route('/api/records', methods=['GET'])
def get_records():
    if 'username' not in session:
        return jsonify({"error": _("未登录")}), 401
    data = load_data()
    return jsonify(data)

@app.route('/api/add_weight', methods=['POST'])
def add_weight():
    if 'username' not in session:
        return jsonify({"error": _("未登录")}), 401
    data = load_data()
    date = request.form.get('date', str(datetime.date.today()))
    weight = request.form.get('weight')
    if not weight or not weight.replace('.', '').isdigit():
        return jsonify({"error": _("体重必须是数字")}), 400
    file = request.files.get('image')
    image_path = None
    if file and file.filename:
        filename = secure_filename(f"weight_{len(data['weight']) + 1}_{file.filename}")
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)
    record = {"date": date, "weight": weight, "image": image_path}
    data["weight"].append(record)
    save_data(data)
    return jsonify({"message": _("体重记录已添加成功"), "record": record})

@app.route('/cat_data/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)