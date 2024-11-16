from flask import Flask
from flask import render_template, request
import random as r
import json

app = Flask(__name__)
def overwrite(data):
    with open("data/verif.json", 'w') as file:
        json.dump(data, file, ensure_ascii= False, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    passportID = request.form.get("passportId")
    verifcode = request.form.get("verifcode")
    vote = request.form.get("vote")
    with open("data/verif.json", 'r') as file:
        data = json.load(file)
    for i in data:
        if i == passportID:
            if verifcode == data[i]["verif-code"]:
                if data[i]["voted"] == False:
                    data[i]["voted"] = True
                    overwrite(data)
                    return render_template('success.html', passportID=passportID, vote=vote)
                else:
                    return render_template('error.html', message="Already voted")
            else:
                return render_template('error.html', message="Invalid verification code")

def generate_verif_code(passport_id = str):
    code = ""
    for i in range(16):
        code += r.choice(["A","B","C","D","E"])
    with open("data/verif.json", 'r') as file:
        data = json.load(file)
    data[passport_id] = {"verif-code": code, "voted": False}
    overwrite(data)

def preset(IDs = list):
    for i in IDs:
        generate_verif_code(i)

generate_verif_code("banna")
app.run(host = "0.0.0.0", port = "5000", debug=True) 