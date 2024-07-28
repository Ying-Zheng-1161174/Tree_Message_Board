from flask import Flask
from flask_hashing import Hashing
from TreeOfPeace.config import Config

app = Flask(__name__)

# Load configuration from Config class
app.config.from_object(Config)

# Create an instance of hashing
hashing = Hashing(app)

# Import views 
from TreeOfPeace.views import main, user, admin, auth
from TreeOfPeace.utils.filters import format_date

# Register data formatting filter
app.jinja_env.filters['format_date'] = format_date