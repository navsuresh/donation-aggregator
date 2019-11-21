from modules.events import api_bp as api_events
from modules.follow import api_bp as api_follow
from modules.login import api_bp as api_login
from modules.charity import api_bp as api_charity
from modules.faq import api_bp as api_faq

from modules import globals
from flask_cors import CORS
from flask import Flask
from flask_mail import Mail

globals.app = Flask(__name__)
globals.app.secret_key = "chartiyaggregator"

globals.app.register_blueprint(api_events, url_prefix='')
globals.app.register_blueprint(api_follow, url_prefix='')
globals.app.register_blueprint(api_login, url_prefix='')
globals.app.register_blueprint(api_charity, url_prefix='')
globals.app.register_blueprint(api_faq, url_prefix='')


CORS(globals.app, resources={r"/*": {"origins": "*"}})
globals.app.config['CORS_ENABLED'] = True
globals.app.config['CORS_HEADERS'] = 'Content-Type'
globals.app.config['MAIL_SERVER'] = 'smtp.gmail.com'
globals.app.config['MAIL_PORT'] = 465
globals.app.config['MAIL_USERNAME'] = 'charity.email.se@gmail.com'
globals.app.config['MAIL_PASSWORD'] = 'updatedCharitySE123'
globals.app.config['MAIL_USE_TLS'] = False
globals.app.config['MAIL_USE_SSL'] = True

globals.mail = Mail(globals.app)


if __name__ == "__main__":
    globals.app.run(debug=True)