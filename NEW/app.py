from flask import Flask, render_template, request, redirect, current_app, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
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
socketio = SocketIO(app)
@socketio.on('connect')
def on_connect():
    username = session.get('username')  # Get the username from the session
    if username:
        join_room(username)
        print(f'{username} has joined the room {username}')

@socketio.on('disconnect')
def on_disconnect():
    username = session.get('username')
    if username:
        leave_room(username)  # Leave the room when disconnecting
        print(f"{username} has left room {username}")
        
@socketio.on("message")
def handle_message(data):
    self = session.get("username")  # Get sender's username
    recipient = data.get("recipient")  # Get recipient's username
    msg = data.get("msg")  # Get message text

    if not self or not recipient or not msg:
        return  # Ignore invalid messages

    if not msg.startswith("/"):
        with open("data/users.json", "r+") as f:
            users = json.load(f)

            # Ensure the chat structure exists
            users.setdefault(self, {}).setdefault("chat", {}).setdefault(recipient, [])
            users.setdefault(recipient, {}).setdefault("chat", {}).setdefault(self, [])

            # Append message to chat history
            users[self]["chat"][recipient].append({"sender": "self", "msg": msg})
            users[recipient]["chat"][self].append({"sender": "other", "msg": msg})

            # Save back to JSON
            f.seek(0)
            json.dump(users, f, indent=4)
            f.truncate()

        # Emit message in real-time to both sender and recipient
        emit("message", {"sender": "self", "msg": msg}, room=self)
        emit("message", {"sender": "other", "msg": msg}, room=recipient)
        print(socketio.server.manager.rooms)
    else:
        if msg.startswith("/clear"):
            print("Clearing")
            with open("data/users.json", "r+") as f:
                users = json.load(f)
                users[self]["chat"][recipient] = []
                users[recipient]["chat"][self] = []
                f.seek(0)
                json.dump(users, f, indent=4)
                f.truncate()
        elif msg.startswith("/quit"):
            pass



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
            return redirect('/chat')
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

    session['signup_username'] = username
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
        username = session.get('signup_username')
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
            
            data[username] = {"email": email, "password": hashed_password, "chat": {}}
            os.makedirs("data", exist_ok=True)
            with open("data/users.json", 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            session['username'] = username
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
    self = session['username']
    if username == '':
        data = user_data_from_json(self)
        print(data["chat"])
        users = data["chat"].keys()
        print(users)
        return render_template("chat_overview.html", users = users) #  TODO
    elif username == 'static/styles/chat.css':
        return app.send_static_file('styles/chat.css')
    elif username == 'static/scripts/chat.js':
        return app.send_static_file('scripts/chat.js')
    # load session user
    
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
        contacts = user_data["chat"].keys() # list of contacts
        return render_template('chat.html', msgs=the_chat, recipient=username, contacts = contacts)
    else:
        return render_template('chat.html', recipient=username)
    



@app.route('/', defaults= {'subpath':''})
@app.route('/<path:subpath>')
def catch_all(subpath):
    # check for paths
    if subpath == "admin":
        return render_template('error.html', err_num = "401", message = "You are not authorized to access this page!")
    if session.get('username') == None:
        return render_template('login.html')
    print(session.get('username'))
    return render_template('error.html', err_num = "404", message = "User not found")
    

#app.run(host = "0.0.0.0", port = "5050", debug=True) 
socketio.run(app, host = "0.0.0.0", port = "5050", debug=True)