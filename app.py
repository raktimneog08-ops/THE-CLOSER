import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Import custom core modules
from email_generator import generate_email
from email_sender import send_or_draft_email
from logger import log_outreach

# Page Configurations
st.set_page_config(
    page_title="The Closer - AI Outreach Operator",
    page_icon="📨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

CONTACTS_FILE = "contacts.json"
LOG_FILE = "outreach_log.csv"

# Ensure session state variables
if "active_index" not in st.session_state:
    st.session_state.active_index = 0
if "drafts" not in st.session_state:
    st.session_state.drafts = {}  # key: email, value: {"subject": subject, "body": body}

# CSS Injection for Liquid Glassmorphism Dark Mode Styling
st.markdown("""
<style>
    /* Main App Background Override */
    .stApp {
        background-color: #050505 !important;
        background-image: 
            radial-gradient(circle at 20% 20%, rgba(46, 91, 255, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 50% 0%, #171f33 0%, transparent 60%) !important;
        background-attachment: fixed !important;
        color: #e5e2e1 !important;
        font-family: 'Geist', -apple-system, sans-serif !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #b8c3ff !important;
        font-family: 'Geist', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Glass Panels for Cards */
    .glass-card {
        background-color: rgba(18, 18, 18, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }

    /* Custom Text inputs & textareas */
    textarea, input {
        background-color: #0a0a0a !important;
        color: #e5e2e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }
    textarea:focus, input:focus {
        border-color: #2e5bff !important;
        box-shadow: 0 0 8px rgba(46, 91, 255, 0.3) !important;
    }

    /* Styled buttons */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: #b8c3ff !important;
        box-shadow: 0 0 10px rgba(184, 195, 255, 0.2) !important;
    }

    /* Special Primary Buttons (e.g. Generate/Send) */
    div.st-emotion-cache-1q8dd3e > button {
        background: linear-gradient(135deg, #2e5bff 0%, #8b5cf6 100%) !important;
        border: none !important;
        color: white !important;
    }
    div.st-emotion-cache-1q8dd3e > button:hover {
        box-shadow: 0 0 15px rgba(46, 91, 255, 0.5) !important;
    }

    /* Active indicator pulsing orb */
    .pulsing-orb {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #2e5bff;
        box-shadow: 0 0 8px #2e5bff;
        animation: pulseOrb 2s infinite ease-in-out;
        margin-right: 8px;
    }

    @keyframes pulseOrb {
        0%, 100% { opacity: 0.6; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.2); }
    }
</style>
""", unsafe_allow_html=True)


def load_contacts():
    """Loads target outreach records from contacts.json."""
    if not os.path.exists(CONTACTS_FILE):
        return []
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def get_logs_df():
    """Loads CSV logs for the audit table."""
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["Timestamp", "Recipient Email", "Company", "Role", "Subject", "Status", "Error Message"])
    try:
        df = pd.read_csv(LOG_FILE)
        return df.iloc[::-1]  # Reverse to show newest logs first
    except Exception:
        return pd.DataFrame()


# Load the data
contacts = load_contacts()
sender_name = os.getenv("SENDER_NAME", "Candidate")
candidate_background = os.getenv("CANDIDATE_BACKGROUND", "")
portfolio_url = os.getenv("PORTFOLIO_URL", "")

candidate_profile = {
    "sender_name": sender_name,
    "candidate_background": candidate_background,
    "portfolio_url": portfolio_url
}

# Sidebar Navigation (Contacts list Queue)
with st.sidebar:
    st.markdown('<h1 style="margin-bottom:0px;">The Closer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px; color:#8e90a2; margin-top:0px; font-family:monospace;">AI Outreach Operator</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<h3 style="font-size:14px; text-transform:uppercase; tracking-widest: 1.5px; color:#8e90a2;">Active Queue</h3>', unsafe_allow_html=True)
    
    if not contacts:
        st.write("No contacts found in contacts.json.")
    else:
        for idx, contact in enumerate(contacts):
            c_name = contact.get("recipient_name") or "Hiring Manager"
            c_comp = contact.get("company", "Unknown")
            c_role = contact.get("role", "Open Role")
            c_email = contact.get("recipient_email", "")
            
            # Formulate title for the queue button
            is_active = (idx == st.session_state.active_index)
            active_badge = "🔵 " if is_active else "  "
            
            if st.button(f"{active_badge}{c_name} — {c_comp}", key=f"sidebar_contact_{idx}"):
                st.session_state.active_index = idx

    st.markdown("---")
    st.markdown("### Profile Settings")
    st.info(f"**Sender**: {sender_name}\n\n**Background**: {candidate_background}\n\n**Portfolio**: {portfolio_url}")
    
    # Dry Run status indicator
    is_dry_run = os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")
    if is_dry_run:
        st.warning("⚠️ **Dry Run Mode: Active** (Emails will be simulated, not sent)")
    else:
        st.error("🚀 **LIVE Mode: Active** (Emails will be sent immediately)")


# Main Workspace Setup
if not contacts:
    st.error("No contacts to process. Please ensure contacts.json exists and contains records.")
else:
    # Ensure active_index is in bounds
    if st.session_state.active_index >= len(contacts):
        st.session_state.active_index = 0

    active_contact = contacts[st.session_state.active_index]
    c_name = active_contact.get("recipient_name") or "Hiring Manager"
    c_email = active_contact.get("recipient_email", "")
    c_comp = active_contact.get("company", "Unknown")
    c_role = active_contact.get("role", "Open Role")
    c_note = active_contact.get("personalization_note", "")

    # Layout for main content
    st.markdown(f'<h2>Active Lead: {c_name} at {c_comp}</h2>', unsafe_allow_html=True)
    
    # Info context card (Level 1 Panel style)
    st.markdown(f"""
    <div class="glass-card">
        <p style="margin: 0px; font-size:14px; color:#8e90a2;">Target Details</p>
        <h4 style="margin: 4px 0px 0px 0px; color:#ffffff;">{c_role} — {c_comp} ({c_email})</h4>
        <p style="margin: 8px 0px 0px 0px; font-size:14px; color:#c4c5d9;"><b>Personalization Hook:</b> {c_note if c_note else "None provided"}</p>
    </div>
    """, unsafe_allow_html=True)

    # Load/Generate Active Contact Draft
    if c_email not in st.session_state.drafts:
        # Auto-generate draft using LLM (saves API call on clicks, gives instant preview)
        with st.spinner("Generating personalized outreach using Groq..."):
            subject, body = generate_email(active_contact, candidate_profile)
            st.session_state.drafts[c_email] = {"subject": subject, "body": body}

    current_draft = st.session_state.drafts[c_email]

    # Editor Canvas
    st.markdown("### Email Workspace")
    
    edit_subject = st.text_input("Subject Line", value=current_draft["subject"])
    edit_body = st.text_area("Email Body", value=current_draft["body"], height=300)
    
    # Update drafts cache immediately on UI text change
    st.session_state.drafts[c_email] = {"subject": edit_subject, "body": edit_body}

    # Action Controls Cluster
    col_skip, col_regen, col_send = st.columns([1, 1, 2])
    
    with col_skip:
        if st.button("Skip Contact", width="stretch"):
            log_outreach(c_email, c_comp, c_role, edit_subject, "Skipped")
            st.success(f"Skipped {c_name}.")
            # Advance index
            st.session_state.active_index = (st.session_state.active_index + 1) % len(contacts)
            st.rerun()

    with col_regen:
        if st.button("✨ Regenerate Draft", width="stretch"):
            # Force regeneration by dropping draft key
            if c_email in st.session_state.drafts:
                del st.session_state.drafts[c_email]
            st.rerun()

    with col_send:
        btn_label = "Send Simulated Email" if is_dry_run else "📨 Send Real Email"
        if st.button(btn_label, width="stretch", type="primary"):
            with st.spinner("Sending outreach..."):
                status, err_msg = send_or_draft_email(edit_subject, edit_body, c_email)
                
                # Write CSV log
                log_outreach(c_email, c_comp, c_role, edit_subject, status, err_msg)
                
                if status == "Failed":
                    st.error(f"Failed to send email: {err_msg}")
                else:
                    st.success(f"Success! Status: '{status}'")
                    # Advance to next contact
                    st.session_state.active_index = (st.session_state.active_index + 1) % len(contacts)
                    st.rerun()

# Transaction History Table at the bottom
st.markdown("---")
st.markdown("### Outreach Transaction Log (`outreach_log.csv`)")
logs_df = get_logs_df()

if not logs_df.empty:
    st.dataframe(
        logs_df,
        width="stretch",
        hide_index=True
    )
else:
    st.info("No transaction records found yet.")
