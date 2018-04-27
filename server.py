from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'iasoeriua8w4raeirua'
mysql = MySQLConnector(app,'thewalldb')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def insert():
    valid = True
    if len(request.form['first_name']) < 2 or request.form['first_name'].isalpha() == False or len(request.form['last_name']) < 2 or request.form['last_name'].isalpha() == False:
        flash("First Name and Last Name should have at least 2 characters and only letters!") 
        valid = False
    if len(request.form['email']) < 1 or not EMAIL_REGEX.match(request.form['email']):
        flash("E-mail should not be empty and should be valid!")
        valid = False
    if len(request.form['password']) < 8:
        flash("Password should be at least 8 characters long")
        valid = False
    elif request.form['password'] != request.form['confirm_password']:
        flash("Password does not match")
        valid = False
    if valid == True:
        query_insert = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        data_insert = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'password': md5.new(request.form['password']).hexdigest(),
               }
        print data_insert
        mysql.query_db(query_insert, data_insert)
        query_select = "SELECT id, first_name, last_name FROM users WHERE email = :email"
        data_select = {
            'email': request.form['email']
        }
        response = mysql.query_db(query_select, data_select)
        print response
        session['id'] = response[0]['id']
        session['fname'] = response[0]['first_name']
        session['lname'] = response[0]['last_name']
        print session['id']
        query_select = "SELECT messages.message, DATE_FORMAT(messages.updated_at,'%c/%d/%y %r') AS updated_at, users.first_name, users.last_name FROM users JOIN messages ON users.id = messages.user_id ORDER BY messages.updated_at DESC"
        messages = mysql.query_db(query_select)
        return render_template ('success.html', postmessages=messages)
    else:
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    valid = True
    if len(request.form['email']) < 1 or  len(request.form['password']) < 1:
        flash("Please inform e-mail and password to log in!")
        valid = False
        return redirect('/') 
    if valid == True:
        query_select = "SELECT * FROM users WHERE email = :email AND password = :password"
        data_select = {
            'email': request.form['email'],
            'password': md5.new(request.form['password']).hexdigest(),
        }
        user = mysql.query_db(query_select, data_select)
        if user == []:
            flash("User not found!")
            return redirect('/') 
        else:
            session['id'] = user[0]['id']
            query_select = "SELECT first_name, last_name FROM users WHERE id = :id"
            data_select = {
                'id': session['id'],
            }
            response = mysql.query_db(query_select, data_select)
            session['fname'] = response[0]['first_name']
            session['lname'] = response[0]['last_name']
            # flash("Welcome {} {}" .format(response[0]['first_name'],response[0]['last_name']))
            print response
            query_select = "SELECT messages.message, DATE_FORMAT(messages.updated_at,'%c/%d/%y %r') AS updated_at, users.first_name, users.last_name FROM users JOIN messages ON users.id = messages.user_id ORDER BY messages.updated_at DESC"
            messages = mysql.query_db(query_select)
            return render_template('success.html', postmessages=messages)

@app.route('/postmessage', methods=['POST'])
def message():

    if len(request.form['message']) < 1:
        flash("Message cannot be empty")
    else:
        query_insert = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id, :message, now(), now())"
        data_insert = {
            'user_id': session['id'],
            'message': request.form['message'],
        }
        print data_insert
        mysql.query_db(query_insert,data_insert)
        flash("Message posted")
        query_select = "SELECT messages.message, DATE_FORMAT(messages.updated_at,'%c/%d/%y %r') AS updated_at , users.first_name, users.last_name FROM users JOIN messages ON users.id = messages.user_id ORDER BY messages.updated_at DESC"
        messages = mysql.query_db(query_select)

    return render_template('success.html', postmessages=messages)

@app.route('/postcomment', methods=['POST'])
def comment():

    if len(request.form['comment']) < 1:
        flash("Message cannot be empty")
    else:
        query_insert = "INSERT INTO comments (user_id, message_id, comment, created_at, updated_at) VALUES (:user_id, :message_id, comment, now(), now())"
        data_insert = {
            'user_id': session['id'],
            'message_id': ...,
            'comment': request.form['comment']
        }
        mysql.query_db(query_insert,data_insert)
        flash("Comment posted!")
    return render_template('success.html')

app.run(debug=True)
