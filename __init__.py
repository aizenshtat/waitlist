from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

cs_host = 'https://aizenshtat-bug-free-potato-q99qqwx59g7395jx-5000.preview.app.github.dev/'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wait_lists.db'
db = SQLAlchemy(app)

with app.app_context():
    from . import routes

    # Register Blueprints
    app.register_blueprint(routes.main_bp)
    
    # Create Database Models
    db.create_all()

if __name__ == "__main__":
    app.run()