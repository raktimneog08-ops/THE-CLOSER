# The Closer — Cold Email Writer & Send Bot (Groq LLM Edition)

**The Closer** is a modular Python cold outreach assistant designed to help job seekers generate, review, and send personalized cold emails to recruiters and hiring managers. 

It provides two operation modes:
1. 🖥️ **Command-Line Interface (CLI)**: A lightweight terminal coordinator requiring confirmation keys (`y`/`s`/`q`) for sequential outreach.
2. 🌐 **Premium Web UI**: A modern, interactive **Streamlit Dashboard** featuring a dark obsidian theme, side-by-side queue navigation, and inline email editing before dispatching.

---

## Features
- **Liquid Glassmorphism Web Dashboard**: Refined dark theme UI built on Streamlit with interactive lead lists and a real-time edit workspace.
- **Groq LLM Integration**: Personalizes email subjects and body text using the Llama 3.3 model (`llama-3.3-70b-versatile`).
- **Template Fallback**: Automatically falls back to a structured deterministic template if API calls fail or credentials are omitted.
- **Human-in-the-Loop Safeguard**: Prevents automated spamming by requiring manual review and approval before any email leaves the machine.
- **Dry-Run Security Mode**: Displays outreach simulation templates directly to the outbox box/console, making it safe to test without hitting network limits.
- **Local CSV Audit Logs**: Automatically captures outcomes (`Simulated`, `Sent`, `Skipped`, `Failed`) inside `outreach_log.csv`.

---

## File Structure
- `app.py`: The entry point for the Streamlit web dashboard.
- `main.py`: The entry point for the terminal-based CLI coordinator.
- `email_generator.py`: Module for Groq LLM prompt assembly and fallback templates.
- `email_sender.py`: Secure Python `smtplib` driver (STARTTLS) and simulated outbox engine.
- `logger.py`: Appends transaction outcomes to the CSV spreadsheet.
- `contacts.json`: Local JSON file storing targets (e.g. name, company, role, hook).
- `outreach_log.csv`: Auto-generated outreach history database.
- `.env.example`: Configuration variables template.
- `requirements.txt`: Python package dependencies.

---

## Setup Instructions

### 1. Install Dependencies
Ensure Python 3 is installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Configure Settings
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill out the variables inside `.env`:
* **`DRY_RUN`**: Keep as `true` for testing. Toggle to `false` to send real emails.
* **`SENDER_NAME`**: Your full name.
* **`CANDIDATE_BACKGROUND`**: Concise description of your skills/portfolio details.
* **`PORTFOLIO_URL`**: GitHub or LinkedIn link.
* **`GROQ_API_KEY`**: Your API key from Groq Console.
* **`GROQ_MODEL`**: Model to use (defaults to `llama-3.3-70b-versatile`).
* **`SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD`**: SMTP server credentials (for Gmail, generate a 16-character Google App Password).

### 3. Load Targets
Input your targets in `contacts.json`. A sample list is preloaded.

---

## Usage

### Option A: Launch the Web UI (Recommended)
Launch the Streamlit server:
```bash
python -m streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### Option B: Launch the Terminal CLI
Run the command-line flow:
```bash
python main.py
```
* **`y` / `yes`**: Approve and send/simulate.
* **`s` / `skip`**: Skip active target.
* **`q` / `quit`**: Stop execution.
