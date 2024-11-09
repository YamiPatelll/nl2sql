import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


db_path = 'moon.db'

SMTP_SERVER = "74.125.200.108" 
SMTP_PORT = 587                 
EMAIL = "" 
PASSWORD = ""        

# Email messages based on status
status_messages = {
    'selected': "Congratulations {name}! You have been selected for the position.",
    'rejected': "Dear {name}, we regret to inform you that you were not selected for the position.",
    'on hold': "Hello {name}, your application is currently on hold. We will update you soon."
}

def send_email(to_email, subject, message):
    """Send email to the specified recipient."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, to_email, msg.as_string())
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")

def notify_candidates():
    """Fetch candidates based on status and send them emails if not yet notified."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch candidates who haven't been notified yet
    cursor.execute("SELECT candidate_id, candidate_name, email, status FROM candidates WHERE notified = 0")
    candidates = cursor.fetchall()

    for candidate_id, name, email, status in candidates:
        # Prepare personalized message
        message = status_messages.get(status, "").format(name=name)
        if message:
            subject = f"Application Status: {status.capitalize()}"
            send_email(email, subject, message)
            # Mark candidate as notified
            cursor.execute("UPDATE candidates SET notified = 1 WHERE candidate_id = ?", (candidate_id,))

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("All notifications sent and database updated.")

# Uncomment these lines to create the database and add a sample record if needed
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        candidate_id INTEGER PRIMARY KEY,
        candidate_name TEXT NOT NULL,
        email TEXT NOT NULL,
        status TEXT NOT NULL,
        notified INTEGER DEFAULT 0
    )
''')
sample_data = [
    ('Yamipatel', 'yamipatel307@gmail.com', 'selected'),
    # ('Jane Smith', 'jane.smith@example.com', 'rejected'),
    # ('Emily Johnson', 'emily.johnson@example.com', 'on hold')
]
cursor.executemany("INSERT INTO candidates (candidate_name, email, status) VALUES (?, ?, ?)", sample_data)
conn.commit()
conn.close()


notify_candidates()
