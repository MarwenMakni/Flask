import sqlite3
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from keras.models import load_model
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import os
from flask_login import current_user




app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
login_manager = LoginManager(app)
login_manager.login_view = 'login'


def preprocess_image(img):
    img = cv2.resize(img, (100, 100))
    img = img[np.newaxis, :]
    return img

def read_users():
    if os.path.exists('users.txt'):
        with open('users.txt', 'r') as f:
            users = {}
            for line in f.readlines():
                user_id, username, password = line.strip().split(',')
                users[int(user_id)] = User(int(user_id), username, password)
            return users
    else:
        return {}

def write_users(users):
    with open('users.txt', 'w') as f:
        for user in users.values():
            f.write(f'{user.id},{user.username},{user.password}\n')

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    users = read_users()
    return users.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = read_users()
        user_id = max(users.keys(), default=-1) + 1
        user = User(user_id, username, password)
        users[user_id] = user
        write_users(users)
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = read_users()
        user = None
        for user_data in users.values():
            if user_data.username == username and user_data.password == password:
                user = user_data
                break
        if user:
            login_user(user)
            if user.username == 'admin':
                return redirect(url_for('database'))
            else:
                return redirect(url_for('predict'))
        else:
            flash('Login unsuccessful. Please check your credentials and try again.', 'danger')
    return render_template('login.html')
model_files = [    'model1.h5',    'model2.h5',    'model3.h5']

from flask_login import current_user, login_required

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    filename = None
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = ''

    if request.method == 'POST':
        if 'button1' in request.form:
            print('Button 1 clicked!')
            model = load_model('model.h5')
        elif 'button2' in request.form:
            print('Button 2 clicked!')
            model = load_model('model.h5')
        elif 'button3' in request.form:
            print('Button 3 clicked!')
            model = load_model('model.h5')
        else:
            print('Button xx clicked!')
        
        file = request.files['image']
        filename = secure_filename(file.filename)
        image_path = os.path.join('static/uploads', filename)
        file.save(image_path)

        img = cv2.imread(image_path)
        img = preprocess_image(img)

        model = load_model('model.h5')
        prediction = model.predict(img)
        result = np.argmax(prediction)
        if result == 0:
            result = 'Melanocytic nevi (nv)'
        elif result == 1:
            result = 'Melanoma (mel)'
        elif result == 2:
            result = 'Benign keratosis-like lesions (bkl)'
        elif result == 3: 
            result = 'Basal cell carcinoma (bcc))' 
        elif result == 4:
            result = 'Actinic keratoses (akiec)'
        elif result == 5:
            result = 'Vascular lesions (vasc)'
        elif result == 6:
            result = 'Dermatofibroma (df)' 

        # Ajoutez cette instruction pour insérer dans la base de données
        conn = sqlite3.connect('database.db')
        conn.execute('''
             INSERT INTO users (name, entry_time, classification)
             VALUES (?, ?, ?)
        ''', (username, datetime.now(), result))
        conn.commit()
        conn.close()
    
        return render_template('predict.html', result=result, filename=filename)

    # Gestion de la méthode GET
    return render_template('predict.html', filename=filename)



    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def home():
    return redirect(url_for('login'))








import sqlite3

# Connexion à la base de données (création si elle n'existe pas)
conn = sqlite3.connect('database.db')

# Création de la table
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        classification TEXT
    )
''')

# Fermeture de la connexion à la base de données
conn.close()




import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('database.db')

# Récupération des données
cursor = conn.execute('SELECT * FROM users')

# Génération du tableau HTML
table_html = '<table class="table">'
table_html += '<thead><tr><th>Entry ID</th><th>Name</th><th>Date and Time of Entry</th><th>Classification</th></tr></thead>'
table_html += '<tbody>'
for row in cursor:
    entry_id = row[0]
    name = row[1]
    entry_time = row[2]
    classification = row[3]
    
    # Ajout d'une ligne au tableau
    table_html += f'<tr><td>{entry_id}</td><td>{name}</td><td>{entry_time}</td><td>{classification}</td></tr>'
table_html += '</tbody></table>'

# Fermeture du curseur et de la connexion à la base de données
cursor.close()
conn.close()

# Utilisez la variable 'table_html' pour afficher le tableau dans votre page HTML




from flask import render_template
from datetime import datetime
import sqlite3

@app.route('/database')
def database():
    # Connexion à la base de données
    conn = sqlite3.connect('database.db')

    # Récupération des données
    cursor = conn.execute('SELECT * FROM users')

    # Génération du tableau HTML
    table_html = '<table class="table">'
    table_html += '<thead><tr><th>Entry ID</th><th>Name</th><th>Date and Time of Entry</th><th>Classification</th></tr></thead>'
    table_html += '<tbody>'
    for row in cursor:
        entry_id = row[0]
        name = row[1]
        entry_time = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f')
        entry_date = entry_time.strftime('%Y-%m-%d')
        entry_hour = entry_time.strftime('%H:%M:%S')
        classification = row[3]

        # Ajout d'une ligne au tableau
        table_html += f'<tr><td>{entry_id}</td><td>{name}</td><td>{entry_date} {entry_hour}</td><td>{classification}</td></tr>'
    table_html += '</tbody></table>'

    # Fermeture du curseur et de la connexion à la base de données
    cursor.close()
    conn.close()

    return render_template('database.html', table_html=table_html)


if __name__ == '__main__':
    app.run(debug=True)
