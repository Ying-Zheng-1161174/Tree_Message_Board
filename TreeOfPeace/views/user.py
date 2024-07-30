from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from datetime import datetime
from TreeOfPeace import app, hashing
import re
import os
from TreeOfPeace.decorators import isLoggedIn, isAuthorized
from TreeOfPeace.utils.db import getCursor
from TreeOfPeace.utils.validators import validate_user_data

PASSWORD_SALT = app.config['PASSWORD_SALT']
DEFAULT_IMAGE = app.config['DEFAULT_IMAGE']
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

@app.route('/<username>/messages', methods=['GET', 'POST'])
@isLoggedIn
@isAuthorized(owner_only=True, allowed_roles=['moderator', 'admin'])
def user_messages(username):
    """Route for viewing and managing a user's messages."""
    cursor = getCursor()
    if request.method == 'GET':
        try:
            # View the loggedin user's messages
            cursor.execute('SELECT * FROM messages WHERE user_id = %s', (session['id'],))
            messages = cursor.fetchall()
            return render_template('user_messages.html', messages = messages)
        except Exception:
            return render_template('error.html', error = 'Something went wrong. Please try again later.') 
    else:
        messageID = request.form['message_id']
        # Allow only loggedin user, admin and moderator to delete a message
        # if username == session['username'] or session['role'] in ['moderator','admin']:
        try:
            # Delete message and replies (ON DELETE CASCADE)
            cursor.execute('DELETE FROM messages WHERE message_id = %s', (messageID,))
            # If delete by moderator or admin, redirect to home page
            if session['role'] in ['moderator','admin']:
                return redirect(url_for('home'))
            # If delete by user, redirect to user's messages page
            else:
                return redirect(url_for('user_messages', username = session['username']))
        except Exception:
            return render_template('error.html', error = 'Something went wrong. Please try again later.') 

@app.route('/<username>/replies', methods=['GET', 'POST'])
@isLoggedIn
@isAuthorized(owner_only=True, allowed_roles=['moderator', 'admin'])
def user_replies(username):
    """Route for viewing and managing a user's replies."""
    cursor = getCursor()
    if request.method == 'GET':
        try:
            cursor.execute('''
                           SELECT r.reply_id, r.message_id, r.content, r.created_at,
                           m.title AS message_title FROM replies r
                           INNER JOIN
                           messages m ON r.message_id = m.message_id
                           WHERE r.user_id = %s
                           ''', (session['id'],))
            replies = cursor.fetchall()
            
            return render_template('user_replies.html', replies = replies)
        except Exception:
            return render_template('error.html', error = 'Something went wrong. Please try again later.') 
    else:
        replyID = request.form['reply_id']
        messageID = request.form['message_id']
        if username == session['username'] or session['role'] in ['moderator','admin']:
            try:
                # Delete a reply
                cursor.execute('DELETE FROM replies WHERE reply_id = %s', (replyID,))
                if session['role'] in ['moderator','admin']:
                    return redirect(url_for('message_detail', message_id= messageID))
                else:
                    return redirect(url_for('user_replies', username = session['username']))
            except Exception:
                return render_template('error.html', error = 'Something went wrong. Please try again later.') 

@app.route('/<username>/profile', methods=['GET', 'POST'])
@isLoggedIn
@isAuthorized(owner_only=True, allowed_roles=['admin'])
def profile(username):
    """Route for viewing and editing a user's profile."""
    cursor = getCursor()

    # Handle editing profile
    if request.method == 'POST' and username == session['username']:
        # Update user's profile
        email = request.form['email']
        firstName = request.form['firstname']
        lastName = request.form['lastname']
        birthDate = request.form['birthdate']
        location = request.form['location']

        # Validate user data
        error = validate_user_data(email, firstName, lastName, birthDate, location)
        if error:
            return render_template('profile.html', username = username, mode='edit', currentdate=datetime.now().date(), default_image=DEFAULT_IMAGE, error=error)
        
        # Handle profile_image changes
        profileImage = request.files['profile_image']
        removeImage = request.form.get('remove_image', 'false') == 'true'

        if removeImage:
            profileImagePath = None
        elif profileImage and profileImage.filename != '':
            filename = profileImage.filename
            profileImagePath = os.path.join(UPLOAD_FOLDER, filename)
            profileImage.save(profileImagePath)
            profileImagePath = f'upload/{filename}'
        else:
            # Retrieve the current profile image path from the database if no action from user
            cursor.execute('SELECT profile_image FROM users WHERE user_id = %s', (session['id'],))
            current_image = cursor.fetchone()
            profileImagePath = current_image['profile_image']            

        try:
            # Update user information
            cursor.execute('UPDATE users SET email = %s, first_name = %s, last_name = %s, birth_date = %s, location = %s, profile_image = %s WHERE user_id = %s', 
                            (email, firstName, lastName, birthDate, location, profileImagePath, session['id']))
            session['message'] = 'Profile updated successfully!'
    
            return redirect(url_for('profile', username=session['username']))
        except Exception:
            return render_template('error.html', error = 'Something went wrong. Please try again later.')
    
    # If it is a Get request, display user information 
    try:
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        msg = session.pop('message', None) 
        # Create a variable, get value from url, set default value to view and pass it to template
        mode = request.args.get('mode', 'view')

        # Check if user is trying to access edit mode without being the owner
        if mode == 'edit' and username != session['username']:
            return render_template('error.html', error='Access Denied')
        
        return render_template('profile.html', account = account, mode = mode, currentdate = datetime.now().date(), default_image = DEFAULT_IMAGE, msg=msg)

    except Exception:
        return render_template('error.html', error = 'Something went wrong. Please try again later.')

@app.route('/<username>/change_password', methods=['GET', 'POST'])
@isLoggedIn
@isAuthorized(owner_only=True)
def change_password(username):
    if request.method == 'GET':
        return render_template('change_password.html')
    else:
        # Get password info from form
        oldPassword = request.form['old_password'] 
        newPassword = request.form['password']
        confirmPassword = request.form['confirm_password']
        oldPassword_hash = hashing.hash_value(oldPassword, PASSWORD_SALT)  
        
    error = ''
    cursor = getCursor()
    
    try:
        # Retrieve the current hashed password from the database
        cursor.execute('SELECT password_hash FROM users WHERE user_id = %s', (session['id'],))
        account = cursor.fetchone()
        # Check if the new pass is different to the old pass, and new pass matched confirm pass
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
            return render_template('change_password.html', username=session['username'], msg = 'Password updated successfully!')
        
        if error:
            return render_template('change_password.html', error = error)
        
    except Exception:
        return render_template('error.html', error = 'Something went wrong. Please try again later.')

if __name__ == '__main__':
    app.run(debug=True)