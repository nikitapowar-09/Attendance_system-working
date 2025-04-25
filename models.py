from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class OTPVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Employee Table
class Employee(UserMixin, db.Model):
    __tablename__ = 'Employee'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)  # Unique Employee ID
    emp_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed Password
    pic_path = db.Column(db.Text)
    registered_on = db.Column(db.DateTime)

# Attendance Table
class Attendance(db.Model):
    __tablename__ = 'Attendance'

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('Employee.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time, nullable=True)
    check_out = db.Column(db.Time, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Absent")  # Present/Absent

    __table_args__ = (db.UniqueConstraint('emp_id', 'date', name='unique_attendance'),)

# Leave Request Table
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('Employee.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    leave_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Accept/Reject

# Admin Table
class Admin(db.Model):
    __tablename__ = 'Admin'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed Password
    email = db.Column(db.String(100), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    registered_on = db.Column(db.DateTime)

# Leave Request Table for Admin Approval
class AdminLeaveApproval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('Employee.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    leave_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Accept/Reject
    action = db.Column(db.String(20), default="Pending")  # Admin action
