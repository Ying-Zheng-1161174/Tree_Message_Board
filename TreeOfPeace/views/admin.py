from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from TreeOfPeace import app
from TreeOfPeace.decorators import isLoggedIn
from TreeOfPeace.utils.db import getCursor

@app.route('/admin', methods=['GET'])
@app.route('/admin/<username>', methods=['GET','POST'])
@isLoggedIn
def admin(username=None):
    """
    Route for admin views only.
    GET: List all users or search users.
    POST: Update user role or status.
    """
    cursor = getCursor()
    if session['role'] == 'admin':
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
    
                session['message'] = 'Change saved!'
                return redirect(url_for('profile', username = username))
            except Exception:
                return render_template('error.html', error = 'Something went wrong. Please try again later.')
    else:
        return render_template('error.html', error = 'Access Denied')