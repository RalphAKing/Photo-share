from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory, send_file
from pymongo import MongoClient
import yaml
from yaml.loader import SafeLoader
from datetime import datetime, timedelta
from bson import ObjectId
from bleach import clean
from werkzeug.security import check_password_hash
import os
import json

def init_json():
    if not os.path.exists('static/photoshare'):
        os.makedirs('static/photoshare')
    
    json_path = 'static/photoshare/files.json'
    if not os.path.exists(json_path):
        with open(json_path, 'w') as f:
            json.dump({}, f)


app = Flask(__name__)
app.secret_key = 'your_secret_key_here' 
init_json()

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






@app.route('/photoshare')
def photo_root():
    if 'userid' not in session:
        return redirect('/login')
    
    with open('static/photoshare/files.json', 'r') as f:
        albums = json.load(f)
    
    user_albums = albums.get(session['userid'], {})
    return render_template('albums.html', albums=user_albums)

@app.route('/photoshare/<album_id>')
def view_album(album_id):
    if 'userid' not in session:
        return redirect('/login')
        
    with open('static/photoshare/files.json', 'r') as f:
        albums = json.load(f)
    
    if album_id in albums.get(session['userid'], {}):
        album_data = albums[session['userid']][album_id]
        return render_template('view_album.html', album=album_data, album_id=album_id, albums=albums)
    return "Album not found", 404



@app.route('/photoshare/share/<album_id>')
def shared_album(album_id):
    with open('static/photoshare/files.json', 'r') as f:
        albums = json.load(f)
    
    for user_id, user_albums in albums.items():
        if album_id in user_albums and user_albums[album_id].get('shared', False):
            album = user_albums[album_id]
            album['owner'] = user_id
            return render_template('shared_album.html', album=album, album_id=album_id, albums=albums)
    return "Shared album not found", 404



@app.route('/photoshare/<album_id>/upload', methods=['GET', 'POST'])
def upload_photos(album_id):
    if 'userid' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        if 'photo' not in request.files:
            return redirect(f'/photoshare/{album_id}')
            
        photos = request.files.getlist('photo')
        
        with open('static/photoshare/files.json', 'r') as f:
            albums = json.load(f)
        
        if album_id in albums[session['userid']]:
            upload_path = f"static/photoshare/{session['userid']}/{album_id}"
            os.makedirs(upload_path, exist_ok=True)
            
            for photo in photos:
                if photo.filename:
                    photo.save(os.path.join(upload_path, photo.filename))
                    if 'photos' not in albums[session['userid']][album_id]:
                        albums[session['userid']][album_id]['photos'] = []
                    albums[session['userid']][album_id]['photos'].append(photo.filename)
            
            with open('static/photoshare/files.json', 'w') as f:
                json.dump(albums, f, indent=4)
                
        return redirect(f'/photoshare/{album_id}')
    
    return render_template('photoshare/view_album.html', album_id=album_id)


@app.route('/photoshare/create', methods=['POST'])
def create_album():
    if 'userid' not in session:
        return redirect('/login')
    
    album_name = request.form['name']
    parent_folder = request.form.get('parent', '')
    
    with open('static/photoshare/files.json', 'r') as f:
        albums = json.load(f)
    
    if session['userid'] not in albums:
        albums[session['userid']] = {}
    
    album_id = f"album_{len(albums[session['userid']]) + 1}"
    full_path = f"{parent_folder}/{album_id}" if parent_folder else album_id
    
    albums[session['userid']][album_id] = {
        'name': album_name,
        'shared': False,
        'parent': parent_folder,
        'is_folder': True,
        'photos': [],
        'path': full_path
    }

    folder_path = f"static/photoshare/{session['userid']}/{full_path}"
    os.makedirs(folder_path, exist_ok=True)
    
    with open('static/photoshare/files.json', 'w') as f:
        json.dump(albums, f, indent=4)
    
    return redirect(f'/photoshare/{parent_folder}' if parent_folder else '/photoshare')


@app.route('/photoshare/toggle-share/<album_id>')
def toggle_share(album_id):
    if 'userid' not in session:
        return redirect('/login')
    
    with open('static/photoshare/files.json', 'r') as f:
        albums = json.load(f)
    
    def toggle_recursive(album_id, new_state):
        if album_id in albums[session['userid']]:
            albums[session['userid']][album_id]['shared'] = new_state
            for child_id, child in albums[session['userid']].items():
                if child.get('parent') == album_id:
                    toggle_recursive(child_id, new_state)
    
    if album_id in albums[session['userid']]:
        new_state = not albums[session['userid']][album_id]['shared']
        toggle_recursive(album_id, new_state)
        
        with open('static/photoshare/files.json', 'w') as f:
            json.dump(albums, f, indent=4)
            
        return jsonify({'shared': new_state})
    return "Album not found", 404









@app.route('/logout')
def logout():
    session.pop('userid', None)
    return redirect('/') 


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)