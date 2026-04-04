from dotenv import load_dotenv
import json
import os
import random
import smtplib
import string
import urllib.error
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
import stripe

load_dotenv()
st.set_page_config(page_title="RegnbueMatch", page_icon="🌈", layout="centered")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
PAID_EMAILS_FILE = os.path.join(BASE_DIR, "paid_emails.json")
DEFAULT_FROM_EMAIL = "noreply@longform-ai88.com"
DEFAULT_FROM_NAME = os.getenv("RESEND_FROM_NAME", "RegnbueMatch").strip() or "RegnbueMatch"
ADMIN_NOTIFICATION_EMAIL = os.getenv("ADMIN_NOTIFICATION_EMAIL", "").strip()
EARLY_ACCESS_LIMIT = 50

DEMO_PROFILES = [
    {
        "username": "PrideAlex",
        "password": "pass123",
        "email": "alex@regnbuematch.no",
        "phone": "90000001",
        "gender": "Mann",
        "seeking": "Mann",
        "age": 28,
        "bio": "Liker konserter, kaffeprat og spontane helgeturer 🌈",
        "matches": [],
        "is_paid": True,
    },
    {
        "username": "RainbowSara",
        "password": "pass123",
        "email": "sara@regnbuematch.no",
        "phone": "90000002",
        "gender": "Kvinne",
        "seeking": "Kvinne",
        "age": 26,
        "bio": "Trygg, sosial og alltid klar for en god samtale ✨",
        "matches": [],
        "is_paid": True,
    },
    {
        "username": "QueerChris",
        "password": "pass123",
        "email": "chris@regnbuematch.no",
        "phone": "90000003",
        "gender": "Annet",
        "seeking": "Annet",
        "age": 31,
        "bio": "Filmkveld, humor og ærlige relasjoner er min vibe 💜",
        "matches": [],
        "is_paid": False,
    },
    {
        "username": "NovaKim",
        "password": "pass123",
        "email": "nova@regnbuematch.no",
        "phone": "90000004",
        "gender": "Kvinne",
        "seeking": "Mann",
        "age": 29,
        "bio": "Elsker god mat, fjellturer og små romantiske øyeblikk.",
        "matches": [],
        "is_paid": True,
    },
]

DEMO_USERNAMES = {user["username"].strip().lower() for user in DEMO_PROFILES}
DEMO_EMAILS = {(user.get("email") or "").strip().lower() for user in DEMO_PROFILES}

ONLINE_SHOWCASE = [
    {
        "username": "PrideAlex",
        "age": 28,
        "bio": "Klar for nye matcher i kveld.",
        "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=facearea&w=600&q=80&facepad=2",
    },
    {
        "username": "RainbowSara",
        "age": 26,
        "bio": "Svarer raskt og elsker hyggelige meldinger.",
        "img": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=facearea&w=600&q=80&facepad=2",
    },
    {
        "username": "QueerChris",
        "age": 31,
        "bio": "Ser etter ekte kjemi og trygg stemning.",
        "img": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=facearea&w=600&q=80&facepad=2",
    },
]

APP_CSS = """
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(255, 79, 163, 0.18), transparent 30%),
        radial-gradient(circle at top right, rgba(75, 139, 255, 0.18), transparent 28%),
        linear-gradient(135deg, #fff8fc 0%, #f5f7ff 100%);
}
.block-container {
    max-width: 860px;
    padding-top: 0.9rem !important;
    padding-bottom: 4rem !important;
}
.hero-card {
    background: linear-gradient(135deg, #ff4fa3 0%, #a259c6 55%, #4b8bff 100%);
    border-radius: 28px;
    padding: 24px 20px;
    color: #ffffff;
    box-shadow: 0 18px 38px rgba(91, 36, 122, 0.22);
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
}
.hero-card::after {
    content: "";
    position: absolute;
    inset: auto -60px -70px auto;
    width: 180px;
    height: 180px;
    background: rgba(255,255,255,0.12);
    border-radius: 50%;
}
.hero-grid {
    display: grid;
    grid-template-columns: 1.35fr 0.85fr;
    gap: 14px;
    align-items: center;
}
.eyebrow {
    display: inline-block;
    margin-bottom: 8px;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.26);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.hero-card h1, .hero-card p, .hero-card strong, .hero-card span {
    color: #ffffff !important;
    margin: 0;
}
.hero-preview {
    display: grid;
    gap: 10px;
}
.hero-mini-card {
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 18px;
    padding: 12px;
    backdrop-filter: blur(8px);
}
.hero-mini-card strong {
    display: block;
    margin-bottom: 4px;
}
.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}
.pill {
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.28);
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 0.85rem;
    color: #fff;
}
label, h1, h2, h3, h4 {
    color: #1d1230 !important;
}
input::placeholder, textarea::placeholder {
    color: #666 !important;
}
.stTextInput input, .stTextArea textarea, .stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #1d1230 !important;
    border-radius: 12px !important;
}
.stButton > button {
    width: 100%;
    border-radius: 14px !important;
    min-height: 48px;
    font-size: 1rem;
    font-weight: 700;
    border: none !important;
    background: linear-gradient(135deg, #ff4fa3 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 10px 24px rgba(139, 92, 246, 0.22);
}
.stLinkButton > a {
    width: 100%;
    border-radius: 14px !important;
    min-height: 48px;
    font-size: 1rem;
    font-weight: 700;
}
.stImage img {
    border-radius: 18px;
}
[data-testid="stSidebar"] {
    background: rgba(162, 89, 198, 0.08) !important;
    border-right: 1px solid rgba(162, 89, 198, 0.12);
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(162, 89, 198, 0.16);
    border-radius: 16px;
    padding: 10px 12px;
}
.profile-card, .soft-card, .feature-item, .how-step {
    background: rgba(255,255,255,0.9);
    border-radius: 18px;
    padding: 14px;
    border: 1px solid rgba(162,89,198,0.14);
    box-shadow: 0 8px 24px rgba(69, 38, 100, 0.08);
    margin-bottom: 12px;
}
.card-badge {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    background: #f5edff;
    color: #7c3aed;
    font-size: 0.78rem;
    font-weight: 700;
    margin-bottom: 8px;
}
.feature-grid, .how-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin: 10px 0 6px;
}
.feature-item h4, .how-step h4 {
    margin-bottom: 6px;
}
.cta-card {
    background: linear-gradient(135deg, rgba(255,79,163,0.12) 0%, rgba(75,139,255,0.12) 100%);
    border: 1px solid rgba(162,89,198,0.18);
    border-radius: 22px;
    padding: 16px;
    margin-top: 10px;
}
.tiny-note {
    color: #6b5a85;
    font-size: 0.88rem;
}
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 0.6rem !important;
    }
    .hero-card {
        padding: 18px 14px;
        border-radius: 20px;
    }
    .hero-grid, .feature-grid, .how-grid {
        grid-template-columns: 1fr;
    }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.3rem !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.45rem 0.65rem;
        font-size: 0.9rem;
    }
}
</style>
"""


def load_json_file(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return default
    return default


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_paid_emails():
    return load_json_file(PAID_EMAILS_FILE, [])


def save_paid_email(email):
    email = (email or "").strip().lower()
    if not email:
        return
    paid_emails = load_paid_emails()
    if email not in paid_emails:
        paid_emails.append(email)
        save_json_file(PAID_EMAILS_FILE, paid_emails)


def is_email_paid(email):
    email = (email or "").strip().lower()
    return bool(email and email in load_paid_emails())


def normalize_user(user):
    username = user.get("username", "Bruker")
    email = (user.get("email") or f"{username.lower().replace(' ', '')}@example.com").lower()
    free_access_granted = bool(user.get("free_access_granted", False))
    return {
        "username": username,
        "password": user.get("password", "pass123"),
        "email": email,
        "phone": user.get("phone", ""),
        "gender": user.get("gender", "Annet"),
        "seeking": user.get("seeking", "Annet"),
        "age": int(user.get("age", 25)),
        "bio": user.get("bio", "Klar for nye matcher 🌈"),
        "matches": list(dict.fromkeys(user.get("matches", []))),
        "free_access_granted": free_access_granted,
        "is_paid": bool(user.get("is_paid", False) or free_access_granted or is_email_paid(email)),
    }


def is_demo_user(user):
    username = (user.get("username") or "").strip().lower()
    email = (user.get("email") or "").strip().lower()
    return username in DEMO_USERNAMES or email in DEMO_EMAILS


def grant_early_access(users):
    early_access_count = 0
    updated_users = []

    for raw_user in users:
        user = normalize_user(raw_user)
        if is_demo_user(user):
            updated_users.append(user)
            continue

        if user.get("free_access_granted", False):
            early_access_count += 1
        elif not is_email_paid(user["email"]) and early_access_count < EARLY_ACCESS_LIMIT:
            user["free_access_granted"] = True
            user["is_paid"] = True
            early_access_count += 1

        updated_users.append(user)

    return updated_users


def count_early_access_users(users=None):
    users = users if users is not None else st.session_state.get("users", [])
    return sum(
        1
        for user in users
        if normalize_user(user).get("free_access_granted", False) and not is_demo_user(user)
    )


def early_access_spots_left(users=None):
    return max(0, EARLY_ACCESS_LIMIT - count_early_access_users(users))


def get_membership_label(user):
    user = normalize_user(user or {})
    if user.get("free_access_granted", False):
        return "Gratis Early Access"
    return "Aktivt" if user.get("is_paid", False) else "Gratis"


def save_users(users):
    save_json_file(USERS_FILE, [normalize_user(user) for user in users])


def load_users():
    users = [normalize_user(user) for user in load_json_file(USERS_FILE, [])]
    existing_names = {user["username"] for user in users}
    for demo_user in DEMO_PROFILES:
        if demo_user["username"] not in existing_names:
            users.append(normalize_user(demo_user))
    users = grant_early_access(users)
    save_users(users)
    return users


def get_user_by_username(username):
    username = (username or "").strip().lower()
    for user in st.session_state.users:
        if user["username"].lower() == username:
            return normalize_user(user)
    return None


def update_user_record(updated_user):
    updated_user = normalize_user(updated_user)
    refreshed_users = []
    found = False
    for user in st.session_state.users:
        if user["username"] == updated_user["username"]:
            refreshed_users.append(updated_user)
            found = True
        else:
            refreshed_users.append(normalize_user(user))
    if not found:
        refreshed_users.append(updated_user)
    st.session_state.users = refreshed_users
    save_users(refreshed_users)
    st.session_state.user = updated_user
    st.session_state.is_paid = updated_user.get("is_paid", False)


def init_session_state():
    defaults = {
        "users": load_users(),
        "mode": "main",
        "logged_in": False,
        "user": None,
        "is_paid": False,
        "verification_code": None,
        "verification_email": None,
        "email_verified": False,
        "pending_verification": None,
        "verification_attempts": 0,
        "email_delivery_message": None,
        "email_delivery_fallback": False,
        "registration_success": False,
        "post_registration_messages": [],
        "private_chats": {},
        "group_chat": [
            {"sender": "System", "message": "Velkommen til felleschatten i RegnbueMatch 🌈"}
        ],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            if isinstance(value, (list, dict)):
                st.session_state[key] = value.copy()
            else:
                st.session_state[key] = value

    st.session_state.users = [normalize_user(user) for user in st.session_state.users]
    if st.session_state.user:
        refreshed_user = get_user_by_username(st.session_state.user.get("username"))
        if refreshed_user:
            st.session_state.user = refreshed_user
            st.session_state.is_paid = refreshed_user.get("is_paid", False)


def reset_verification_state():
    st.session_state.verification_code = None
    st.session_state.verification_email = None
    st.session_state.email_verified = False
    st.session_state.pending_verification = None
    st.session_state.verification_attempts = 0
    st.session_state.email_delivery_message = None
    st.session_state.email_delivery_fallback = False


def create_verification_code():
    return "".join(random.choices(string.digits, k=6))


def send_email_via_resend(
    to_email,
    subject,
    text_body,
    html_body=None,
    from_email=None,
    from_name=None,
):
    resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
    sender_email = (from_email or DEFAULT_FROM_EMAIL).strip()
    sender_name = (from_name or DEFAULT_FROM_NAME).strip() or "RegnbueMatch"

    if not resend_api_key or not sender_email:
        return False, "Resend mangler `RESEND_API_KEY` eller avsenderadresse."

    payload = {
        "from": f"{sender_name} <{sender_email}>",
        "to": [to_email],
        "subject": subject,
        "text": text_body,
        "html": html_body
        or (
            "<div style='font-family:Arial,sans-serif;padding:20px;'>"
            f"<p>{text_body}</p>"
            "</div>"
        ),
    }
    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "RegnbueMatch/1.0 (+https://regnbuematch.no)",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status_code = getattr(response, "status", None) or response.getcode()
            response_text = response.read().decode("utf-8", "ignore")
            if 200 <= status_code < 300:
                return True, response_text
            return False, f"Resend svarte med status {status_code}: {response_text[:200]}"
    except urllib.error.HTTPError as error:
        error_text = error.read().decode("utf-8", "ignore")
        if "1010" in error_text:
            return (
                False,
                "Resend/Cloudflare blokkerte forespørselen (1010). "
                "Sjekk at `RESEND_FROM_EMAIL` bruker ditt verifiserte domene, "
                "lag en ny `RESEND_API_KEY` i Resend, oppdater den i Render og redeploy appen.",
            )
        return False, f"Resend-feil {error.code}: {error_text[:200]}"
    except Exception as error:
        return False, f"Resend-feil: {error}"


def send_email_message(
    to_email,
    subject,
    text_body,
    html_body=None,
    success_message=None,
    allow_fallback=False,
    fallback_message=None,
    fallback_code=None,
):
    smtp_server = os.getenv("SMTP_SERVER", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").strip()
    resend_from_email = DEFAULT_FROM_EMAIL
    resend_from_name = os.getenv("RESEND_FROM_NAME", DEFAULT_FROM_NAME).strip() or "RegnbueMatch"

    if not to_email:
        return {"ok": False, "message": "Skriv inn en gyldig e-postadresse først."}

    provider_error = None

    if os.getenv("RESEND_API_KEY", "").strip() and resend_from_email:
        resend_ok, resend_message = send_email_via_resend(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            from_email=resend_from_email,
            from_name=resend_from_name,
        )
        if resend_ok:
            return {"ok": True, "message": success_message or f"E-post sendt til {to_email} 📧"}
        provider_error = resend_message

    if smtp_server and smtp_user and smtp_pass:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{resend_from_name} <{smtp_user}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15) as server:
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
                    server.ehlo()
                    if smtp_port in (587, 2525):
                        server.starttls()
                        server.ehlo()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            return {"ok": True, "message": success_message or f"E-post sendt til {to_email} 📧"}
        except Exception as error:
            provider_error = provider_error or str(error)

    if allow_fallback:
        reason = provider_error or "E-post er ikke satt opp på serveren ennå."
        return {
            "ok": True,
            "message": f"{reason} {fallback_message or 'Midlertidig fallback er aktiv.'}",
            "fallback_code": fallback_code,
        }

    return {"ok": False, "message": provider_error or "E-postsending er ikke konfigurert ennå."}


def send_verification_email(to_email, code):
    return send_email_message(
        to_email=to_email,
        subject="Din kode",
        text_body=(
            "Hei!\n\n"
            f"Din kode er: {code}\n\n"
            "Skriv inn koden i appen for å fullføre registreringen."
        ),
        html_body=(
            "<div style='font-family:Arial,sans-serif;padding:20px;'>"
            "<h2>RegnbueMatch</h2>"
            "<p>Din kode er:</p>"
            f"<div style='font-size:32px;font-weight:700;letter-spacing:4px;margin:12px 0;'>{code}</div>"
            "<p>Skriv inn koden i appen for å fullføre registreringen.</p>"
            "</div>"
        ),
        success_message=f"Kode sendt til {to_email} 📧",
        allow_fallback=True,
        fallback_message="Koden vises midlertidig direkte i appen så brukeren kan fortsette.",
        fallback_code=code,
    )


def send_welcome_email(user):
    username = user.get("username", "venn")
    to_email = (user.get("email") or "").strip().lower()
    return send_email_message(
        to_email=to_email,
        subject="Velkommen til RegnbueMatch 🌈",
        text_body=(
            f"Hei {username}!\n\n"
            "Profilen din er nå aktiv på RegnbueMatch.\n"
            "Du kan logge inn, se matcher og begynne å chatte med en gang.\n\n"
            "Takk for at du er med 💜"
        ),
        html_body=(
            "<div style='font-family:Arial,sans-serif;padding:20px;'>"
            f"<h2>Hei {username}! 🌈</h2>"
            "<p>Profilen din er nå aktiv på <strong>RegnbueMatch</strong>.</p>"
            "<p>Du kan logge inn, se matcher og begynne å chatte med en gang.</p>"
            "<p>Takk for at du er med 💜</p>"
            "</div>"
        ),
        success_message=f"Velkomstmail sendt til {to_email} 📬",
    )


def notify_admin_new_registration(user):
    if not ADMIN_NOTIFICATION_EMAIL:
        return None

    username = user.get("username", "Ukjent")
    email = user.get("email", "")
    phone = user.get("phone", "")
    return send_email_message(
        to_email=ADMIN_NOTIFICATION_EMAIL,
        subject=f"Ny registrering i RegnbueMatch: {username}",
        text_body=(
            "En ny bruker har registrert seg.\n\n"
            f"Brukernavn: {username}\n"
            f"E-post: {email}\n"
            f"Telefon: {phone}\n"
        ),
        html_body=(
            "<div style='font-family:Arial,sans-serif;padding:20px;'>"
            "<h3>Ny registrering i RegnbueMatch</h3>"
            f"<p><strong>Brukernavn:</strong> {username}</p>"
            f"<p><strong>E-post:</strong> {email}</p>"
            f"<p><strong>Telefon:</strong> {phone}</p>"
            "</div>"
        ),
        success_message="Adminvarsel sendt.",
    )


def is_current_email_verified(current_email):
    current_email = (current_email or "").strip().lower()
    verified_email = (st.session_state.verification_email or "").strip().lower()
    return bool(current_email and st.session_state.email_verified and current_email == verified_email)


def register_user(username, password, gender, age, bio, seeking, email, phone):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    phone = (phone or "").strip()

    if not username or not password or not email or not phone:
        return False, "Fyll ut brukernavn, passord, e-post og telefonnummer."

    if not is_current_email_verified(email):
        return False, "Du må verifisere e-postadressen før registrering."

    if any(user["username"].lower() == username.lower() for user in st.session_state.users):
        return False, "Brukernavnet er allerede i bruk."

    if any(user["email"].lower() == email for user in st.session_state.users):
        return False, "E-postadressen er allerede registrert."

    paid_via_email = is_email_paid(email)
    session_has_paid_access = bool(st.session_state.is_paid and (st.session_state.verification_email or "").strip().lower() == email)
    grant_free_access = early_access_spots_left(st.session_state.users) > 0 and not (paid_via_email or session_has_paid_access)

    new_user = normalize_user({
        "username": username,
        "password": password,
        "email": email,
        "phone": phone,
        "gender": gender,
        "age": age,
        "bio": bio or "Ny på RegnbueMatch 🌈",
        "seeking": seeking,
        "matches": [],
        "free_access_granted": grant_free_access,
        "is_paid": paid_via_email or session_has_paid_access or grant_free_access,
    })
    st.session_state.users.append(new_user)
    save_users(st.session_state.users)
    return True, new_user


def authenticate_user(identifier, password):
    identifier = (identifier or "").strip().lower()
    password = password or ""
    for user in st.session_state.users:
        normalized_user = normalize_user(user)
        if (
            normalized_user["password"] == password
            and identifier in {normalized_user["username"].strip().lower(), normalized_user["email"].strip().lower()}
        ):
            return normalized_user
    return None


def find_matches(current_user):
    current_user = normalize_user(current_user)
    matches = []
    for user in st.session_state.users:
        user = normalize_user(user)
        if user["username"] == current_user["username"]:
            continue
        preference_ok = current_user["seeking"] == "Swingers" or user["gender"] in {current_user["seeking"], "Annet"}
        reverse_ok = user["seeking"] == "Swingers" or current_user["gender"] in {user["seeking"], "Annet"}
        age_ok = abs(user["age"] - current_user["age"]) <= 12
        if (preference_ok or reverse_ok) and age_ok:
            matches.append(user)
    return matches[:8] or [user for user in st.session_state.users if user["username"] != current_user["username"]][:5]


def add_match(current_username, other_username):
    updated_users = []
    for user in st.session_state.users:
        user = normalize_user(user)
        if user["username"] == current_username and other_username not in user["matches"]:
            user["matches"].append(other_username)
        if user["username"] == other_username and current_username not in user["matches"]:
            user["matches"].append(current_username)
        updated_users.append(user)
    st.session_state.users = updated_users
    save_users(updated_users)
    if st.session_state.user and st.session_state.user["username"] == current_username:
        st.session_state.user = get_user_by_username(current_username)


def chat_key(user_a, user_b):
    return "::".join(sorted([user_a, user_b]))


def get_chat(user_a, user_b):
    return st.session_state.private_chats.get(chat_key(user_a, user_b), [])


def send_message(user_a, user_b, message):
    if not message.strip():
        return
    key = chat_key(user_a, user_b)
    history = st.session_state.private_chats.get(key, [])
    history.append({"sender": user_a, "message": message.strip()})
    st.session_state.private_chats[key] = history


def get_group_chat():
    return st.session_state.group_chat


def send_group_message(sender, message):
    if not message.strip():
        return
    st.session_state.group_chat.append({"sender": sender, "message": message.strip()})


def ai_assistant_response(question):
    prompt = (question or "").strip().lower()
    if not prompt:
        return "Skriv et spørsmål først, så får du et kort og nyttig svar."
    if any(word in prompt for word in ["sikker", "trygg", "rød flagg"]):
        return "Møt alltid på et offentlig sted, del planene dine med en venn, og stol på magefølelsen din."
    if any(word in prompt for word in ["første date", "date", "tips"]):
        return "Hold første date enkel: kaffe, gåtur eller noe lavterskel. Vær nysgjerrig og still åpne spørsmål."
    if any(word in prompt for word in ["profil", "bio"]):
        return "En god bio er kort, varm og konkret: hva du liker, hvem du ser etter og litt humor."
    return "Vær deg selv, vær tydelig på hva du ønsker, og bygg trygghet steg for steg 💜"


def handle_payment_status():
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_price_id = os.getenv("STRIPE_PRICE_ID", "")
    app_base_url = os.getenv("APP_BASE_URL", "").rstrip("/")
    stripe_config_ok = bool(stripe_secret_key and stripe_price_id)

    if stripe_config_ok:
        stripe.api_key = stripe_secret_key

    query_params = st.query_params
    if query_params.get("success") == "true":
        session_id = query_params.get("session_id", "")
        if stripe_config_ok and session_id:
            try:
                checkout_session = stripe.checkout.Session.retrieve(session_id)
                if checkout_session.get("payment_status") == "paid":
                    st.session_state.is_paid = True
                    paid_email = checkout_session.get("customer_email") or (checkout_session.get("customer_details") or {}).get("email")
                    save_paid_email(paid_email)
                    st.success("Betaling bekreftet. Abonnementet er aktivt ✅")
                else:
                    st.warning("Betalingen er ikke bekreftet ennå.")
            except Exception as error:
                st.error(f"Kunne ikke verifisere Stripe-betalingen: {error}")
        query_params.clear()
    elif query_params.get("canceled") == "true":
        st.info("Betalingen ble avbrutt.")
        query_params.clear()

    return stripe_config_ok, stripe_price_id, app_base_url


def render_sidebar():
    st.sidebar.title("Meny")
    if st.session_state.logged_in and st.session_state.user:
        st.sidebar.success(f"Innlogget som {st.session_state.user['username']}")
        medlemskap = get_membership_label(st.session_state.user)
        st.sidebar.caption(f"Medlemskap: {medlemskap}")
        if st.sidebar.button("🏠 Forside", key="sidebar_home_logged"):
            st.session_state.mode = "main"
            st.rerun()
        if not st.session_state.user.get("is_paid", False):
            spots_left = early_access_spots_left()
            if spots_left > 0:
                st.sidebar.info(f"🎁 {spots_left} gratisplasser igjen for verifiserte profiler.")
            else:
                st.sidebar.info("💎 Full tilgang aktiveres via abonnement.")
        if st.sidebar.button("🚪 Logg ut", key="sidebar_logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.is_paid = False
            st.session_state.mode = "main"
            st.rerun()
    else:
        if st.sidebar.button("🏠 Forside", key="sidebar_home_public"):
            st.session_state.mode = "main"
            st.rerun()
        if st.sidebar.button("📝 Registrer", key="sidebar_register"):
            st.session_state.mode = "register"
            st.rerun()
        if st.sidebar.button("🔐 Logg inn", key="sidebar_login"):
            st.session_state.mode = "login"
            st.rerun()


def render_header():
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-grid">
                <div>
                    <span class="eyebrow">TRYGG MATCHING · NORSK PWA</span>
                    <h1>🌈 RegnbueMatch</h1>
                    <p>Dating-appen som føles varm, enkel og ekte — laget for raske matcher, trygge samtaler og fin kjemi på mobil.</p>
                    <div class="pill-row">
                        <span class="pill">Verifisert e-post</span>
                        <span class="pill">Chat & fellesskap</span>
                        <span class="pill">Installerbar app</span>
                    </div>
                </div>
                <div class="hero-preview">
                    <div class="hero-mini-card">
                        <strong>✨ Kveldens vibe</strong>
                        <span>Rolige profiler, raske svar og mindre støy.</span>
                    </div>
                    <div class="hero-mini-card">
                        <strong>💬 Klar for samtale</strong>
                        <span>Finn noen å skrive med på under ett minutt.</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1, 0.9])
    with col1:
        st.link_button("📲 Installer appen", "/app/static/index.html", use_container_width=True)
    with col2:
        st.link_button("🖼️ Se app-preview", "/app/static/index.html", use_container_width=True)
    with col3:
        if st.button("💜 Start nå", key="hero_start_now"):
            st.session_state.mode = "dashboard" if st.session_state.logged_in else "register"
            st.rerun()
    st.caption("På mobil kan du velge ‘Legg til på startskjerm’, og på PC kan du bruke ‘Installer app’ i nettleseren.")


def render_home():
    spots_left = early_access_spots_left()
    stats = st.columns(3)
    stats[0].metric("Profiler", len(st.session_state.users))
    stats[1].metric("Online nå", len(ONLINE_SHOWCASE))
    stats[2].metric("Early access", f"{spots_left} igjen")

    if spots_left > 0:
        st.success(f"🎉 Fase 2-tilbud: De første {EARLY_ACCESS_LIMIT} verifiserte profilene får gratis full tilgang. {spots_left} plasser igjen.")
    else:
        st.info("Early access er fulltegnet. Nye brukere kan fortsatt registrere seg og oppgradere til abonnement.")

    intro_col, preview_col = st.columns([1.15, 0.85], gap="large")
    with intro_col:
        st.markdown(
            """
            <div class="soft-card">
                <span class="card-badge">NY FORSIDE</span>
                <h3>Føles mer som en ekte datingside</h3>
                <p>RegnbueMatch er laget for rolige førsteinntrykk, verifiserte profiler og en enklere start på samtalen — uten rot og med fokus på mobil.</p>
                <div class="feature-grid">
                    <div class="feature-item">
                        <h4>💌 Trygg start</h4>
                        <p>E-postkode gir en renere og mer seriøs onboarding.</p>
                    </div>
                    <div class="feature-item">
                        <h4>⚡ Rask matching</h4>
                        <p>Se profiler, vis interesse og kom raskt i gang med chat.</p>
                    </div>
                    <div class="feature-item">
                        <h4>📲 App-følelse</h4>
                        <p>Installer på startskjermen og bruk den som en ekte app.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with preview_col:
        splashscreen_path = os.path.join(STATIC_DIR, "icons", "splashscreen.png")
        if os.path.exists(splashscreen_path):
            st.image(splashscreen_path, use_container_width=True)

    st.markdown(
        """
        <div class="soft-card">
            <span class="card-badge">SLIK FUNGERER DET</span>
            <div class="how-grid">
                <div class="how-step">
                    <h4>1. Lag profil</h4>
                    <p>Velg hvem du er, hva du søker, og skriv en kort bio.</p>
                </div>
                <div class="how-step">
                    <h4>2. Finn kjemi</h4>
                    <p>Se hvem som er online, og få forslag som passer deg.</p>
                </div>
                <div class="how-step">
                    <h4>3. Start praten</h4>
                    <p>Chat privat eller bli med i fellesskapet når du er klar.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.logged_in:
        cta1, cta2 = st.columns(2)
        with cta1:
            if st.button("💜 Opprett gratis profil", key="home_register_cta"):
                st.session_state.mode = "register"
                st.rerun()
        with cta2:
            if st.button("🔐 Jeg har allerede konto", key="home_login_cta"):
                st.session_state.mode = "login"
                st.rerun()

    st.subheader("🟢 Online nå")
    profile_cols = st.columns(len(ONLINE_SHOWCASE))
    for index, person in enumerate(ONLINE_SHOWCASE):
        with profile_cols[index]:
            st.image(person["img"], use_container_width=True)
            st.markdown(
                f"""
                <div class="profile-card">
                    <span class="card-badge">Online nå</span>
                    <h4>{person['username']}, {person['age']}</h4>
                    <p>{person['bio']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"💫 Vis interesse", key=f"showcase_{person['username']}"):
                if st.session_state.logged_in:
                    st.success(f"Hyggelig! {person['username']} er lagt til i dine forslag.")
                else:
                    st.info("Logg inn eller registrer deg for å begynne å chatte.")

    st.markdown(
        """
        <div class="cta-card">
            <h3>💜 Klar for første match?</h3>
            <p>Installer appen, opprett profil og gjør forsiden om til din nye favorittplass for trygge samtaler.</p>
            <p class="tiny-note">Perfekt på mobil, enkel på desktop, og bygget for raske førsteinntrykk.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_register():
    st.subheader("Opprett ny profil")
    stripe_config_ok, stripe_price_id, app_base_url = handle_payment_status()

    reg_username = st.text_input("Brukernavn", key="reg_user")
    reg_password = st.text_input("Passord", type="password", key="reg_pass")
    reg_email = st.text_input("E-postadresse", key="reg_email")
    reg_phone = st.text_input("Telefonnummer", key="reg_phone")
    reg_gender = st.selectbox("Kjønn", ["Mann", "Kvinne", "Annet"], key="reg_gender")
    reg_seeking = st.selectbox("Hva søker du etter?", ["Mann", "Kvinne", "Annet", "Swingers"], key="reg_seeking")
    reg_age = st.number_input("Alder", min_value=18, max_value=99, value=25, key="reg_age")
    reg_bio = st.text_area("Om deg selv", key="reg_bio", placeholder="Fortell litt om deg selv, interesser og hva du ser etter.")

    spots_left = early_access_spots_left()
    current_email_has_paid_access = bool(reg_email and is_email_paid(reg_email))
    st.session_state.is_paid = current_email_has_paid_access

    with st.container(border=True):
        st.markdown("#### 🎁 Tilgang")
        if current_email_has_paid_access:
            st.success("Denne e-posten har allerede aktivt abonnement og full tilgang.")
        elif spots_left > 0:
            st.success(
                f"De første {EARLY_ACCESS_LIMIT} verifiserte profilene får gratis full tilgang. "
                f"Det er {spots_left} plasser igjen akkurat nå."
            )
            st.caption("Opprett profilen og bekreft e-posten din for å låse opp early access automatisk.")
        else:
            st.warning("Gratisplassene er brukt opp. Du kan fortsatt registrere deg gratis, men abonnement trengs for full chat-tilgang.")
            if not stripe_config_ok:
                st.info("Sett `STRIPE_SECRET_KEY` og `STRIPE_PRICE_ID` på Render for å aktivere kjøp.")
            if not app_base_url:
                st.info("Sett `APP_BASE_URL` til din Render-URL for korrekt tilbakekobling fra Stripe.")
            if st.button("Kjøp abonnement (kr 199)", key="buy_subscription", disabled=not (stripe_config_ok and bool(app_base_url))):
                try:
                    session_payload = {
                        "payment_method_types": ["card"],
                        "line_items": [{"price": stripe_price_id, "quantity": 1}],
                        "mode": "subscription",
                        "success_url": f"{app_base_url}/?success=true&session_id={{CHECKOUT_SESSION_ID}}",
                        "cancel_url": f"{app_base_url}/?canceled=true",
                    }
                    if reg_email:
                        session_payload["customer_email"] = reg_email
                    session = stripe.checkout.Session.create(**session_payload)
                    st.link_button("Åpne Stripe-betalingen", session.url, use_container_width=True)
                except Exception as error:
                    st.error(f"Stripe-feil: {error}")

    st.markdown("#### ✉️ E-postverifisering")
    if st.button("Send kode", key="send_code_main_btn"):
        code = create_verification_code()
        st.session_state.verification_code = code
        st.session_state.verification_email = reg_email
        st.session_state.pending_verification = reg_username or reg_email
        st.session_state.email_verified = False
        st.session_state.verification_attempts = 0
        result = send_verification_email(reg_email, code)
        st.session_state.email_delivery_message = result["message"]
        st.session_state.email_delivery_fallback = bool(result.get("fallback_code"))
        if result["ok"]:
            if result.get("fallback_code"):
                st.warning(result["message"])
                st.code(result["fallback_code"])
            else:
                st.success(result["message"])
        else:
            st.error(result["message"])

    current_verification_email = (st.session_state.verification_email or "").strip().lower()
    current_reg_email = (reg_email or "").strip().lower()

    if st.session_state.email_delivery_message and not st.session_state.email_verified:
        if st.session_state.email_delivery_fallback and st.session_state.verification_code:
            st.warning(st.session_state.email_delivery_message)
            st.code(st.session_state.verification_code)
            st.caption("Midlertidig fallback er aktiv. Sett helst `RESEND_API_KEY` og `RESEND_FROM_EMAIL` i Render. Valgfritt: `ADMIN_NOTIFICATION_EMAIL` for varsler til deg.")
        elif current_verification_email == current_reg_email:
            st.success(st.session_state.email_delivery_message)

    if st.session_state.pending_verification and not st.session_state.email_verified:
        code_input = st.text_input("Skriv inn koden du har mottatt", key="verify_code")
        if st.button("Bekreft kode", key="confirm_code_main_btn"):
            if code_input == st.session_state.verification_code:
                st.session_state.email_verified = True
                st.session_state.verification_code = None
                st.session_state.pending_verification = None
                st.session_state.email_delivery_fallback = False
                st.success("E-post verifisert ✅")
            else:
                st.session_state.verification_attempts += 1
                if st.session_state.verification_attempts >= 3:
                    reset_verification_state()
                    st.error("For mange feil forsøk. Be om ny kode.")
                else:
                    st.error("Feil kode. Prøv igjen.")

    email_is_verified = is_current_email_verified(reg_email)
    if st.session_state.email_verified and current_reg_email != current_verification_email:
        st.warning("Du endret e-post etter verifisering. Send en ny kode for den nye adressen før registrering.")
    elif email_is_verified:
        st.success("Denne e-postadressen er bekreftet og klar til registrering.")
    else:
        st.info("Du må verifisere e-postadressen før du kan registrere profilen.")

    if st.button("✅ Registrer profil", key="register_main_btn", disabled=not email_is_verified):
        success, payload = register_user(
            reg_username,
            reg_password,
            reg_gender,
            reg_age,
            reg_bio,
            reg_seeking,
            email=reg_email,
            phone=reg_phone,
        )
        if success:
            delivery_updates = []
            if payload.get("free_access_granted", False):
                delivery_updates.append(("success", f"🎉 Du fikk gratis full tilgang som en av de første {EARLY_ACCESS_LIMIT} verifiserte brukerne."))

            welcome_result = send_welcome_email(payload)
            if welcome_result["ok"]:
                delivery_updates.append(("success", welcome_result["message"]))
            elif welcome_result["message"]:
                delivery_updates.append(("info", f"Profilen er opprettet, men velkomstmail ble ikke sendt: {welcome_result['message']}"))

            admin_result = notify_admin_new_registration(payload)
            if admin_result and not admin_result["ok"]:
                delivery_updates.append(("warning", f"Adminvarsel ble ikke sendt: {admin_result['message']}"))

            st.session_state.post_registration_messages = delivery_updates
            reset_verification_state()
            st.session_state.registration_success = True
            st.session_state.mode = "login"
            st.rerun()
        else:
            st.error(payload)


def render_login():
    st.subheader("Logg inn")
    login_identifier = st.text_input("Brukernavn eller e-post", key="login_user")
    login_password = st.text_input("Passord", type="password", key="login_pass")
    st.caption("Du kan logge inn med enten brukernavn eller e-postadressen du registrerte deg med.")

    if st.button("Logg inn", key="login_submit"):
        user = authenticate_user(login_identifier, login_password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.is_paid = user.get("is_paid", False)
            st.success(f"Velkommen, {user['username']}! 🚀")
            st.rerun()
        else:
            st.error("Feil brukernavn/e-post eller passord.")


def render_matches_tab():
    st.header("Dine matcher")
    matches = find_matches(st.session_state.user)
    if not matches:
        st.info("Ingen matcher funnet ennå.")
        return

    for match in matches:
        with st.container(border=True):
            st.image(f"https://api.dicebear.com/7.x/adventurer/svg?seed={match['username']}", width=80)
            st.markdown(f"**{match['username']}**, {match['age']} år")
            st.caption(match['bio'])
            if st.button(f"💘 Match med {match['username']}", key=f"match_{match['username']}"):
                add_match(st.session_state.user['username'], match['username'])
                st.success(f"Du har matchet med {match['username']}!")
                st.rerun()


def render_online_tab():
    st.header("Online nå 🟢")
    for person in ONLINE_SHOWCASE:
        with st.container(border=True):
            st.image(person["img"], use_container_width=True)
            st.markdown(f"**{person['username']}** · {person['age']} år")
            st.caption(person["bio"])


def render_chat_tab():
    st.header("Chat med matcher")
    my_matches = st.session_state.user.get("matches", [])
    if not my_matches:
        st.info("Du har ingen matcher å chatte med ennå.")
        return

    chat_partner = st.selectbox("Velg match", my_matches, key="chat_partner_select")
    for item in get_chat(st.session_state.user['username'], chat_partner):
        role = "user" if item["sender"] == st.session_state.user['username'] else "assistant"
        with st.chat_message(role):
            st.write(item["message"])

    message = st.text_input("Skriv melding", key="private_message_input")
    if st.button("Send melding", key="send_chat_btn"):
        send_message(st.session_state.user['username'], chat_partner, message)
        st.rerun()


def render_group_chat_tab():
    st.header("Felles Chat (kun for medlemmer)")
    for item in get_group_chat():
        role = "user" if item["sender"] == st.session_state.user['username'] else "assistant"
        with st.chat_message(role):
            st.write(f"**{item['sender']}**: {item['message']}")

    group_message = st.text_input("Skriv melding til felleschatten", key="group_message_input")
    if st.button("Send til felles chat", key="send_group_chat_btn"):
        send_group_message(st.session_state.user['username'], group_message)
        st.rerun()


def render_ai_tab():
    st.header("AI-assistent")
    question = st.text_input("Spør om dating, sikkerhet eller profiltekst", key="ask_ai_input")
    if st.button("Spør AI", key="ask_ai_btn"):
        st.info(ai_assistant_response(question))


def render_dashboard():
    user = st.session_state.user
    st.success(f"Velkommen tilbake, {user['username']}!")

    stats = st.columns(3)
    stats[0].metric("Matcher", len(user.get("matches", [])))
    stats[1].metric("Medlemskap", get_membership_label(user))
    stats[2].metric("Status", "Online")

    tab_labels = ["Matcher", "Online nå", "Chat", "AI-assistent"]
    if user.get("is_paid", False):
        tab_labels.insert(3, "Felles Chat")

    tabs = st.tabs(tab_labels)
    tab_index = 0
    with tabs[tab_index]:
        render_matches_tab()
    tab_index += 1
    with tabs[tab_index]:
        render_online_tab()
    tab_index += 1
    with tabs[tab_index]:
        render_chat_tab()
    if user.get("is_paid", False):
        tab_index += 1
        with tabs[tab_index]:
            render_group_chat_tab()
    with tabs[-1]:
        render_ai_tab()


def main():
    render_sidebar()
    render_header()

    if st.session_state.registration_success:
        st.success("Bruker registrert! Du kan nå logge inn med brukernavn eller e-post.")
        for level, message in st.session_state.post_registration_messages:
            getattr(st, level, st.info)(message)
        st.session_state.post_registration_messages = []
        st.session_state.registration_success = False

    if st.session_state.logged_in and st.session_state.user:
        render_dashboard()
        return

    if st.session_state.mode == "register":
        render_register()
    elif st.session_state.mode == "login":
        render_login()
    else:
        render_home()


init_session_state()
main()
