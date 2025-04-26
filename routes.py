from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import OTPVerification, AdminLeaveApproval
from flask_mail import Message, Mail
from utils.email_utils import generate_otp, send_otp_email
import random
from functools import wraps
from app import app, db
from video_capture import VideoCapture
from models import Employee, Admin, Attendance, LeaveRequest
import sqlite3
from flask import request, session, redirect, url_for
from datetime import datetime, date
import cv2
import face_recognition_models
import face_recognition

import numpy as np
import os
import time

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "employee_login"  # Redirect users to this route if they are not logged in

# User Loader Function
@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id)) or Admin.query.get(int(user_id))

def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'fty_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login!', 'danger')
            return redirect(url_for('admin_login'))
    return wrap

def is_employee_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'std_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login!', 'danger')
            return redirect(url_for('employee_login'))
    return wrap


@app.route('/')
def landing_page():
    return render_template('welcome.html')


@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        user_id = request.form.get('employee_id')
        password = request.form.get('password')

        # Debugging: Print values to check what is being entered
        print(f"User ID: {user_id}, Password: {password}")

        user = Employee.query.filter_by(emp_id=user_id).first()

        if user:
            print(f"Found user: {user.name}, Hashed password in DB: {user.password}")

        if user and check_password_hash(user.password, password):
            login_user(user)
            session['emp_id'] = user.emp_id  
            return redirect(url_for('employee_dashboard'))
        else:
            flash("Invalid credentials", "error")

    return render_template('emp_login.html')

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    if not isinstance(current_user, Employee):
        return redirect(url_for('employee_login'))  # Prevent admins from accessing employee page
    return render_template('employee_home.html', name=current_user.name)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id")
        password = request.form.get("password")
        print("Admin ID:", admin_id)
        print("Password:", password)


        admin = Admin.query.filter_by(admin_id=admin_id).first()
        print("Admin found:", admin)


        if admin and check_password_hash(admin.password, password):
            session["admin_id"] = admin.admin_id  # Store admin session
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))  # Redirect to admin dashboard
        
        flash("Invalid credentials!", "danger")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

@app.route('/admin/dashboard')
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for('admin_login'))  
    admin = Admin.query.filter_by(admin_id=session["admin_id"]).first()
    return render_template('admin_home.html', username=admin.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing_page'))

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')
 
# --------------register-------------
@app.route('/register_employee', methods=['GET', 'POST'])
def register_employee():
    if request.method == 'POST':
        # Safely get the email from the form
        email = request.form.get('email')
        
        # Check if the employee already exists based on email
        data = Employee.query.filter_by(email=email).first()

        if data is None:
            # Create new employee record
            new_employee = Employee(
                name=request.form.get("name"),
                emp_id=request.form.get('employee_id'),
                email=email,
                phone=request.form.get("Phone"),
                password=request.form.get("password"),  # Ensure the password is provided
                pic_path=f'static/images/users/{request.form["employee_id"]}-{request.form["name"]}.jpg',  # Correct file path
                registered_on=datetime.now()
            )
            
            # Add the new employee to the database
            try:
                db.session.add(new_employee)
                db.session.commit()  # Try to commit the new employee to the database
                flash('Employee registration successful', 'success')

                # If temp.jpg exists, rename it
                if os.path.isfile('static/images/users/temp.jpg'):
                    os.rename(
                        'static/images/users/temp.jpg',
                        f'static/images/users/{request.form["employee_id"]}-{request.form["name"]}.jpg'  # Correct path
                    )

                # Remove session data if image was captured
                session.pop('img_captured', None)  # Clear img_captured session variable
                session.pop('dt', None)  # Clear datetime session variable (optional)
                
                # Return to initial form state
                return redirect(url_for('register_employee'))

            except Exception as e:
                # Rollback in case of any error during commit
                db.session.rollback()
                print(f"Error occurred while saving employee: {e}")  # Log the error for debugging
                flash('There was an issue with saving the employee record. Please try again.', 'danger')

        else:
            # If employee with the same email exists
            flash('Employee with this email already exists!', 'danger')

    # Check if temp.jpg exists for displaying preview
    if os.path.isfile('static/images/users/temp.jpg'):
        temp_pic = True
    else:
        temp_pic = False
    
    return render_template('new_emp_register.html', temp_pic=temp_pic)

@app.route("/capture_image")
def capture_image():
    session['dt'] = datetime.now()
    path = 'static/images/users'
    cap = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display the resulting frame
        cv2.imshow('Press c to capture image', frame)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            cv2.imwrite(os.path.join(path, 'temp.jpg'), frame)
            time.sleep(2)
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

    session['img_captured'] = True

    return redirect(url_for('register_employee'))

@app.route('/verify', methods=["POST"])
def verify():
    email = request.form["email"]
    otp = send_otp_email(email)
    if otp:
        session['otp'] = otp
        session['email'] = email
        return "OTP sent"
    else:
        return "Error sending OTP", 500

@app.route('/validate', methods=["POST"])
def validate():
    entered_otp = request.form["otp"]
    if entered_otp == session.get("otp"):
        return f"<span style='color:green;'>✅ OTP Verified for {session.get('email')}</span>"
    else:
        return "<span style='color:red;'>❌ Invalid OTP</span>"
     
# -----------------Attendance-------------
@app.route('/view_attendance', methods=['GET', 'POST'])
def view_attendance():
    if "admin_id" not in session:
        return jsonify({"message": "Unauthorized"}), 403

    selected_date = request.form.get("selected_date")
    if selected_date:
        # Convert selected date to a datetime object
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        # Filter records by the selected date
        attendance_records = Attendance.query.filter_by(date=selected_date).all()
        if not attendance_records:
            no_data = True
        else:
            no_data = False

        return render_template('check_att.html', records=attendance_records, selected_date=selected_date, no_data=no_data)
    else:
        # Show all attendance records by default if no date is selected
        attendance_records = Attendance.query.all()
        return render_template('check_att.html', records=attendance_records, no_data=False)
    
@app.route('/fr_attendance')
def fr_attendance():
    video_capture = VideoCapture(0)

    known_face_encodings = []
    known_face_names = []
    known_faces_filenames = []

    for (dirpath, dirnames, filenames) in os.walk('static/images/users'):
        known_faces_filenames.extend(filenames)
        break

    for filename in known_faces_filenames:
        face = face_recognition.load_image_file('static/images/users/' + filename)
        known_face_names.append(filename[:-4])  # Remove extension
        known_face_encodings.append(face_recognition.face_encodings(face)[0])

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        frame = video_capture.read()

        if process_this_frame:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            face_names = []

            flag = False
            marked_ids = set()
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                emp_info = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    emp_info = known_face_names[best_match_index]  # E.g., "E101-Rahul"
                    emp_id, emp_name = emp_info.split('-')

                    if '-' in emp_info:
                        emp_id, emp_name = emp_info.split('-')  # Split into emp_id and emp_name
                    else:
                        # Handle the case where the format is not as expected (e.g., "Unknown")
                        emp_id = emp_name = "Unknown"  # Or take other appropriate action (skip, log error, etc.)

                    today = datetime.today().date()
                    exists = Attendance.query.filter_by(emp_id=emp_id, name=emp_name,  check_in=datetime.today().date()).first()

                    if not exists:
                        attendance = Attendance(
                            emp_id=emp_id,
                            name=emp_name,
                            status="present",
                            date=datetime.today().date(),
                            check_in=datetime.now().time()
                        )
                        db.session.add(attendance)
                        db.session.commit()
                        flag = True
                        flash(f"Attendance marked successfully for {emp_name}", "success")
                    else:
                        flash(f"Attendance already marked for {emp_name} today.", "warning")
                face_names.append(emp_info)

        process_this_frame = not process_this_frame

        for (top, right, bottom, left), emp_info in zip(face_locations, face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, emp_info, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
            if flag:
                cv2.putText(frame, 'Marked', (left + 12, bottom - 12), font, 0.5, (0, 255, 0), 1)

        cv2.imshow('Employee Attendance', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return redirect(url_for('mark_attendance' ))

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    emp_id = request.form['emp_id']
    name = request.form['name']
    today = date.today()

    # Check if attendance already exists
    existing_attendance = Attendance.query.filter_by(emp_id=emp_id, date=today).first()

    if existing_attendance:
        flash("Your attendance is already marked for today.", "warning")
    else:
        check_in_time = datetime.now().time()
        new_attendance = Attendance(
            emp_id=emp_id,
            name=name,
            date=today,
            check_in=check_in_time,
            status='present'
        )
        db.session.add(new_attendance)
        db.session.commit()
        flash("Attendance marked successfully!", "success")

    return redirect(url_for('employee_home')) 

@app.route('/attendance_page')
def attendance_page():
    return render_template('attendance_1.html')  # Make sure to create this template

@app.route('/attendance_success')
def attendance_success():
    return "✅ Attendance marked successfully!"

@app.route('/attendance_failed')
def attendance_failed():
    return "❌ Face not recognized. Please try again."

# ------------leaves----------------
@app.route('/leave_form')
def leave_form():
    # Fetch the latest leave requests for the employee
    emp_id = session.get('emp_id')  # Assuming you have employee logged in and session stores emp_id
    if emp_id:
        all_requests = AdminLeaveApproval.query.filter_by(emp_id=emp_id).order_by(AdminLeaveApproval.leave_date.desc()).all()
    else:
        all_requests = []
    return render_template('send_leave_req.html', requests=all_requests)
 # create this file in templates folder

@app.route('/request_holiday', methods=['POST'])
def request_holiday():
    emp_id = request.form['emp_id']
    name = request.form['name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    reason = request.form['reason']

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    current_date = start_date_obj
    while current_date <= end_date_obj:
        leave = AdminLeaveApproval(
            emp_id=emp_id,
            name=name,
            leave_date=current_date,
            reason=reason
        )
        db.session.add(leave)
        current_date += timedelta(days=1)

    db.session.commit()
    return redirect(url_for('leave_form'))  # <<< Redirect instead of re-render

  
@app.route('/approve_holiday/<int:leave_id>')
def approve_holiday(leave_id):
    leave = AdminLeaveApproval.query.get_or_404(leave_id)
    leave.status = 'Approved'
    leave.action = 'Approved'
    db.session.commit()
    return redirect(url_for('manage_leaves'))

@app.route('/reject_holiday/<int:leave_id>')
def reject_holiday(leave_id):
    leave = AdminLeaveApproval.query.get_or_404(leave_id)
    leave.status = 'Rejected'
    leave.action = 'Rejected'
    db.session.commit()
    return redirect(url_for('manage_leaves'))

@app.route('/view_leave_status')
@login_required
def view_leave_status():
    emp_id = session.get('emp_id')
    leaves = AdminLeaveApproval.query.filter_by(emp_id=emp_id).all()
    return render_template('view_leave_status.html', leaves=leaves)

@app.route('/manage_leaves')
def manage_leaves():
    leaves = AdminLeaveApproval.query.order_by(AdminLeaveApproval.leave_date.desc()).all()
    return render_template('check_req.html', leaves=leaves)

@app.route('/admin/register_admin', methods=['GET','POST'])
@is_admin_logged_in
def register_admin():
    if request.method == 'POST':
        data = Admin.query.filter_by(email=request.form['email']).first()
        if 'isAdmin' in request.form:
            is_admin = True
        else:
            is_admin = False
        # if email does not already exist
        if data is None:
            admin = Admin(
                username = data.get('username'),
                password = generate_password_hash(data.get('password')),
                last_admin = Admin.query.order_by(Admin.id.desc()).first(),
                is_admin=is_admin,
                registered_on=datetime.now()
            )
            db.session.add(admin)
            db.session.commit()

            flash("Admin registered successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Admin with this email already exists!', 'danger')
    return render_template('register_admin.html')


@app.route('/set_password', methods=['POST'])
def set_password():
    email = request.form['email']
    password = generate_password_hash(request.form['password'])

    # Continue with name, phone, image etc. if needed
    employee = Employee(email=email, password=password)
    db.session.add(employee)
    db.session.commit()

    flash("Registration complete!", "success")
    return redirect(url_for('admin_dashboard'))