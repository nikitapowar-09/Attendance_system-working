
import random
import smtplib

# email_otp.py
def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp_email(receiver_email):
    sender_email = "vikaschaurasiya8491@gmail.com"
    sender_password = "zkmpxpevmeurionp"

    otp = generate_otp()
    subject = "Your OTP Verification Code"
    body = f"Your OTP code is: {otp}"
    message = f"From: {sender_email}\nTo: {receiver_email}\nSubject: {subject}\nReply-To: {sender_email}\n\n{body}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
        print("✅ OTP sent to:", receiver_email)
        return otp
    except Exception as e:
        print("❌ Error sending email:", e)
        return None