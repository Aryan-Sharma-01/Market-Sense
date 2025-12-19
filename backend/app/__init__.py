"""Flask application factory for the market sentiment backend."""
from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from .api.routes import api_bp
from .db import init_db, remove_session
from .services.seed import ensure_seed_data


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env()
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)
    ensure_seed_data()

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        remove_session(exception)

    @app.get("/healthz")
    def healthcheck():
        return {"status": "ok"}

    return app


