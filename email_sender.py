import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_or_draft_email(subject, body, recipient_email):
    """
    Sends the email using SMTP or prints/simulates sending if DRY_RUN is active.
    Returns: (status, error_message)
    """
    dry_run_env = os.getenv("DRY_RUN", "true").lower()
    is_dry_run = dry_run_env in ("true", "1", "yes")

    sender_name = os.getenv("SENDER_NAME", "Candidate")
    sender_email = os.getenv("SMTP_USER")

    # If dry run is active, simulate and print to terminal
    if is_dry_run:
        print("\n" + "="*50)
        print(" [DRY RUN ACTIVE] SIMULATED OUTBOX")
        print(f" To: {recipient_email}")
        print(f" From: {sender_name} <{sender_email or 'no-reply@example.com'}>")
        print(f" Subject: {subject}")
        print("-"*50)
        print(body)
        print("="*50 + "\n")
        return "Simulated", ""

    # Real sending mode
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_host, smtp_port, smtp_user, smtp_password]):
        missing = [k for k, v in {
            "SMTP_HOST": smtp_host,
            "SMTP_PORT": smtp_port,
            "SMTP_USER": smtp_user,
            "SMTP_PASSWORD": smtp_password
        }.items() if not v]
        return "Failed", f"Missing SMTP settings in environment: {', '.join(missing)}"

    try:
        port = int(smtp_port)
    except ValueError:
        return "Failed", f"Invalid SMTP_PORT: {smtp_port}"

    # Construct email message
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{smtp_user}>"
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Establish connection (using standard starttls flow)
        server = smtplib.SMTP(smtp_host, port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient_email, msg.as_string())
        server.quit()
        return "Sent", ""
    except Exception as e:
        return "Failed", str(e)
