from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .scraper_routes import scraper_bp
    app.register_blueprint(scraper_bp)

    return app
