from flask import Flask, request, jsonify
from datetime import datetime as dt

app = Flask(__name__)

@app.route("/x")
def x():
    data = request.get_json()
    passportID = data.get("passportId")
    vote = data.get("vote")
    if not passportID or not vote:
        return jsonify({"error":"Missing data"}), 400
    with open("data/locallog.txt") as f:
        f.write(f"{passportID}, {vote}, {dt.now()}, {request.remote_addr}\n")
    return "done"
app.run(host = "0.0.0.0", port = "5000", debug= True)
