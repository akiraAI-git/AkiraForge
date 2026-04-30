import os
import logging
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    _SENDGRID_AVAILABLE = True
except Exception:
    _SENDGRID_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [EMAIL] %(levelname)s: %(message)s"
)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = "akiraforge@outlook.com"

_SG_CLIENT = None
if _SENDGRID_AVAILABLE and SENDGRID_API_KEY:
    try:
        _SG_CLIENT = SendGridAPIClient(SENDGRID_API_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize SendGrid client: {e}")
        _SG_CLIENT = None
else:
    if not _SENDGRID_AVAILABLE:
        logging.warning("sendgrid package not available - email features disabled.")
    else:
        logging.warning("SENDGRID_API_KEY not set; email features will be disabled.")

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    if _SG_CLIENT is None:
        logging.warning(f"Attempted to send email to {to_email} but SendGrid is not configured.")
        return False

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_body
    )

    try:
        response = _SG_CLIENT.send(message)
        logging.info(f"Email sent to {to_email} | Status: {response.status_code}")
        return True
    except Exception as e:
        logging.error(f"Email sending failed: {e}")
        return False

def template(title: str, body: str) -> str:
    """
    Generate HTML email template.
    
    Args:
        title: Email title/heading
        body: Email body content
        
    Returns:
        HTML formatted email string
    """
    return f"""
    <div style='font-family: Arial, sans-serif; background:#f5f5f5; padding:20px;'>
        <div style='max-width:600px; margin:auto; background:white; border-radius:8px; overflow:hidden;'>
            <div style='background:#111827; padding:16px;'>
                <h2 style='color:white; margin:0; font-size:20px;'>Akira Forge</h2>
            </div>
            <div style='padding:20px; color:#333;'>
                <h3 style='margin-top:0; font-size:18px;'>{title}</h3>
                <p style='font-size:15px; line-height:1.6;'>{body}</p>
            </div>
            <div style='background:#f0f0f0; padding:12px; text-align:center; font-size:12px; color:#666;'>
                This message was sent by Akira Forge.
            </div>
        </div>
    </div>
    """