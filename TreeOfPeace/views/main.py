from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from TreeOfPeace import app
from TreeOfPeace.decorators import isLoggedIn
from TreeOfPeace.utils.db import getCursor
from TreeOfPeace.utils.filters import format_date 

@app.route('/')
def home():
    cursor = getCursor()
    # Get the messages, replies, users info from database
    cursor.execute('''
                   SELECT u.username, u.profile_image AS image, 
                   m.message_id, m.title, m.content, m.created_at AS message_created_at
                   FROM users u
                   INNER JOIN messages m ON u.user_id = m.user_id 
                   ORDER BY m.created_at DESC
                   ''')
    messages = cursor.fetchall()
    return render_template('home.html', messages = messages )

@app.route('/message/<int:message_id>')
def message_detail(message_id):
    """Route for viewing details of a specific message."""
    cursor = getCursor()

    try:
        # Get message, related replies and users info
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
            # Add data to reply list
            if detail ['reply_content']:
                message['replies'].append({
                    'reply_id': detail['reply_id'],
                    'reply_content': detail['reply_content'],
                    'reply_created_at': format_date(detail['reply_created_at']),
                    'reply_username': detail['reply_username'],
                    'reply_image': detail['reply_image']
                })

        return render_template('message_details.html',  message = message)
    except Exception:
        return render_template('error.html', error = 'Something went wrong. Please try again later.')

@app.route('/add_reply/<int:message_id>', methods=['POST'])
@isLoggedIn
def add_reply(message_id):
    """Route for adding a reply to a message."""
    reply_content = request.form['reply_content']
    user_id = session['id']

    # Check if reply_content is empty
    if not reply_content.strip():
        return render_template('error.html', error = 'Reply content cannot be empty')
    else:
        cursor = getCursor()
        try:
            # Add reply to database
            cursor.execute('''
                            INSERT INTO replies (message_id, user_id, content, created_at) 
                            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                            ''', (message_id, user_id, reply_content))
            return redirect(url_for('message_detail', message_id=message_id))
        
        except Exception:
            return render_template('error.html', error = 'Something went wrong. Please try again later.')

@app.route('/add_message', methods=['GET', 'POST'])
@app.route('/<username>/add_message', methods=['GET', 'POST'])
@isLoggedIn
def add_message(username = None):
    """Route for posting a new message."""
    if request.method == 'GET':
        return render_template('add_message.html')
    else:
        user_id = session['id']
        title = request.form['title']
        content = request.form['content']

        # Check if title or content is empty
        if not content.strip() or not title.strip():
            return render_template('add_message.html', error = 'Title or content cannot be empty')
        else:
            cursor = getCursor()
            try:
                # Add a new message to database
                cursor.execute('''
                                INSERT INTO messages (user_id, title, content, created_at) 
                                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)''', (user_id, title, content))

                # Get message id 
                cursor.execute('SELECT LAST_INSERT_ID() AS message_id')
                result= cursor.fetchone()
                message_id = result['message_id']

                # Redirect to new message detail page
                return redirect(url_for('message_detail', message_id=message_id))
            
            except Exception:
                return render_template('error.html', error = 'Something went wrong. Please try again later.')