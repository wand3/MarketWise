from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    from webapp.api import api_bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from webapp.main import main_bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
