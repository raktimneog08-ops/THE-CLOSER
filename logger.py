import csv
import os
from datetime import datetime

LOG_FILE = "outreach_log.csv"

def log_outreach(recipient_email, company, role, subject, status, error_message=""):
    """
    Logs an outreach event to the local CSV file outreach_log.csv.
    """
    file_exists = os.path.exists(LOG_FILE)
    
    headers = [
        "Timestamp", 
        "Recipient Email", 
        "Company", 
        "Role", 
        "Subject", 
        "Status", 
        "Error Message"
    ]
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    row = {
        "Timestamp": timestamp,
        "Recipient Email": recipient_email,
        "Company": company,
        "Role": role,
        "Subject": subject,
        "Status": status,
        "Error Message": error_message
    }
    
    try:
        # Open in append mode with newline='' to prevent blank lines on Windows
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        return True
    except Exception as e:
        print(f"[-] Failed to write log to {LOG_FILE}: {e}")
        return False
