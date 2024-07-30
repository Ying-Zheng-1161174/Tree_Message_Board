from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from datetime import datetime
from TreeOfPeace import app, hashing
import re
from TreeOfPeace.utils.db import getCursor
from TreeOfPeace.utils.validators import validate_user_data

PASSWORD_SALT = app.config['PASSWORD_SALT']
DEFAULT_ROLE = app.config['DEFAULT_ROLE']
DEFAULT_STATUS = app.config['DEFAULT_STATUS']
DEFAULT_IMAGE = app.config['DEFAULT_IMAGE']

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', currentdate = datetime.now().date())
    
    else:
        # Create variables for access
        userName = request.form['username']
        password = request.form['password']
        confirmPassword = request.form['confirm_password']
        email = request.form['email']
        firstName = request.form['firstname']
        lastName = request.form['lastname']
        birthDate = request.form['birthdate']
        location = request.form['location']
        
        cursor = getCursor()
        # Initial error msg
        error = ''

        try:
            cursor.execute('SELECT user_id FROM users WHERE username = %s', (userName,))
            account = cursor.fetchone()

            # Check if username exists 
            if account:
                error = 'username already exists, please change another one'
            elif not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
                error = 'Invalid password, please try again'
            elif confirmPassword != password:
                error = 'password do not match'
            elif not password:
                error = 'password cannot be empty'
            else:
                # Validate other data
                error = validate_user_data(email, firstName, lastName, birthDate, location)

            if error:
                return render_template('register.html', error = error)
           
            # Data is valid, create account for user
            password_hash = hashing.hash_value(password, PASSWORD_SALT)  
            cursor.execute('INSERT INTO users (username, password_hash, email, first_name, last_name, birth_date, location, profile_image, role, status) VALUES \
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                            (userName, password_hash, email, firstName, lastName, birthDate, location, DEFAULT_IMAGE, DEFAULT_ROLE, DEFAULT_STATUS ))
            # After registered, redirect user to login page
            return render_template('login.html', success='Registration successful! please login.')

            
                    
        except Exception:
            return render_template('error.html', error = 'Something went wrong. Please try again later.')       

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    else:
        # Create variables for access
        userName = request.form['username']
        userPassword = request.form['password']

        # Check if username exists 
        cursor = getCursor()

        # If account exists show error and validation checks
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (userName,))
            account = cursor.fetchone()
            if account and hashing.check_value(account['password_hash'], userPassword, PASSWORD_SALT):
                # If password correct, create session data
                session['loggedin'] = True
                session['id'] = account['user_id']
                session['username'] = account['username']
                session['role'] = account['role']
                # redirect to home page
                return redirect(url_for('home'))
            else:
                # Password wrong, redirect to login page
                return render_template('login.html', error = 'Incorrect username or password') 

        except Exception:
            return render_template('error.html', error = 'Something went wrong. Please try again later.')
        
@app.route('/logout')
def logout():
    # Remove session data
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('role', None)
    session.pop('username', None)

    # Redirect to login page
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404