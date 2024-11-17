from flask import Flask
from flask import render_template, request, redirect
import random as r
import json
from datetime import datetime as dt
import requests

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
    faktor = 1000
    with open("data/votes.json", 'r') as f:
        file_content = json.load(f)
        sum = 0
        for i in file_content:
            sum += file_content[i]
        FDP = file_content["FDP"]/sum
        SPD = file_content["SPD"]/sum
        Gruene = file_content["Gruene"]/sum
        AfD = file_content["AfD"]/sum
        Die_Linke = file_content["Die Linke"]/sum
        BSW = file_content["BSW"]/sum
        Union = file_content["Union"]/sum
        return render_template('results.html', fdp=FDP*faktor, spd=SPD*faktor, gruene=Gruene*faktor, afd=AfD*faktor, linke=Die_Linke*faktor, bsw=BSW*faktor, union=Union*faktor)

@app.route('/prelogin')
def send_to_login():
    return redirect('/login?passportID=&verifcode=')

@app.route('/login', methods=['GET'])
def login():
    spID = request.args.get('passportID')
    sverif = request.args.get('verifcode')
    if spID == None:
        spID = ""
    if sverif == None:
        sverif = ""
    if request.remote_addr in forbiddenIps:
        return render_template('error.html', message="IP address is banned")
    return render_template('login2.html', sent_passportId = spID, sent_verifcode = sverif)

@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():#
    if request.remote_addr in forbiddenIps:
        return render_template('error.html', message="IP address is banned")
    passportID = request.form.get("passportId")
    verifcode = request.form.get("verifcode")
    vote = request.form.get("vote")
    print(passportID, verifcode, vote)
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
                    #with open("data/log.txt", 'a') as f:
                    #    f.write(f"{passportID}, {vote}, {dt.now()}, {request.remote_addr}\n")
                    return render_template('success.html', passportID=passportID, vote=vote)
                else:
                    return render_template('error.html', message="Already voted")
            else:
                dubiousIPs.append(request.remote_addr)
                print(count_dubious_IPs(dubiousIPs, request.remote_addr))
                if count_dubious_IPs(dubiousIPs, request.remote_addr) >= 5:
                    forbiddenIps.append(request.remote_addr)
                return render_template('error.html', message="Invalid verification code")
    return render_template("error.html", message="Invalid passport id")

@app.route('/fdp')
def external_redirect():
    return redirect('https://www.fdp.de')

@app.route('/overview')
def overview():
    return render_template('overview.html')
@app.route('/', defaults= {'subpath':''})
@app.route('/<path:subpath>')
def catch_all(subpath):
    return render_template('404.html')

app.run(host = "0.0.0.0", port = "5500", debug=True) 