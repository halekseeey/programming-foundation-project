"""
Main Flask application.
"""
from flask import Flask, jsonify
from flask_cors import CORS

from routes.datasets import datasets_bp
from routes.cleaning import cleaning_bp
from routes.analytics import analytics_bp
from routes.data_processing import data_processing_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(datasets_bp)
    app.register_blueprint(cleaning_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(data_processing_bp)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5050, debug=True)
