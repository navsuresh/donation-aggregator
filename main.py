from events import api_bp as api_events
from follow import api_bp as api_follow

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(api_events, url_prefix='')
app.register_blueprint(api_follow, url_prefix='')


CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_ENABLED'] = True
app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(debug=True)