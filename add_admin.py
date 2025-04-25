from app import app, db, Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    hashed_password = generate_password_hash("admin123")  # Securely hash password
    new_admin = Admin(admin_id="admin1", username="admin", password=hashed_password)
    db.session.add(new_admin)
    db.session.commit()
    print("Admin user created successfully!")