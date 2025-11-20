"""
Main Flask application.
"""
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from routes.datasets import datasets_bp
from routes.analytics import analytics_bp
from renewables.data_preprocessing import preprocess_all_datasets, format_preprocessing_stats
from config import get_config

cfg = get_config()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    CORS(app)

    # Preprocess datasets at startup
    print("=" * 60)
    print("Starting data preprocessing...")
    print("=" * 60)
    try:
        stats = preprocess_all_datasets()
        print("=" * 60)
        format_preprocessing_stats(stats)
    except Exception as e:
        print("=" * 60)
        print(f"ERROR during data preprocessing: {e}")
        print("=" * 60)
        # Continue anyway - maybe the merged dataset already exists
        import traceback
        traceback.print_exc()

    # Register blueprints
    app.register_blueprint(datasets_bp)
    app.register_blueprint(analytics_bp)

    @app.get("/")
    def index():
        """Main page"""
        return render_template('index.html')

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5050, debug=True)
