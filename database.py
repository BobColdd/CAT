# This file initializes the database separately
from app import app, db

with app.app_context():
    db.create_all()
    print("Database created successfully!")