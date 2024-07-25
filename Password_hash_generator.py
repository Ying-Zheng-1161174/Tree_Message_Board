"""Script to generate password hashes for one or more user accounts.

You can use this script to generate flask_hashing password hashes for all of
the initial user accounts in your database creation script. Remember that each
of your user accounts should have its own unique password.

You'll need to make two changes before running this script:

1.  Replace the value of constant PASSWORD_SALT, 'ExampleSaltValue', with
    whatever salt value you're using in your web app.

2.  Replace the list of user accounts (the block beginning "users = [") with
    the actual list of user accounts you need to generate hashes for.
"""
from collections import namedtuple
from flask import Flask
from flask_hashing import Hashing

# IMPORTANT: Change 'ExampleSaltValue' to whatever salt value you'll use in
# your application. If you don't do this, your password hashes won't work!
PASSWORD_SALT = 'thisismypasswordsalt'

# We use a "named tuple" here to create a simple "User Account" class that can
# store a username and password.
# 
# Don't worry if you haven't seen this before: it's just a simple way of
# storing those two pieces of data together in one variable. It also lets us
# access the username and password by name: for example, if we create a
# UserAccount named "myuser", like this:
# 
# myuser = UserAccount('myusername', 'mypassword')
# 
# We can then access those values via "myuser.username" and "myuser.password",
# instead of having to access myuser[0] and myuser[1] like you would have to
# with a regular tuple.
UserAccount = namedtuple('UserAccount', ['username', 'password'])

app = Flask(__name__)
hashing = Hashing(app)

# Replace the example UserAccount objects below with the initial user accounts
# for your own web app. You can add as many as you need to the list.
users = [UserAccount('member1', 'member1pass'), 
         UserAccount('member2', 'member2pass'),
         UserAccount('member3', 'member3pass'),
         UserAccount('member4', 'member4pass'),
         UserAccount('member5', 'member5pass'), 
         UserAccount('member6', 'member6pass'),
         UserAccount('member7', 'member7pass'),
         UserAccount('member8', 'member8pass'),
         UserAccount('member9', 'member9pass'), 
         UserAccount('member10', 'member10pass'),
         UserAccount('member11', 'member11pass'),
         UserAccount('member12', 'member12pass'),
         UserAccount('member13', 'member13pass'), 
         UserAccount('member14', 'member14pass'),
         UserAccount('member15', 'member15pass'),
         UserAccount('member16', 'member16pass'),
         UserAccount('member17', 'member17pass'), 
         UserAccount('member18', 'member18pass'),
         UserAccount('member19', 'member19pass'),
         UserAccount('member20', 'member20pass'),
         UserAccount('moderator1', 'moderator1pass'),
         UserAccount('moderator2', 'moderator2pass'),
         UserAccount('moderator3', 'moderator3pass'),
         UserAccount('moderator4', 'moderator4pass'),
         UserAccount('moderator5', 'moderator5pass'),
         UserAccount('admin1', 'admin1pass'),
         UserAccount('admin2', 'admin2pass'),
         ]

print('Username | Password | Hash | Password Matches Hash')

for user in users:
    # Generate a SHA-256 hash using the default settings for flask_hashing and
    # the salt value we defined earlier. This function returns the hash as a 64
    # character string in hexadecimal.
    password_hash = hashing.hash_value(user.password, PASSWORD_SALT)
    
    # Check whether the hash matches the original password. We don't really
    # need to do this here: this is just to show how your web app would check a
    # password supplied by the user (user.password) against a hash value
    # retrieved from the database (password_hash). Note that your application's
    # salt value is also required when checking a password.
    # 
    # This returns True if the password matches, or False if it doesn't.
    password_matches_hash = hashing.check_value(password_hash, user.password, PASSWORD_SALT)

    # Output username, password, hash, and the result of our verification test.
    # 
    # Note that username is never actually used when generating the hash or
    # checking a password. We only include username here for display purposes,
    # to make it easier for you to copy the right password for each user when
    # creating your database population script.
    print(f'{user.username} | {user.password} | {password_hash} | {password_matches_hash}')