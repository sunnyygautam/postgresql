import time
import re
import smtplib
from email.mime.text import MIMEText

LOG_FILE = "app.log"
PATTERN = re.compile(r"ERROR")

def send_email(msg):
    email = MIMEText(msg)
    email["Subject"] = "Log Alert"
    email["From"] = "alert@example.com"
    email["To"] = "admin@example.com"

    with smtplib.SMTP("smtp.example.com", 25) as s:
        s.sendmail(email["From"], [email["To"]], email.as_string())

def monitor():
    with open(LOG_FILE) as f:
        f.seek(0, 2)  # Start from end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            if PATTERN.search(line):
                print("Alert:", line.strip())
                send_email(line.strip())

if __name__ == "__main__":
    print("Monitoring log for:", PATTERN.pattern)
    monitor()
