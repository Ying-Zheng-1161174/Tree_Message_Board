import os

class Config:
    """Configuration settings for the application."""

    SECRET_KEY = "thisismysessionkeyitshouldbemuchmorecomplicatedbutitisokfornow"
    PASSWORD_SALT = 'thisismypasswordsalt'
    # Default role, status, profile_image for all users
    DEFAULT_ROLE = 'member'
    DEFAULT_STATUS = 'active'
    DEFAULT_IMAGE = 'upload/tree.png'
    # Default folder for saving profile_image
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/upload')