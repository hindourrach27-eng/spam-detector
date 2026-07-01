
"""
app/__init__.py — Application factory
"""

import os
from flask import Flask, render_template
from flask_session import Session
from config import Config
from database import init_database

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    Session(app)

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    init_database()

    from app.home.routes import home_blueprint
    app.register_blueprint(home_blueprint)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('page-404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('page-500.html'), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('page-400.html'), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('page-403.html'), 403

    return app