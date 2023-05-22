from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
# from init_db import add_text
import sys
import os
import click
from werkzeug.security import generate_password_hash, check_password_hash

# conn = sqlite3.connect('database_name.db')
# c = conn.cursor()
# c.execute('SELECT * FROM users')
# rows = c.fetchall()
# for row in rows:
#     print(row)
# conn.close()
# welcome message
global names
name_message = { 'message' : 'Welcome to Sportsy',
          'firstname' :'' }

names = [name_message]

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

# app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ics4u'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


class User(db.Model, UserMixin):
    
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname=db.Column(db.String(20))
    lname=db.Column(db.String(20))
    email=db.Column(db.String(20))
    password_hash=db.Column(db.String(128))
    dob = db.Column(db.Date)
    pb = db.Column(db.String(20))
    healthinfo=db.Column(db.String(20))
    dom_side = db.Column(db.String(5))
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(self.password_hash)
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=('GET', 'POST'))
def index():
    # conn = get_db_connection()
    # username = conn.execute('SELECT * FROM users').fetchall()
    # conn.close()
    if request.method == "POST":
        
        irstfname = request.form.get("firstname")
        name_message['firstname'] = str(irstfname)
        return render_template('index.html',  names = names)
    return render_template('index.html',  names = names)

@app.route('/profile')
def profile():
    return render_template('profile.html')
  
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

conn = None
cursor = None

@app.route('/calendar-events')
def calendar_events():

	try:
		conn = sqlite3.connect()
		cursor = conn.cursor(sqlite3.cursors.DictCursor)
		cursor.execute("SELECT id, title, url, class, UNIX_TIMESTAMP(start_date)*1000 as start, UNIX_TIMESTAMP(end_date)*1000 as end FROM event")
		rows = cursor.fetchall()
		resp = jsonify({'success' : 1, 'result' : rows})
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/roster')
def roster():
    return render_template('roster.html', rostername = "yo name")

#adding textbox to roster
@app.route("/add_text", methods=["POST","GET"])
def addText():
    if request.method == "POST":
        text_value = request.form["textv"]
        #saving to database
        add_new = add_text(text_value)
        return redirect(url_for('name'))
    else:
        return render_template('index.html')
    

@app.route('/login', methods=["POST", "GET"])
def login():
    # form = LoginForm()
    # if form.validate_on_submit():
    #     login_user(user) 
    if request.method =="POST":
        email = request.form["email"]
        password = request.form["password"]
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect('/')
        
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/signup')
def signup():
    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        password=request.form['password']
        dob=request.form['dob']
        pb=request.form['pb']
        healthinfo=request.form['healthinfo']
        right=request.form['right']
        left=request.form['left']
        
        if right=='on':
            dom_side = 'right'
        elif left=='on':
            dom_side='left'     
        
        
        user = User(fname=fname, lname=lname, email=email, dob=dob,pb=pb, healthinfo=healthinfo, dom_side=dom_side)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/playerorcoach')
def player_or_coach():
    return render_template('playerorcoach.html')

@app.route('/coachsignup')
def coach_signup():
    return render_template('coach_signup.html')

@app.route('/playersignup')
def player_signup():
    return render_template('player_signup.html')
    
