from flask import Flask, render_template, request, redirect, current_app
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from app import email
from itsdangerous import URLSafeTimedSerializer

def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer('SECRET_KEY')
    return serializer.loads(token, salt='email-verification-salt', max_age=expiration)



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/submit_login', methods=['POST'])
def submit_login():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        with open("data/users.json", 'r') as file:
            data = json.load(file)
        if username in data and check_password_hash(data[username]["password"], password):
            return redirect('/')
        else:
            return render_template('login.html', error_message="Invalid username or password")
    except (FileNotFoundError, json.JSONDecodeError):
        return "Fatal error"

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_password = generate_password_hash(password)

    # Load existing user data
    try:
        with open("data/users.json", 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Check for existing username or email
    if username in data or any(user["email"] == email for user in data.values()):
        return render_template('signup.html', error_message="Username or email already registered")

    # Add user to data
    data[username] = {"email": email, "password": hashed_password}

    # Create data folder if it doesn't exist
    os.makedirs("data", exist_ok=True)

    with open("data/users.json", 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # Send verification email
    try:
        email.send(
            subject="Verify email",
            receivers=email,
            html_template="emails/verify.html",
            body_params={"Name": username}
        )
    except Exception as e:
        return render_template('signup.html', error_message="Failed to send verification email")

    # Registration successful
    return render_template('success.html', message="Registration successful! Please verify your email.")
        
@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = confirm_verification_token(token)
    except Exception:
        return render_template('error.html', message="Invalid or expired token")

    # Mark the user as verified in your data store
    with open("data/users.json", 'r+') as file:
        data = json.load(file)
        for username, details in data.items():
            if details['email'] == email:
                details['verified'] = True
                break
        file.seek(0)
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.truncate()

    return render_template('success.html', message="Your email has been verified!")



@app.route('/', defaults= {'subpath':''})
@app.route('/<path:subpath>')
def catch_all(subpath):
    return render_template('error.html', err_num = 404, message = "File not found")

app.run(host = "0.0.0.0", port = "5000", debug=True) 