import re

def validate_user_data(email, firstName, lastName, birthDate, location):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return 'Invalid email address'
    elif not re.match(r'[A-Za-z]+', firstName):
        return 'Please enter letters (a-z,A-Z) only'
    elif not re.match(r'[A-Za-z]+', lastName):
        return 'Please enter letters (a-z,A-Z) only'
    elif not firstName or not lastName or not birthDate or not location or not email:
        return 'Please fill out the form completely'
    else:
        return None