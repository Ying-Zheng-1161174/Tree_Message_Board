from flask import Flask

app = Flask(__name__)

# Session secret
app.secret_key = 'thisismysessionkeyitshouldbemuchmorecomplicatedbutitisokfornow'

from TreeOfPeace import user
