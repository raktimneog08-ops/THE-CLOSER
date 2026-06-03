import os
import json
from groq import Groq

def generate_fallback_email(contact_data, candidate_profile):
    """
    Generates a deterministic template-based email in case of API failure or missing keys.
    """
    role = contact_data.get("role", "Open Role")
    company = contact_data.get("company", "your company")
    recipient_name = contact_data.get("recipient_name") or "Team"
    personalization_note = contact_data.get("personalization_note", "")
    
    sender_name = candidate_profile.get("sender_name", "Candidate")
    candidate_background = candidate_profile.get("candidate_background", "software development")
    portfolio_url = candidate_profile.get("portfolio_url", "")

    subject = f"Quick note on the {role} role at {company}"

    personalization_sentence = f"I was reading about {personalization_note}." if personalization_note else ""

    body = (
        f"Hi {recipient_name},\n\n"
        f"I noticed {company} is hiring for a {role}. {personalization_sentence}\n\n"
        f"I'm {sender_name}, and I have a background in {candidate_background}. "
        f"The opportunity caught my eye because my experience aligns well with the challenges you are solving.\n\n"
        f"Would you be open to a quick look at my profile or pointing me to the right person to speak with?\n\n"
        f"Best,\n"
        f"{sender_name}\n"
    )
    if portfolio_url:
        body += f"{portfolio_url}\n"

    return subject, body.strip()

def generate_email(contact_data, candidate_profile):
    """
    Generates a personalized cold email using Groq LLM.
    Falls back to a template-based generation if Groq API key is missing or calls fail.
    """
    api_key = os.getenv("GROQ_API_KEY")
    # If API key is not configured or is the default placeholder, fall back.
    if not api_key or "gsk_your_groq_api_key" in api_key:
        print("[-] Groq API key not configured. Using deterministic fallback template.")
        return generate_fallback_email(contact_data, candidate_profile)

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    recipient_name = contact_data.get("recipient_name") or "Hiring Manager / Team"
    recipient_email = contact_data.get("recipient_email")
    company = contact_data.get("company")
    role = contact_data.get("role")
    personalization_note = contact_data.get("personalization_note", "")

    sender_name = candidate_profile.get("sender_name")
    candidate_background = candidate_profile.get("candidate_background")
    portfolio_url = candidate_profile.get("portfolio_url", "")

    prompt = f"""
    You are an expert cold email writer. Write a short, highly personalized cold outreach email to a recruiter or hiring manager.
    
    CRITICAL CONSTRAINTS:
    1. The email body must be under 150 words.
    2. Professional, conversational, and direct tone. No hype, no fluff, no exaggerated claims.
    3. Do NOT make up any credentials, experience, or referrals. Only use the candidate background provided.
    4. Focus on exactly one clear, low-friction call to action (e.g., asking if they can point the candidate in the right direction or review their profile).
    5. The response must be a JSON object with two keys: "subject" and "body".

    CANDIDATE INFORMATION:
    - Name: {sender_name}
    - Background: {candidate_background}
    - Portfolio/Links: {portfolio_url}

    RECIPIENT & ROLE INFORMATION:
    - Recipient Name: {recipient_name}
    - Recipient Email: {recipient_email}
    - Company: {company}
    - Role: {role}
    - Personalization Hook Note: {personalization_note}

    Format your output exactly as a JSON object:
    {{
      "subject": "Subject line here",
      "body": "Email body here"
    }}
    """

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that outputs only valid JSON conforming to the requested schema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        subject = result.get("subject")
        body = result.get("body")
        
        if not subject or not body:
            raise ValueError("Invalid response structure from Groq LLM")
            
        return subject, body.strip()

    except Exception as e:
        print(f"[-] Groq LLM Generation failed (Error: {e}). Falling back to template.")
        return generate_fallback_email(contact_data, candidate_profile)
