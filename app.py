from flask import Flask
from flask import render_template, request, redirect, jsonify
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
        return f"""
        <svg class="chart" width="450" height="350" aria-labelledby="chartinfo" viewBox="0 0 450 350">

	        <g class="bar_purple">
		        <rect fill="purple" width="{BSW*faktor}" height="45" y="0"/>
	        </g>
	        <g class="bar_pink">
		        <rect fill="crimson" width="{Die_Linke*faktor}" height="45" y="50"/>
	        </g>
	        <g class="bar_green">
		        <rect fill="green" width="{Gruene*faktor}" height="45" y="100"/>
	        </g>
	        <g class="bar_red">
		        <rect fill="red" width="{SPD*faktor}" height="45" y="150" />
	        </g>
	        <g class="bar_yellow">
		        <rect fill="yellow" width="{FDP*faktor}" height="45" y="200" />
	        </g>
            <g class="bar_black">
		        <rect fill="black" width="{Union*faktor}" height="45" y="250"/>
	        </g>
            <g class="bar_blue">
		        <rect fill="blue" width="{AfD*faktor}" height="45" y="300"/>
	        </g>
</svg>
"""
 

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
                    pidgeon_message = {
                        "passportId": passportID,
                        "vote": vote
                    }
                    response = requests.post('http://10.15.188.93:5000/x', json = pidgeon_message)
                    if response.status_code != 200:
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

@app.route('/fdp')
def external_redirect():
    return redirect('https://www.fdp.de')


@app.route('/', defaults= {'subpath':''})
@app.route('/<path:subpath>')
def catch_all(subpath):
    return render_template('404.html')

app.run(host = "0.0.0.0", port = "5500", debug=True) 