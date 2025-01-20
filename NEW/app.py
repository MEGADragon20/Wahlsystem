#


from flask import Flask, render_template, request, redirect, current_app, session
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import random as r

def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer('SECRET_KEY')
    return serializer.loads(token, salt='email-verification-salt', max_age=expiration)

def user_data_from_json(username) -> dict:
    try:
        with open(f"data/users.json", 'r') as file:
            data = json.load(file)
        if username in data:
            return data[username]
        raise ValueError('User data not found')
        
    except (FileNotFoundError, json.JSONDecodeError):
        return None

app = Flask(__name__)
app.secret_key = "TheReturnOfTheJedi"


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
            session['username'] = username
            return render_template('/success.html', message="Log-in Successfull (i dont english T-T)")
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
    if username in data:
        return render_template('signup.html', error_message="Username already taken")
    if any(user["email"] == email for user in data.values()):
        return render_template('signup.html', error_message="Email already registered")

    # Create verifcode
    verifcode = ""
    for i in range(6):
        verifcode += str(r.randint(0, 9))

    session['username'] = username
    session['email'] = email
    session['password'] = hashed_password
    session['token'] = generate_password_hash(verifcode)

    # Send verification email
    # TODO
    print(verifcode)

    return render_template('verif_email.html', username= username, email= email, password = hashed_password)

    
        
@app.route('/verificate_signup', methods=['GET', 'POST'])
def verificate_signup():
    if request.method == 'POST':
        username = session.get('username')
        email = session.get('email')
        hashed_password = session.get('password')
        correct_token = session.get('token')
        
        if not (username and email and hashed_password and correct_token):
            return "Session data is missing or invalid."
            
        input_token = request.form.get('input_token')
        if check_password_hash(correct_token, input_token):
            try:
                with open("data/users.json", 'r') as file: 
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}
            
            data[username] = {"email": email, "password": hashed_password}
            os.makedirs("data", exist_ok=True)
            with open("data/users.json", 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            return render_template('success.html', message="Registration successful!")
        else:
            return render_template('verif_email.html', error_message="Incorrect verification code.")
    
    # Redirect for GET requests
    return redirect('/signup')

@app.route('/profile/<path:username>')
def profile(username):
    user_data = user_data_from_json(username)
    if user_data is None:
        return render_template('error.html', err_num = "404", message = "User does not exist")
    user_data
    return render_template('profile.html', user_data=user_data)

@app.route('/chat', defaults= {'username':''})
@app.route('/chat/<path:username>')
def chat(username):
    if username is None:
        return chat_overview() #  TODO
    elif username == 'static/styles/chat.css':
        return app.send_static_file('styles/chat.css')
    # load session user
    self = session['username']
    # err handling
    if self == None:
        return render_template('error.html', err_num = "401", message = "You are not logged in!")
    # load session user data
    user_data = user_data_from_json(self)
    # bit more handling lol
    if user_data is None:
        return render_template('error.html', err_num = "410", message ="You are logged in but your account doesnt exist. We are trying to improve issues like this every day - We are sorry")
    if username in user_data['chat'].keys():
        the_chat = user_data["chat"][username] # chat between user and username
        return render_template('chat.html', msgs=the_chat, recipient=username)
    else:
        return render_template('chat.html', recipient=username)
    

@app.route('/send_msg/<path:recipient>', methods = ['POST'])
def send_msg(recipient):
    msg = request.form.get('msg')
    print("msg", msg)
    self = session.get("username")
    print("rec", recipient)
    if msg[0] == "/":
        # TODO in chat command handling
        pass
    if recipient == self:
        return render_template('error.html', err_num = "403", message = "You cannot send messages to yourself")
    if recipient is None:
        return render_template('error.html', err_num = "400", message = "You are not writing anyone")
    if self == None:
        return render_template('error.html', err_num = "401", message = "You are not logged in!")
    self_data = user_data_from_json(self)
    user_data = user_data_from_json(recipient)
    if user_data is None:
        return render_template('error.html', err_num = "404", message ="We couldn't find the account you were trying to reach")
    if self_data is None:
        return render_template('error.html', err_num = "410", message ="You are logged in but your account doesnt exist. We are trying to improve issues like this every day - We are sorry")
    with open("data/users.json", 'r+') as f:
        data = json.load(f)
        if recipient not in data[self]["chat"].keys():
            data[self]["chat"][recipient] = []
        if self not in data[recipient]["chat"].keys():
            data[recipient]["chat"][self] = []
        
        data[self]["chat"][recipient].append({"sender": "self", "msg": msg})
        data[recipient]["chat"][self].append({"sender": "other", "msg": msg})
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


    return redirect('/chat/'+ recipient)

@app.route('/', defaults= {'subpath':''})
@app.route('/<path:subpath>')
def catch_all(subpath):
    # check for paths
    if subpath == "admin":
        return render_template('error.html', err_num = "401", message = "You are not authorized to access this page!")
    try:
        with open("data/users.json", 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return render_template('error.html', err_num = "404", message = "No useres registred")
    if subpath in data: #check if the users exists
        return render_template('profile.html') #TODO append information
    else:
        return render_template('error.html', err_num = "404", message = "User not found")
    

app.run(host = "0.0.0.0", port = "5050", debug=True) 