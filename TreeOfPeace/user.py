from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask_hashing import Hashing
from datetime import datetime
from datetime import date
from TreeOfPeace import app
from TreeOfPeace import connect
import mysql.connector
import re
import os
from TreeOfPeace.filters import format_date 
from flask import flash

# Create an instance of hashing
hashing = Hashing(app)

PASSWORD_SALT = 'thisismypasswordsalt'
# Default role assigned to new users upon sign up
DEFAULT_ROLE = 'member'
# Default status for all users
DEFAULT_STATUS = 'active'
# Default images for all users
DEFAULT_IMAGE = 'upload/tree.png'

# Default folder for saving profile_image
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.jinja_env.filters['format_date'] = format_date

# Setup Database connection
db_connection = None

def getCursor():
    """
    Get a MySQL cursor with a dictionary format.
    If the connection does not exist or is not connected, it will create a new connection.
    """

    global db_connection

    if db_connection is None or not db_connection.is_connected():
        db_connection = mysql.connector.connect(
            user=connect.dbuser,
            password=connect.dbpass,
            host=connect.dbhost,
            auth_plugin='mysql_native_password',
            database=connect.dbname,
            autocommit=True
        )

    cursor = db_connection.cursor(dictionary=True)

    return cursor

@app.route('/')
def home():
    cursor = getCursor()
    
    # Get the messages, replies, users info from database
    cursor.execute('''
                   SELECT u.username, u.profile_image AS image, 
                   m.message_id, m.title, m.created_at AS message_created_at
                   FROM users u
                   INNER JOIN messages m ON u.user_id = m.user_id 
                   ORDER BY m.created_at DESC
                   ''')
    messages = cursor.fetchall()

    return render_template('message_title.html', messages = messages )

@app.route('/message/<int:message_id>')
def message_detail(message_id):
    cursor = getCursor()
    # Initial an error variable for handle the error from server side

    try:
        cursor.execute('''
                    SELECT 
                    u.username AS message_username, 
                    u.profile_image AS message_profile_image, 
                    m.message_id, 
                    m.title,
                    m.content AS message_content, 
                    m.created_at AS message_created_at, 
                    reply_id,
                    r.content AS reply_content, 
                    r.created_at AS reply_created_at,
                    r.user_id AS reply_user_id,
                    ur.username AS reply_username,
                    ur.profile_image AS reply_image
                    From messages m
                    INNER JOIN users u ON m.user_id = u.user_id 
                    LEFT JOIN replies r ON m.message_id = r.message_id
                    LEFT JOIN users ur ON r.user_id = ur.user_id
                    WHERE m.message_id = %s
                    ORDER BY m.created_at DESC
                    ''', (message_id,))
        messageDetails = cursor.fetchall()
        if not messageDetails:
            return render_template('error.html', error = 'Page not found')
        
        # Handle returned data, create a dictionary for display the specific message
        message = {
            'username': messageDetails[0]['message_username'],
            'image': messageDetails[0]['message_profile_image'],
            'message_id': messageDetails[0]['message_id'], 
            'title': messageDetails[0]['title'],
            'message_content': messageDetails[0]['message_content'],
            'message_created_at':format_date(messageDetails[0]['message_created_at']),
            'replies':[]
        }

        # Check if any replies for a specific message
        for detail in messageDetails:
            # if there is a reply
            if detail ['reply_content']:
                message['replies'].append({
                    'reply_id': detail['reply_id'],
                    'reply_content': detail['reply_content'],
                    'reply_created_at': format_date(detail['reply_created_at']),
                    'reply_username': detail['reply_username'],
                    'reply_image': detail['reply_image']
                })

        return render_template('message_details.html',  message = message)
    except Exception as e:
        return f'An error occurred: {str(e)}'

@app.route('/add_reply/<int:message_id>', methods=['POST'])
def add_reply(message_id):
    if 'loggedin' in session:
        reply_content = request.form['reply_content']
        user_id = session['id']

        # Check if reply_content is empty
        if not reply_content.strip():
            return render_template('error.html', error = 'Reply content cannot be empty')
        else:
            cursor = getCursor()
            try:
                cursor.execute('''
                               INSERT INTO replies (message_id, user_id, content, created_at) 
                               VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                               ''', (message_id, user_id, reply_content))
                db_connection.commit()
                return redirect(url_for('message_detail', message_id=message_id))
            except Exception as e:
                return f'An error occurred: {str(e)}'

    else:       
        return redirect(url_for('login'))

@app.route('/add_message', methods=['GET', 'POST'])
@app.route('/<username>/add_message', methods=['GET', 'POST'])
def add_message(username = None):
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('add_message.html')
        else:
            user_id = session['id']
            title = request.form['title']
            content = request.form['content']

            if not content.strip() or not title.strip():
                return render_template('add_message.html', error = 'Title or content cannot be empty')
            else:
                cursor = getCursor()
                try:
                    cursor.execute('''
                                   INSERT INTO messages (user_id, title, content, created_at) 
                                   VALUES (%s, %s, %s, CURRENT_TIMESTAMP)''', (user_id, title, content))
                    db_connection.commit()

                    # Get message id 
                    cursor.execute('SELECT LAST_INSERT_ID() AS message_id')
                    result= cursor.fetchone()
                    message_id = result['message_id']

                    # Redirect to message detail page
                    return redirect(url_for('message_detail', message_id=message_id))
                except Exception as e:
                    return f'An error occurred: {str(e)}'
    else:
        return redirect(url_for('login'))

@app.route('/<username>/messages', methods=['GET', 'POST'])
def user_messages(username):
    cursor = getCursor()
    if 'loggedin' in session:
        if request.method == 'GET':
            try:
                cursor.execute('SELECT message_id, title, created_at FROM messages WHERE user_id = %s', (session['id'],))
                messages = cursor.fetchall()
                return render_template('user_messages.html', messages = messages)
            except Exception as e:
                return f'An error occurred: {str(e)}' 
        else:
            messageID = request.form['message_id']
            if username == session['username'] or session['role'] in ['moderator','admin']:
                try:
                    # Delete message and replies (ON DELETE CASCADE)
                    cursor.execute('DELETE FROM messages WHERE message_id = %s', (messageID,))
                    db_connection.commit()
                    if session['role'] in ['moderator','admin']:
                        return redirect(url_for('home'))
                    else:
                        return redirect(url_for('user_messages', username = session['username']))
                except Exception as e:
                    return f'An error occurred: {str(e)}' 
    else:
        return redirect(url_for('login'))

@app.route('/<username>/replies', methods=['GET', 'POST'])
def user_replies(username):
    cursor = getCursor()
    if 'loggedin' in session:
        if request.method == 'GET':
            try:
                cursor.execute('SELECT reply_id, message_id, content, created_at FROM replies WHERE user_id = %s', (session['id'],))
                replies = cursor.fetchall()
                return render_template('user_replies.html', replies = replies)
            except Exception as e:
                return f'An error occurred: {str(e)}' 
        else:
            replyID = request.form['reply_id']
            messageID = request.form['message_id']
            if username == session['username'] or session['role'] in ['moderator','admin']:
                try:
                    # Delete message and replies (ON DELETE CASCADE)
                    cursor.execute('DELETE FROM replies WHERE reply_id = %s', (replyID,))
                    db_connection.commit()
                    if session['role'] in ['moderator','admin']:
                        return redirect(url_for('message_detail', message_id= messageID))
                    else:
                        return redirect(url_for('user_replies', username = session['username']))
                except Exception as e:
                    return f'An error occurred: {str(e)}' 
    else:
        return redirect(url_for('login'))
    
@app.route('/admin', methods=['GET'])
@app.route('/admin/<username>', methods=['GET','POST'])
def admin(username=None):
    cursor = getCursor()
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'GET':
            if username is None:
                # Handle search 
                search = request.args.get('search', '')
                # For full name search, split search string into a list based on the space
                searchParts = search.split(' ')
               
                if search:
                    if len(searchParts) == 1:
                        cursor.execute('''
                                    SELECT username, first_name, last_name, profile_image, location FROM users 
                                    WHERE username LIKE %s 
                                    OR first_name LIKE %s
                                    OR last_name LIKE %s
                                    ''', (f'%{search}%', f'%{search}%', f'%{search}%'))
                    elif len(searchParts) >= 2:
                        cursor.execute('''
                                    SELECT username, first_name, last_name, profile_image, location FROM users 
                                    WHERE first_name LIKE %s AND last_name LIKE %s
                                    ''', (f'%{searchParts[0]}%', f'%{searchParts[1]}%'))
                else:
                    # List all users
                    cursor.execute('SELECT username, first_name, last_name, profile_image, location FROM users')
               
                users = cursor.fetchall()
                return render_template('user_list.html', users = users, search = search)
            else:
                return redirect(url_for('profile', username = username))
            
        elif request.method == 'POST' and username is not None:
            role = request.form['role']
            status = request.form['status']
            try:
                cursor.execute('UPDATE users SET role = %s, status = %s WHERE username = %s', 
                                (role, status, username))
                db_connection.commit()
                session['message'] = 'Change saved!'
                return redirect(url_for('profile', username = username))
            except Exception as e:
                return f'An error occurred: {str(e)}'
    else:
        return render_template('error.html', error = 'Access Denied')

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

        # Check if username exists 
        cursor = getCursor()
        # Initial an error variable for handle the error from server side
        error = ''

        # If account exists show error and validation checks
        try:
            cursor.execute('SELECT user_id FROM users WHERE username = %s', (userName,))
            account = cursor.fetchone()
            if account:
                error = 'username already exists, please change another one'
            elif not re.match(r'[A-Za-z0-9]+', userName):
                error = 'Username must contain only characters and numbers.'
            elif not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
                error = 'Invalid password, please try again'
            elif confirmPassword != password:
                error = 'password do not match'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                error = 'Invalid email address'
            elif not re.match(r'[A-Za-z]+', firstName):
                error = 'Please enter letters (a-z,A-Z) only'
            elif not re.match(r'[A-Za-z]+', lastName):
                error = 'Please enter letters (a-z,A-Z) only'
            elif not userName or not firstName or not lastName or not birthDate or not location or not email or not password:
                error = 'Please fill out the form completely'
            else:
                # Data is valid, create account for user
                password_hash = hashing.hash_value(password, PASSWORD_SALT)  
                cursor.execute('INSERT INTO users (username, password_hash, email, first_name, last_name, birth_date, location, profile_image, role, status) VALUES \
                                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                                (userName, password_hash, email, firstName, lastName, birthDate, location, DEFAULT_IMAGE, DEFAULT_ROLE, DEFAULT_STATUS ))
                db_connection.commit()
                
                cursor.execute('SELECT user_id, username, role FROM users WHERE username = %s', (userName,))
                account = cursor.fetchone()

                if account:
                    session['loggedin'] = True
                    session['id'] = account['user_id']
                    session['username'] = account['username']
                    session['role'] = account['role']
                    return render_template('success_redirect.html', success='Registration successful!')
                else:
                    error = 'Failed to create account, please try again'

            if error:
                return render_template('register.html', error = error)
                    
        except Exception as e:
            return f'An error occurred: {str(e)}'       

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
                return render_template('login.html', error = 'Incorrect username or password') 

        except Exception as e:
            return f'An error occurred: {str(e)}'

@app.route('/<username>/profile', methods=['GET', 'POST'])
def profile(username):
    cursor = getCursor()

    # Check if user is logged in
    if 'loggedin' in session or session['role'] == 'admin':
        if request.method == 'POST':
            # Update user's profile
            email = request.form['email']
            firstName = request.form['firstname']
            lastName = request.form['lastname']
            birthDate = request.form['birthdate']
            location = request.form['location']
            
            profileImage = request.files['profile_image']
            removeImage = request.form.get('remove_image', 'false') == 'true'

            if removeImage:
                profileImagePath = None
            elif profileImage and profileImage.filename != '':
                filename = profileImage.filename
                profileImagePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profileImage.save(profileImagePath)
                profileImagePath = f'upload/{filename}'
            else:
                # Retrieve the current profile image path from the database
                cursor.execute('SELECT profile_image FROM users WHERE user_id = %s', (session['id'],))
                current_image = cursor.fetchone()
                profileImagePath = current_image['profile_image']            

            try:
                cursor.execute('UPDATE users SET email = %s, first_name = %s, last_name = %s, birth_date = %s, location = %s, profile_image = %s WHERE user_id = %s', 
                               (email, firstName, lastName, birthDate, location, profileImagePath, session['id']))
                db_connection.commit()
                session['message'] = 'Profile updated successfully!'
      
                return redirect(url_for('profile', username=session['username']))
            except Exception as e:
                return f'An error occurred: {str(e)}'
        
        # If it is a Get request, display user information 
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()
            msg = session.pop('message', None) 
            # Create a variable, get value from url, set default value to view and pass it to template
            mode = request.args.get('mode', 'view')
            return render_template('profile.html', account = account, mode = mode, currentdate = datetime.now().date(), default_image = DEFAULT_IMAGE, msg=msg)

        except Exception as e:
            return f'An error occurred: {str(e)}'
            
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Remove session data
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('role', None)

    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/<username>/change_password', methods=['GET', 'POST'])
def change_password(username):
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('change_password.html')
        else:
            oldPassword = request.form['old_password'] 
            newPassword = request.form['password']
            confirmPassword = request.form['confirm_password']
            oldPassword_hash = hashing.hash_value(oldPassword, PASSWORD_SALT)  
            
        error = ''
        cursor = getCursor()

        # Retrieve the current hashed password from the database
        try:
            cursor.execute('SELECT password_hash FROM users WHERE user_id = %s', (session['id'],))
            account = cursor.fetchone()
            if oldPassword_hash != account['password_hash']:
                error = 'Old password is incorrect'
            elif confirmPassword != newPassword:
                error = 'password do not match'
            elif oldPassword == newPassword:
                error = 'New password cannot be the same as the old password'
            else:
                # Password is valid, update it to database
                password_hash = hashing.hash_value(newPassword, PASSWORD_SALT)  
                cursor.execute('UPDATE users SET password_hash = %s WHERE user_id = %s', 
                                (password_hash, session['id']))
                db_connection.commit()
                return render_template('change_password.html', username=session['username'], msg = 'Password updated successfully!')
            
            if error:
                return render_template('change_password.html', error = error)
            
        except Exception as e:
            return f'An error occurred: {str(e)}'
                 
    else:
        return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

if __name__ == '__main__':
    app.run(debug=True)