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
        user_id = request.form.get('emp_id')
        password = request.form.get('password')

        # Debugging: Print values to check what is being entered
        print(f"User ID: {user_id}, Password: {password}")

        user = Employee.query.filter_by(emp_id=user_id).first()

        if user:
            print(f"Found user: {user.name}, Hashed password in DB: {user.password}")

        if user and check_password_hash(user.password, password):
            login_user(user)
            session['emp_id'] = user.emp_id  
            flash("Login successful!", "success")
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
        entered_otp = request.form.get('otp')
        if entered_otp != session.get('otp'):
            flash('Invalid OTP! Please verify again.', 'danger')
            return redirect(url_for('register_employee'))

        emp_name = request.form.get('emp_name')
        emp_id = request.form.get('emp_id')
        email = request.form.get('email')
        phone = request.form.get('phone')
        hashed_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')

        image_folder = 'static/images/users'
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        temp_image_path = session.get('temp_image_path', None)
        final_image_path = os.path.join(image_folder, f"{emp_id}-{emp_name}.jpg")

        # Debugging step - Check if temp image exists before renaming
        if temp_image_path and os.path.isfile(temp_image_path):
            os.rename(temp_image_path, final_image_path)
            pic_path = final_image_path
        else:
            flash("No image captured, using placeholder.", "warning")
            pic_path = 'static/images/no-image.png'

        # Save to database (Assume Employee model exists)
        new_employee = Employee(
            name=emp_name,
            emp_id=emp_id,
            email=email,
            phone=phone,
            password=hashed_password,
            pic_path=pic_path,
            # registered_on=datetime.now()
        )
        print(f"Name: {emp_name}, ID: {emp_id}, Email: {email}, Phone: {phone}, Password: {hashed_password}") 
        try:
            db.session.add(new_employee)
            db.session.commit()
            flash('Employee registered successfully!', 'success')

            session.pop('otp', None)
            if os.path.isfile(temp_image_path):
                os.remove(temp_image_path)

            return redirect(url_for('register_employee'))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('Error saving employee! Try again.', 'danger')
            return redirect(url_for('register_employee'))

    # Generate OTP for verification
    if 'otp' not in session:
        otp = str(random.randint(1000, 9999))
        session['otp'] = otp
        print(f"Generated OTP: {otp}")

    temp_image_path = session.get('temp_image_path', None)
    flash("Employee Registered successfully!", "success")
    return render_template('new_emp_register.html', temp_image_path=temp_image_path)

@app.route('/capture_image')
def capture_image():
    session['img_captured'] = False
    return render_template('capture_face.html')

@app.route('/start_camera')
def start_camera():
    global os 
    session['dt'] = datetime.now()
    path = 'static/images/users'
    if not os.path.exists(path):
        os.makedirs(path)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow('Press C to Capture', frame)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            # Save the captured image
            temp_image_path = os.path.join(path, 'temp.jpg')
            cv2.imwrite(temp_image_path, frame)
            time.sleep(2)
            break

    cap.release()
    cv2.destroyAllWindows()

    # Set session variable to indicate the image was captured
    session['img_captured'] = True  # Mark that the image has been captured
    print("Session value updated:", session['img_captured']) 
    session['temp_image_path'] = temp_image_path  # Store the captured image path
    import os
    print("File exists:", os.path.exists(session.get('temp_image_path')))  # Debugging step

    # Redirect back to the registration page after image capture
    flash("Image Captured!", "success")
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
    
@app.route('/checkin')
def checkin():
    video_capture = cv2.VideoCapture(0)

    known_face_encodings = []
    known_face_names = []
    known_faces_filenames = []

    # Load known faces
    for (dirpath, dirnames, filenames) in os.walk('static/images/users'):
        known_faces_filenames.extend(filenames)
        break

    for filename in known_faces_filenames:
        face = face_recognition.load_image_file('static/images/users/' + filename)
        known_face_names.append(filename[:-4])  # Remove .jpg/.png extension
        known_face_encodings.append(face_recognition.face_encodings(face)[0])

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        ret, frame = video_capture.read()

        if not ret:
            break

        if process_this_frame:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            face_names = []

            flag = False

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                emp_info = "Unknown"  # Default to Unknown

                # Get the face distance and identify the best match
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    emp_info = known_face_names[best_match_index]  # e.g., "E101-Rahul"

                    # Split employee ID and name from the filename (if applicable)
                    if '-' in emp_info:
                        emp_id, emp_name = emp_info.split('-')
                    else:
                        emp_id = emp_name = "Unknown"

                    # Get today's date
                    today = date.today()

                    # Check if the employee already has an attendance record for today
                    exists = Attendance.query.filter_by(emp_id=emp_id, date=today).first()

                    if not exists:
                        # Add attendance record if not already present
                        attendance = Attendance(
                            emp_id=emp_id,
                            name=emp_name,
                            date=today,
                            check_in=datetime.now().time(),
                            status="present"
                        )
                        db.session.add(attendance)
                        db.session.commit()
                        flag = True
                        flash(f"Check-In successful for {emp_name}", "success")
                    else:
                        flash(f"Already Checked-In today: {emp_name}", "warning")
                else:
                    emp_info = "Unknown"  # If no match is found, mark it as Unknown

                face_names.append(emp_info)

        process_this_frame = not process_this_frame

        # Draw face rectangles and display names
        for (top, right, bottom, left), emp_info in zip(face_locations, face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, emp_info, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            if flag:
                cv2.putText(frame, 'Checked-In', (left + 6, bottom - 25), font, 0.5, (0, 255, 0), 1)

        # Show the video stream
        cv2.imshow('Employee Check-In', frame)

        # Quit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

    return redirect(url_for('attendance_page'))

@app.route('/checkout')
def checkout():
    video_capture = cv2.VideoCapture(0)

    known_face_encodings = []
    known_face_names = []
    known_faces_filenames = []

    # Load known faces
    for (dirpath, dirnames, filenames) in os.walk('static/images/users'):
        known_faces_filenames.extend(filenames)
        break

    for filename in known_faces_filenames:
        face = face_recognition.load_image_file('static/images/users/' + filename)
        known_face_names.append(filename[:-4])  # Remove .jpg/.png extension
        known_face_encodings.append(face_recognition.face_encodings(face)[0])

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        ret, frame = video_capture.read()

        if not ret:
            break

        if process_this_frame:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            face_names = []

            flag = False

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                emp_info = "Unknown"  # Default to "Unknown" if no match is found

                # Get the face distance and identify the best match
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    emp_info = known_face_names[best_match_index]  # e.g., "E101-Rahul"

                    # Split employee ID and name from the filename (if applicable)
                    if '-' in emp_info:
                        emp_id, emp_name = emp_info.split('-')
                    else:
                        emp_id = emp_name = "Unknown"

                    # Get today's date
                    today = date.today()

                    # Check if the employee has checked in today
                    attendance_record = Attendance.query.filter_by(emp_id=emp_id, date=today).first()

                    if attendance_record:
                        # Update check-out time if the employee is already checked in
                        attendance_record.check_out = datetime.now().time()
                        db.session.commit()
                        flag = True
                        flash(f"Check-Out successful for {emp_name}", "success")
                    else:
                        flash(f"Please Check-In first!", "warning")
                else:
                    emp_info = "Unknown"  # If no match is found, mark it as Unknown

                face_names.append(emp_info)

        process_this_frame = not process_this_frame

        # Draw face rectangles and display names
        for (top, right, bottom, left), emp_info in zip(face_locations, face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, emp_info, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            if flag:
                cv2.putText(frame, 'Checked-Out', (left + 6, bottom - 25), font, 0.5, (255, 0, 0), 1)

        # Show the video stream
        cv2.imshow('Employee Check-Out', frame)

        # Quit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

    return redirect(url_for('attendance_page'))


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

    flash("Leave request submitted successfully!", "success")  # ✅ Flash message before redirect
    return redirect(url_for('leave_form'))  # ✅ Redirect to leave form
  # <<< Redirect instead of re-render

  
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

# -------------------other----------
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