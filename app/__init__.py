# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate

# Initialize the database object
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///players.db'  # Change URI as needed
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional

    # Initialize the database with the app
    db.init_app(app)

    # Initialize Flask-Migrate with the app and the database
    migrate.init_app(app, db)

    # Register the blueprint
    from app.routes import routes  # Import your blueprint
    app.register_blueprint(routes)  # Register the routes blueprint

    return app
