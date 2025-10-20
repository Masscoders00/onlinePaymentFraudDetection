from flask import Flask, render_template, request, redirect, url_for, session
import pickle
from main import predict_transaction
from utils.database import init_db, insert_user, validate_user, insert_report, get_user_reports, save_feedback
from utils.encrypt import encrypt_password
from utils.tips_generator import generate_tips

app = Flask(__name__)
app.secret_key = 'your_secret_key'
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        features = [float(request.form[key]) for key in [
            'step', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
            'oldbalanceDest', 'newbalanceDest', 'type'
        ]]
        result, risk = predict_transaction(features)
        return render_template('result.html', result=result, risk=risk)
    except Exception as e:
        return render_template('result.html', result="Error", risk=str(e))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if insert_user(request.form['username'], request.form['password']):
            return redirect(url_for('login'))
        return render_template('register.html', error="Username exists")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if validate_user(request.form['username'], request.form['password']):
            session['user'] = request.form['username']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    reports = get_user_reports(session['user'])
    return render_template('dashboard.html', user=session['user'], reports=reports)

@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        insert_report(
            session['user'],
            request.form['report_type'],
            request.form['description'],
            request.form['risk_level']
        )
        return render_template('report.html', success="Submitted")
    return render_template('report.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    questions = [
        {
            "q": "Which is common sign of phishing?",
            "opts": ["Generic greetings", "Personal email", "Correct grammar", "Known sender"],
            "ans": 0
        },
        {
            "q": "What to do with suspicious link?",
            "opts": ["Click", "Ignore", "Forward it", "Report it"],
            "ans": 3
        },
        {
            "q": "Safest for payments?",
            "opts": ["Public Wi-Fi", "VPN", "Unsecured site", "Unknown app"],
            "ans": 1
        }
    ]
    if request.method == 'POST':
        score = sum(
            1 for i, q in enumerate(questions) if int(request.form.get(f'q{i}')) == q['ans']
        )
        return render_template('quiz.html', questions=questions, submitted=True, score=score)
    return render_template('quiz.html', questions=questions, submitted=False)

@app.route('/tips')
def tips():
    return render_template('tips.html', tips=generate_tips())

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        save_feedback(session.get('user', 'Anonymous'),
                      int(request.form['rating']),
                      request.form['comment'])
        return render_template('feedback.html', success="Thank you!")
    return render_template('feedback.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
