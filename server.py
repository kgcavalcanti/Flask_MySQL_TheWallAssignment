from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
from datetime import datetime 
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
        query_select = "SELECT id, CONCAT_WS(' ', first_name, last_name) AS full_name FROM users WHERE email = :email"
        data_select = {
            'email': request.form['email']
        }
        user = mysql.query_db(query_select, data_select)
        session['id'] = user[0]['id']
        session['full_name'] = user[0]['full_name']
        return redirect ('/wall')
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
        query_select = "SELECT id, CONCAT_WS(' ', first_name, last_name) AS full_name FROM users WHERE email = :email AND password = :password"
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
            session['full_name'] = user[0]['full_name']
            response = mysql.query_db(query_select, data_select)           
            return redirect('/wall')



@app.route('/wall')
def wall():
    query_comments = "SELECT comments.id AS comment_id, comments.message_id AS message_id, DATE_FORMAT(comments.updated_at, '%M %d %y %r') AS comment_updated, comments.comment, CONCAT_WS(' ', users.first_name,users.last_name) AS comment_full_name FROM comments JOIN users ON comments.user_id = users.id ORDER BY comments.updated_at DESC"
    comments = mysql.query_db(query_comments)
    print comments
    query_messages = "SELECT messages.id AS message_id, messages.message, DATE_FORMAT(messages.updated_at, '%M %d %y %r') AS message_updated, CONCAT_WS(' ', users.first_name,users.last_name) AS message_full_name FROM messages JOIN users ON messages.user_id = users.id ORDER BY messages.updated_at DESC"
    messages = mysql.query_db(query_messages)
    print messages
    return render_template('success.html', postmessages=messages, postcomments=comments)



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
    return redirect('/wall')



@app.route('/postcomment/<message_id>', methods=['POST'])
def comment(message_id):
    if len(request.form['comment']) < 1:
        flash("Message cannot be empty")
    else:
        query_insert = "INSERT INTO comments (user_id, message_id, comment, created_at, updated_at) VALUES (:user_id, :specific_id, :comment, now(), now())"
        data_insert = {
            'user_id': session['id'],
            'specific_id': message_id,
            'comment': request.form['comment'],
        }


        print data_insert
        mysql.query_db(query_insert,data_insert)
        flash("Comment posted!")
    return redirect('/wall')


@app.route('/deletemessage/<message_id>')
def delete_message(message_id):
    query_deletecomments = "DELETE FROM comments WHERE message_id = :specific_id"
    data_delete = {
        'specific_id': message_id,
    }
    mysql.query_db(query_deletecomments,data_delete)
    query_deletemessages = "DELETE FROM messages WHERE id = :specific_id"
    data_delete = {
        'specific_id': message_id,
    }
    mysql.query_db(query_deletemessages,data_delete)
    flash("Message deleted!")
    return redirect('/wall')


app.run(debug=True)
