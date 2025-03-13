from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory, send_file
from pymongo import MongoClient
import yaml
from yaml.loader import SafeLoader
from datetime import datetime, timedelta
from bson import ObjectId
from bleach import clean
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' 
UPLOAD_FOLDER = 'storage'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Database configuration
with open('config.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)

# Database collections
def accounts():
    cluster = MongoClient(config["mongodbaddress"], connect=False)
    return cluster["RKingIndustries"]["accounts"]

def unverified_accounts():
    cluster = MongoClient(config["mongodbaddress"], connect=False)
    return cluster["RKingIndustries"]["unverified_accounts"]

def boards():
    cluster = MongoClient(config["mongodbaddress"], connect=False)
    return cluster["RKingIndustries"]["boards"]

# Routes
@app.route('/login', methods=["GET", "POST"])
def login():
    if 'userid' in session:
        logged_accounts=accounts()
        account = logged_accounts.find_one({'userid':session['userid']})
        if account != None:
            return redirect('/')
        else:
            session.pop('userid', None)
    if request.method == 'POST':
        logged_accounts=accounts()
        email = (request.form['email']).lower()
        password = request.form['password']

        account = logged_accounts.find_one({'email':email})
        if account != None:
            if check_password_hash(account['password'], password):
                session['userid'] = account['userid']
                try:
                    try:
                        account['score']
                    except:
                        account['score'] = 0
                        logged_accounts.replace_one({'userid':session['userid']}, account)
                    data=boards()
                    found = data.find_one({'owner':account['userid']})
                    if found == None:
                        name=f"{account['username']}'s Board"
                        number=0
                        while data.find_one({"name":name}) != None:
                            number+=1
                            name=f"{account['username']}'s Board {number}"
                        data.insert_one({"name": name, "description":f"{account['username']}'s Board", "owner":account['userid'], "members":[]})                          
                except:
                    print('failed')
                return redirect('/')
            else:
                return render_template('login.html', error='Invalid Password')
        else:
            unaccounts = unverified_accounts()
            if unaccounts.find_one({'email':email}):
                return redirect('/verify')
            return render_template('login.html', error='Invalid Email')

    return render_template('login.html')


















@app.route('/logout')
def logout():
    session.pop('userid', None)
    return redirect('/') 


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)