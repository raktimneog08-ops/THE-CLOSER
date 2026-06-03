import os
import sys
import json
from dotenv import load_dotenv

# Import our custom modules
from email_generator import generate_email
from email_sender import send_or_draft_email
from logger import log_outreach

CONTACTS_FILE = "contacts.json"

def load_contacts():
    """
    Loads target outreach records from contacts.json.
    """
    if not os.path.exists(CONTACTS_FILE):
        print(f"[-] Input file '{CONTACTS_FILE}' not found. Please create it first.")
        return []
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            contacts = json.load(f)
            if not isinstance(contacts, list):
                print(f"[-] Error: '{CONTACTS_FILE}' must contain a JSON array of objects.")
                return []
            return contacts
    except json.JSONDecodeError as e:
        print(f"[-] Error parsing JSON in '{CONTACTS_FILE}': {e}")
        return []
    except Exception as e:
        print(f"[-] Error loading contacts: {e}")
        return []

def main():
    # Load environment variables
    load_dotenv()

    # Retrieve candidate profile configuration
    sender_name = os.getenv("SENDER_NAME")
    candidate_background = os.getenv("CANDIDATE_BACKGROUND")
    portfolio_url = os.getenv("PORTFOLIO_URL", "")

    if not sender_name or not candidate_background:
        print("[-] Error: SENDER_NAME and CANDIDATE_BACKGROUND must be set in your .env file.")
        sys.exit(1)

    candidate_profile = {
        "sender_name": sender_name,
        "candidate_background": candidate_background,
        "portfolio_url": portfolio_url
    }

    # Load targets
    contacts = load_contacts()
    if not contacts:
        print("[-] No contacts to process. Exiting.")
        sys.exit(0)

    print("="*60)
    print(" THE CLOSER: COLD OUTREACH OPERATOR")
    print(f" Loaded {len(contacts)} target contact(s).")
    print(f" Mode: {'DRY RUN (Simulated)' if os.getenv('DRY_RUN', 'true').lower() in ('true', '1', 'yes') else 'LIVE EMAIL SENDING'}")
    print("="*60)

    for idx, contact in enumerate(contacts, 1):
        recipient_name = contact.get("recipient_name") or "Hiring Manager"
        recipient_email = contact.get("recipient_email")
        company = contact.get("company", "Unknown")
        role = contact.get("role", "Open Role")

        if not recipient_email:
            print(f"\n[-] Skipping target #{idx}: Missing recipient_email.")
            continue

        print(f"\n[{idx}/{len(contacts)}] Processing: {recipient_name} at {company} ({role})")
        print("Generating personalized email using Groq LLM...")
        
        # Step 2: Generate subject & body
        subject, body = generate_email(contact, candidate_profile)

        # Step 3: Human Review Console (CLI) Preview
        print("\n" + "~"*60)
        print(" EMAIL PREVIEW")
        print("~"*60)
        print(f"To:      {recipient_email}")
        print(f"Subject: {subject}")
        print("-"*60)
        print(body)
        print("~"*60)

        # Prompt user for confirmation
        while True:
            choice = input("\nAction: [y]es (send/draft) / [s]kip / [q]uit: ").strip().lower()
            if choice in ("y", "yes"):
                print("Sending...")
                status, err_msg = send_or_draft_email(subject, body, recipient_email)
                
                if status == "Failed":
                    print(f"[-] Delivery failed: {err_msg}")
                else:
                    print(f"[+] Success: Status is '{status}'")
                
                # Log transaction
                log_outreach(recipient_email, company, role, subject, status, err_msg)
                break

            elif choice in ("s", "skip", "n", "no"):
                print("[*] Skipping this contact.")
                log_outreach(recipient_email, company, role, subject, "Skipped")
                break

            elif choice in ("q", "quit", "exit"):
                print("[*] Exiting program.")
                sys.exit(0)
            else:
                print("Invalid input. Please choose 'y', 's', or 'q'.")

    print("\n[+] Done processing all contacts. Check 'outreach_log.csv' for audit logs.")

if __name__ == "__main__":
    main()
