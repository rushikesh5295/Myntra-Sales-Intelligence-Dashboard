"""Flask application factory for the Myntra Sales Intelligence dashboard."""

from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)

    from app.routes.api import api_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)

    return app
