# setup_db.py
from routes import app
from extensions import db
import models

with app.app_context():
    db.create_all()
    print("Database tables created.")
