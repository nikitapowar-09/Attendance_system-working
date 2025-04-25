# create_admin.py

from app import app, db  # replace with your actual app file name
from app import Admin  # update this import path accordingly
from werkzeug.security import generate_password_hash

def create_initial_admin():
    hashed_password = generate_password_hash("admin123", method="pbkdf2:sha256")
    new_admin = Admin(admin_id="admin001", username="SuperAdmin", password=hashed_password)
    
    with app.app_context():
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Admin created successfully.")

if __name__ == "__main__":
    create_initial_admin()
