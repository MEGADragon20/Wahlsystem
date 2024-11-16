from flask import Flask
from flask import render_template, request
import random as r
import json
from datetime import datetime as dt


dubiousIPs = []   
forbiddenIps = []


app = Flask(__name__)
def overwrite(data):
    with open("data/verif.json", 'w') as file:
        json.dump(data, file, ensure_ascii= False, indent=4)

def count_dubious_IPs(liste, tester):
    count = 0
    for i in liste:
        if i == tester:
            count += 1
    return count
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/leaderboard')
def leaderboard():
    with open("data/votes.json", 'r') as f:
        file_content = json.load(f)
        FDP = file_content["FDP"]
        SPD = file_content["SPD"]
        Grüne = file_content["Grüne"]
        AfD = file_content["AfD"]
        Die_Linke = file_content["Die Linke"]
        BSW = file_content["BSW"]
        Union = file_content["Union"]
        return render_template('leaderboard.html', FDP = FDP, Union = Union, SPD = SPD, Grüne = Grüne, AfD = AfD, Die_Linke = Die_Linke, BSW = BSW)
 

@app.route('/login')
def login():
    if request.remote_addr in forbiddenIps:
        return render_template('error.html', message="IP address is banned")
    return render_template('login.html')

@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():#
    if request.remote_addr in forbiddenIps:
        return render_template('error.html', message="IP address is banned")
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
                    with open("data/votes.json", 'r') as f:
                        vote_data = json.load(f)
                    vote_data[vote] += 1
                    with open("data/votes.json", 'w') as f:
                        json.dump(vote_data, f, ensure_ascii= False, indent=4)
                    with open("data/log.txt", 'a') as f:
                        f.write(f"{passportID}, {vote}, {dt.now()}, {request.remote_addr}\n")
                    return render_template('success.html', passportID=passportID, vote=vote)
                else:
                    return render_template('error.html', message="Already voted")
            else:
                dubiousIPs.append(request.remote_addr)
                print(count_dubious_IPs(dubiousIPs, request.remote_addr))
                if count_dubious_IPs(dubiousIPs, request.remote_addr) >= 5:
                    forbiddenIps.append(request.remote_addr)
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
preset(["g", "a", "f", "t"])

app.run(host = "0.0.0.0", port = "5500", debug=True) 