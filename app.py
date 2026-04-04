from dotenv import load_dotenv
import base64
import json
import os
import random
import secrets
import smtplib
import sqlite3
import string
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
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
PRIVATE_CHATS_FILE = os.path.join(BASE_DIR, "private_chats.json")
GROUP_CHAT_FILE = os.path.join(BASE_DIR, "group_chat.json")
NOTIFICATIONS_FILE = os.path.join(BASE_DIR, "notifications.json")
AUTH_SESSIONS_FILE = os.path.join(BASE_DIR, "auth_sessions.json")
DATA_DB_FILE = os.path.join(BASE_DIR, "regnbuematch.db")
DEFAULT_FROM_EMAIL = "noreply@longform-ai88.com"
DEFAULT_FROM_NAME = os.getenv("RESEND_FROM_NAME", "RegnbueMatch").strip() or "RegnbueMatch"
ADMIN_NOTIFICATION_EMAIL = os.getenv("ADMIN_NOTIFICATION_EMAIL", "").strip()
EARLY_ACCESS_LIMIT = 50
DEFAULT_GROUP_CHAT = [
    {"sender": "System", "message": "Velkommen til felleschatten i RegnbueMatch 🌈"}
]

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
.priority-banner {
    border-radius: 20px;
    padding: 16px 18px;
    margin: 10px 0;
    border: 1px solid rgba(162,89,198,0.18);
    box-shadow: 0 10px 24px rgba(69, 38, 100, 0.08);
}
.priority-banner-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1d1230;
    margin-bottom: 4px;
}
.priority-banner-text {
    font-size: 1rem;
    color: #2d1f45;
}
.priority-banner-time {
    margin-top: 6px;
    font-size: 0.82rem;
    color: #6b5a85;
}
.like-banner {
    background: linear-gradient(135deg, rgba(255,79,163,0.16) 0%, rgba(255,255,255,0.96) 100%);
}
.match-banner {
    background: linear-gradient(135deg, rgba(139,92,246,0.16) 0%, rgba(255,255,255,0.96) 100%);
}
.message-banner {
    background: linear-gradient(135deg, rgba(75,139,255,0.16) 0%, rgba(255,255,255,0.96) 100%);
}
.notice-banner {
    background: linear-gradient(135deg, rgba(255,204,0,0.16) 0%, rgba(255,255,255,0.96) 100%);
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


def get_storage_key(path):
    return os.path.splitext(os.path.basename(path))[0]


def ensure_storage_db():
    with sqlite3.connect(DATA_DB_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                storage_key TEXT PRIMARY KEY,
                json_value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def load_json_file(path, default):
    storage_key = get_storage_key(path)
    try:
        ensure_storage_db()
        with sqlite3.connect(DATA_DB_FILE) as connection:
            row = connection.execute(
                "SELECT json_value FROM app_state WHERE storage_key = ?",
                (storage_key,),
            ).fetchone()
        if row and row[0]:
            return json.loads(row[0])
    except (sqlite3.Error, json.JSONDecodeError, TypeError):
        pass

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                legacy_data = json.load(file)
            save_json_file(path, legacy_data)
            return legacy_data
        except (json.JSONDecodeError, OSError):
            return default
    return default


def save_json_file(path, data):
    serialized = json.dumps(data, ensure_ascii=False, indent=2)
    storage_key = get_storage_key(path)

    try:
        ensure_storage_db()
        with sqlite3.connect(DATA_DB_FILE) as connection:
            connection.execute(
                """
                INSERT INTO app_state (storage_key, json_value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(storage_key) DO UPDATE SET
                    json_value = excluded.json_value,
                    updated_at = excluded.updated_at
                """,
                (storage_key, serialized, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
            )
            connection.commit()
    except sqlite3.Error:
        pass

    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(serialized)
    except OSError:
        pass


def load_auth_sessions():
    return load_json_file(AUTH_SESSIONS_FILE, {})


def save_auth_sessions(sessions):
    save_json_file(AUTH_SESSIONS_FILE, sessions)


def create_auth_session(username):
    username = (username or "").strip()
    if not username:
        return ""
    sessions = load_auth_sessions()
    token = secrets.token_urlsafe(24)
    sessions[token] = {
        "username": username,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_auth_sessions(sessions)
    return token


def get_user_by_auth_token(token):
    token = (token or "").strip()
    if not token:
        return None
    sessions = load_auth_sessions()
    session = sessions.get(token, {})
    return get_user_by_username(session.get("username", "")) if session else None


def clear_auth_session(token):
    token = (token or "").strip()
    if not token:
        return
    sessions = load_auth_sessions()
    if token in sessions:
        del sessions[token]
        save_auth_sessions(sessions)


def persist_login_state(user):
    user = normalize_user(user or {})
    token = create_auth_session(user.get("username", ""))
    if token:
        st.session_state.auth_token = token
        st.query_params["auth"] = token


def clear_persisted_login():
    clear_auth_session(st.session_state.get("auth_token", ""))
    st.session_state.auth_token = None
    if st.query_params.get("auth"):
        try:
            del st.query_params["auth"]
        except Exception:
            st.query_params.clear()


def restore_login_from_storage():
    auth_token = (st.session_state.get("auth_token") or st.query_params.get("auth") or "").strip()
    if not auth_token:
        return
    remembered_user = get_user_by_auth_token(auth_token)
    if remembered_user:
        st.session_state.logged_in = True
        st.session_state.user = remembered_user
        st.session_state.is_paid = remembered_user.get("is_paid", False)
        st.session_state.auth_token = auth_token
        if st.session_state.mode in {"main", "login", "register"}:
            st.session_state.mode = "dashboard"
    else:
        st.session_state.auth_token = None
        if st.query_params.get("auth"):
            try:
                del st.query_params["auth"]
            except Exception:
                st.query_params.clear()


def load_notifications():
    return load_json_file(NOTIFICATIONS_FILE, {})


def save_notifications(notifications):
    save_json_file(NOTIFICATIONS_FILE, notifications)


def get_user_notifications(username):
    username = (username or "").strip()
    if not username:
        return []
    notifications = load_notifications()
    user_notifications = notifications.get(username, [])
    return sorted(user_notifications, key=lambda item: item.get("created_at", ""), reverse=True)


def count_unread_notifications(username):
    return sum(1 for item in get_user_notifications(username) if not item.get("read", False))


def mark_notifications_read(username):
    username = (username or "").strip()
    if not username:
        return
    notifications = load_notifications()
    user_notifications = notifications.get(username, [])
    for item in user_notifications:
        item["read"] = True
    notifications[username] = user_notifications
    save_notifications(notifications)
    st.session_state.notifications = notifications


def create_notification(username, title, message, kind="info"):
    username = (username or "").strip()
    if not username:
        return
    notifications = load_notifications()
    user_notifications = notifications.get(username, [])
    user_notifications.append(
        {
            "title": title,
            "message": message,
            "kind": kind,
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "read": False,
        }
    )
    notifications[username] = user_notifications[-50:]
    save_notifications(notifications)
    st.session_state.notifications = notifications


def notify_user_event(target_username, title, message, kind="info", email_subject=None):
    target_username = (target_username or "").strip()
    if not target_username:
        return

    create_notification(target_username, title, message, kind=kind)
    target_user = get_user_by_username(target_username)
    if not target_user or not target_user.get("email"):
        return

    try:
        send_email_message(
            to_email=target_user["email"],
            subject=email_subject or f"RegnbueMatch: {title}",
            text_body=(
                f"Hei {target_username}!\n\n"
                f"{message}\n\n"
                "Logg inn på RegnbueMatch for å se varselet."
            ),
            html_body=(
                "<div style='font-family:Arial,sans-serif;padding:20px;'>"
                f"<h3>{title}</h3>"
                f"<p>{message}</p>"
                "<p>Logg inn på RegnbueMatch for å se varselet.</p>"
                "</div>"
            ),
        )
    except Exception:
        pass


def load_private_chats():
    return load_json_file(PRIVATE_CHATS_FILE, {})


def save_private_chats(chats):
    save_json_file(PRIVATE_CHATS_FILE, chats)


def load_group_chat_messages():
    messages = load_json_file(GROUP_CHAT_FILE, DEFAULT_GROUP_CHAT)
    return messages or DEFAULT_GROUP_CHAT.copy()


def save_group_chat_messages(messages):
    save_json_file(GROUP_CHAT_FILE, messages)


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
    phone = (user.get("phone") or "").strip()
    bio = (user.get("bio") or "Klar for nye matcher 🌈").strip() or "Klar for nye matcher 🌈"
    photo_url = (user.get("photo_url") or "").strip()
    photo_data = user.get("photo_data") or ""
    likes_sent = list(dict.fromkeys(user.get("likes_sent", [])))
    liked_by = list(dict.fromkeys(user.get("liked_by", [])))
    free_access_granted = bool(user.get("free_access_granted", False))
    profile_completed = bool(user.get("profile_completed", False) or ((photo_url or photo_data) and phone and bio))
    return {
        "username": username,
        "password": user.get("password", "pass123"),
        "email": email,
        "phone": phone,
        "gender": user.get("gender", "Annet"),
        "seeking": user.get("seeking", "Annet"),
        "age": int(user.get("age", 25)),
        "bio": bio,
        "matches": list(dict.fromkeys(user.get("matches", []))),
        "likes_sent": likes_sent,
        "liked_by": liked_by,
        "photo_url": photo_url,
        "photo_data": photo_data,
        "profile_completed": profile_completed,
        "free_access_granted": free_access_granted,
        "is_paid": bool(user.get("is_paid", False) or free_access_granted or is_email_paid(email)),
    }


def is_profile_complete(user):
    return normalize_user(user or {}).get("profile_completed", False)


def get_profile_image(user):
    user = normalize_user(user or {})
    if user.get("photo_data"):
        return user["photo_data"]
    if user.get("photo_url"):
        return user["photo_url"]
    seed = urllib.parse.quote(user.get("username", "Bruker"))
    return f"https://api.dicebear.com/7.x/adventurer/svg?seed={seed}"


def make_uploaded_image_data_url(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        payload = uploaded_file.getvalue()
    except Exception:
        return ""
    if not payload:
        return ""
    mime_type = getattr(uploaded_file, "type", "") or "image/png"
    encoded = base64.b64encode(payload).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


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
        "auth_token": None,
        "verification_code": None,
        "verification_email": None,
        "email_verified": False,
        "pending_verification": None,
        "verification_attempts": 0,
        "email_delivery_message": None,
        "email_delivery_fallback": False,
        "registration_success": False,
        "post_registration_messages": [],
        "private_chats": load_private_chats(),
        "group_chat": load_group_chat_messages(),
        "notifications": load_notifications(),
        "dashboard_section": "Finn noen",
        "active_chat_user": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            if isinstance(value, (list, dict)):
                st.session_state[key] = value.copy()
            else:
                st.session_state[key] = value

    st.session_state.users = load_users()
    st.session_state.private_chats = load_private_chats()
    st.session_state.group_chat = load_group_chat_messages()
    st.session_state.notifications = load_notifications()
    restore_login_from_storage()
    if st.session_state.user:
        refreshed_user = get_user_by_username(st.session_state.user.get("username"))
        if refreshed_user:
            st.session_state.logged_in = True
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
        "likes_sent": [],
        "liked_by": [],
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


def get_incoming_likes(current_user):
    current_user = normalize_user(current_user)
    incoming_users = []
    seen = set()
    for username in current_user.get("liked_by", []):
        if username in current_user.get("matches", []) or username in seen:
            continue
        liked_user = get_user_by_username(username)
        if liked_user:
            incoming_users.append(liked_user)
            seen.add(username)
    return incoming_users


def get_matched_users(current_user):
    current_user = normalize_user(current_user)
    matched_users = []
    for username in current_user.get("matches", []):
        matched_user = get_user_by_username(username)
        if matched_user:
            matched_users.append(matched_user)
    return matched_users


def set_dashboard_section(section_name):
    st.session_state.dashboard_section = section_name
    st.session_state.mode = "dashboard"


def open_chat_with(partner_username):
    st.session_state.active_chat_user = partner_username
    set_dashboard_section("Inbox")


def find_matches(current_user):
    current_user = normalize_user(current_user)
    suggestions = []
    hidden_users = set(current_user.get("matches", [])) | set(current_user.get("likes_sent", []))
    for user in st.session_state.users:
        user = normalize_user(user)
        if user["username"] == current_user["username"] or user["username"] in hidden_users:
            continue
        preference_ok = current_user["seeking"] == "Swingers" or user["gender"] in {current_user["seeking"], "Annet"}
        reverse_ok = user["seeking"] == "Swingers" or current_user["gender"] in {user["seeking"], "Annet"}
        age_ok = abs(user["age"] - current_user["age"]) <= 12
        if (preference_ok or reverse_ok) and age_ok:
            suggestions.append(user)
    if suggestions:
        return suggestions[:8]
    return [
        normalize_user(user)
        for user in st.session_state.users
        if normalize_user(user)["username"] != current_user["username"] and normalize_user(user)["username"] not in hidden_users
    ][:5]


def add_match(current_username, other_username):
    current_user = get_user_by_username(current_username) or {}
    current_user = normalize_user(current_user)
    if other_username in current_user.get("matches", []):
        return True, f"Du og {other_username} er allerede en match 💬"

    other_user = get_user_by_username(other_username) or {}
    other_user_likes = normalize_user(other_user).get("likes_sent", [])
    mutual_match = current_username in other_user_likes
    already_liked = other_username in current_user.get("likes_sent", [])

    if already_liked and not mutual_match:
        return False, f"Du har allerede sendt like til {other_username} 💌"

    updated_users = []
    for raw_user in st.session_state.users:
        user = normalize_user(raw_user)
        if user["username"] == current_username:
            if other_username not in user["likes_sent"]:
                user["likes_sent"].append(other_username)
            if other_username in user.get("liked_by", []):
                user["liked_by"].remove(other_username)
            if mutual_match and other_username not in user["matches"]:
                user["matches"].append(other_username)
        elif user["username"] == other_username:
            if current_username not in user["liked_by"]:
                user["liked_by"].append(current_username)
            if mutual_match and current_username not in user["matches"]:
                user["matches"].append(current_username)
        updated_users.append(user)

    st.session_state.users = updated_users
    save_users(updated_users)
    if st.session_state.user and st.session_state.user["username"] == current_username:
        st.session_state.user = get_user_by_username(current_username)

    if mutual_match:
        open_chat_with(other_username)
        notify_user_event(
            current_username,
            "Ny match 🎉",
            f"Du og {other_username} likte hverandre. Åpne inboxen for å starte chat.",
            kind="match",
        )
        notify_user_event(
            other_username,
            "Ny match 🎉",
            f"Du og {current_username} likte hverandre. Åpne inboxen for å starte chat.",
            kind="match",
        )
        return True, f"Det er en match med {other_username}! Åpne inboxen og start chatten 💜"

    notify_user_event(
        other_username,
        "Nytt like 💜",
        f"{current_username} likte profilen din. Sjekk inboxen for å svare.",
        kind="like",
    )
    return False, f"Like sendt til {other_username} 💌"


def chat_key(user_a, user_b):
    return "::".join(sorted([user_a, user_b]))


def get_chat(user_a, user_b):
    chats = load_private_chats()
    st.session_state.private_chats = chats
    return chats.get(chat_key(user_a, user_b), [])


def send_message(user_a, user_b, message):
    if not message.strip():
        return
    key = chat_key(user_a, user_b)
    chats = load_private_chats()
    history = chats.get(key, [])
    history.append({"sender": user_a, "message": message.strip()})
    chats[key] = history
    save_private_chats(chats)
    st.session_state.private_chats = chats
    notify_user_event(
        user_b,
        "Ny melding 💬",
        f"{user_a} sendte deg en ny melding: “{message.strip()[:80]}”",
        kind="message",
    )


def get_group_chat():
    messages = load_group_chat_messages()
    st.session_state.group_chat = messages
    return messages


def send_group_message(sender, message):
    if not message.strip():
        return
    messages = load_group_chat_messages()
    messages.append({"sender": sender, "message": message.strip()})
    save_group_chat_messages(messages)
    st.session_state.group_chat = messages


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
        unread_notifications = count_unread_notifications(st.session_state.user["username"])
        st.sidebar.caption(f"Medlemskap: {medlemskap}")
        st.sidebar.caption(f"🔔 Varsler: {unread_notifications} uleste")
        st.sidebar.markdown("### Gå direkte til")
        if st.sidebar.button("💜 Finn noen", key="sidebar_browse"):
            set_dashboard_section("Finn noen")
            st.rerun()
        if st.sidebar.button("🔔 Inbox", key="sidebar_inbox"):
            set_dashboard_section("Inbox")
            st.rerun()
        if st.sidebar.button("👤 Min profil", key="sidebar_profile"):
            set_dashboard_section("Min profil")
            st.rerun()
        if st.session_state.user.get("is_paid", False):
            if st.sidebar.button("👥 Felles chat", key="sidebar_group_chat"):
                set_dashboard_section("Felles chat")
                st.rerun()
        if not st.session_state.user.get("is_paid", False):
            spots_left = early_access_spots_left()
            if spots_left > 0:
                st.sidebar.info(f"🎁 {spots_left} gratisplasser igjen for verifiserte profiler.")
            else:
                st.sidebar.info("💎 Full tilgang aktiveres via abonnement.")
        if st.sidebar.button("🚪 Logg ut", key="sidebar_logout"):
            clear_persisted_login()
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
                    <h1>🌈 La oss bygge et fargerikt fellesskap sammen</h1>
                    <p>– og skape plass til flere i laget vårt.</p>
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

    st.subheader("🟢 Online nå")
    online_cols = st.columns(len(ONLINE_SHOWCASE))
    for index, person in enumerate(ONLINE_SHOWCASE):
        with online_cols[index]:
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
                    made_match, message = add_match(st.session_state.user['username'], person['username'])
                    if made_match:
                        st.success(message)
                    else:
                        st.info(message)
                    st.rerun()
                else:
                    st.info("Logg inn eller registrer deg for å begynne å chatte.")

    if spots_left > 0:
        st.success(f"🎉 Fase 2-tilbud: De første {EARLY_ACCESS_LIMIT} verifiserte profilene får gratis full tilgang. {spots_left} plasser igjen.")
    else:
        st.info("Early access er fulltegnet. Nye brukere kan fortsatt registrere seg og oppgradere til abonnement.")

    intro_col, preview_col = st.columns([1.15, 0.85], gap="large")
    with intro_col:
        st.markdown(
            """
            <div class="soft-card">
                <span class="card-badge">VELKOMMEN</span>
                <h3>Et varmere og enklere fellesskap</h3>
                <p>RegnbueMatch skal være et trygt sted for nye forbindelser, gode samtaler og et mer inkluderende miljø for alle som blir med.</p>
                <div class="feature-grid">
                    <div class="feature-item">
                        <h4>💌 Trygg start</h4>
                        <p>Verifisering gjør fellesskapet mer ekte og seriøst.</p>
                    </div>
                    <div class="feature-item">
                        <h4>🌈 Fellesskap</h4>
                        <p>Bygg nettverk, finn matcher og møt flere som passer deg.</p>
                    </div>
                    <div class="feature-item">
                        <h4>📲 Enkelt å bruke</h4>
                        <p>Alt viktig er samlet på ett sted og lett å forstå.</p>
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
                    <p>Opprett profil og vis hvem du er.</p>
                </div>
                <div class="how-step">
                    <h4>2. Finn noen</h4>
                    <p>Se hvem som er online og send likes.</p>
                </div>
                <div class="how-step">
                    <h4>3. Start praten</h4>
                    <p>Når det blir match, dukker chatten opp i inboxen.</p>
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

    st.markdown(
        """
        <div class="cta-card">
            <h3>💜 Klar til å bli med?</h3>
            <p>Opprett profil, bli synlig i fellesskapet og start samtaler med folk som matcher deg.</p>
            <p class="tiny-note">Enklere, varmere og mer inkluderende – rett fra mobilen eller PC.</p>
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
            st.session_state.logged_in = True
            st.session_state.user = payload
            st.session_state.is_paid = payload.get("is_paid", False)
            persist_login_state(payload)
            st.session_state.registration_success = True
            st.session_state.mode = "dashboard"
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
            persist_login_state(user)
            st.success(f"Velkommen, {user['username']}! 🚀")
            st.rerun()
        else:
            st.error("Feil brukernavn/e-post eller passord.")


def render_priority_notifications(user):
    user = normalize_user(user)
    unread_items = [item for item in get_user_notifications(user["username"]) if not item.get("read", False)]
    if not unread_items:
        return

    banner_class_by_kind = {
        "like": "like-banner",
        "match": "match-banner",
        "message": "message-banner",
    }

    st.markdown("## 🔔 Nye oppdateringer")
    for item in unread_items[:3]:
        banner_class = banner_class_by_kind.get(item.get("kind"), "notice-banner")
        st.markdown(
            f"""
            <div class="priority-banner {banner_class}">
                <div class="priority-banner-title">{item.get('title', 'Nytt varsel')}</div>
                <div class="priority-banner-text">{item.get('message', 'Sjekk inboxen for detaljer.')}</div>
                <div class="priority-banner-time">{item.get('created_at', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if len(unread_items) > 3:
        st.caption(f"Du har totalt {len(unread_items)} uleste varsler. Åpne `Inbox` for å se alle.")


def render_profile_tab():
    user = normalize_user(st.session_state.user)
    st.header("Min profil")

    if is_profile_complete(user):
        st.success("Profilen din er fullført og klar for nye matcher ✅")
    else:
        st.warning("Legg til profilbilde og litt mer info for å fullføre profilen din.")

    preview_col, form_col = st.columns([0.85, 1.15], gap="large")
    with preview_col:
        st.image(get_profile_image(user), use_container_width=True)
        st.markdown(f"**{user['username']}**, {user['age']} år")
        st.caption(user.get("bio") or "Legg til en bio for å fortelle litt om deg selv.")
        st.write(f"**Kjønn:** {user.get('gender', 'Annet')}")
        st.write(f"**Søker:** {user.get('seeking', 'Annet')}")
        st.write(f"**Telefon:** {user.get('phone') or 'Ikke lagt til ennå'}")
        st.write(f"**Profilstatus:** {'Komplett ✅' if is_profile_complete(user) else 'Mangler bilde/info'}")

    with form_col:
        with st.form("profile_edit_form"):
            gender_options = ["Mann", "Kvinne", "Annet"]
            seeking_options = ["Mann", "Kvinne", "Annet", "Swingers"]
            edited_phone = st.text_input("Telefonnummer", value=user.get("phone", ""))
            edited_age = st.number_input("Alder", min_value=18, max_value=99, value=int(user.get("age", 25)))
            edited_gender = st.selectbox(
                "Kjønn",
                gender_options,
                index=gender_options.index(user.get("gender", "Annet")) if user.get("gender", "Annet") in gender_options else 2,
            )
            edited_seeking = st.selectbox(
                "Hva søker du etter?",
                seeking_options,
                index=seeking_options.index(user.get("seeking", "Annet")) if user.get("seeking", "Annet") in seeking_options else 2,
            )
            edited_bio = st.text_area(
                "Om deg selv",
                value=user.get("bio", ""),
                placeholder="Skriv litt om deg selv, interesser og hvem du ønsker å møte.",
            )
            uploaded_photo = st.file_uploader("Last opp profilbilde", type=["jpg", "jpeg", "png", "webp"])
            photo_url = st.text_input(
                "Eller lim inn bilde-URL",
                value=user.get("photo_url", ""),
                placeholder="https://...",
            )
            remove_photo = st.checkbox("Bruk standard avatar i stedet")
            saved = st.form_submit_button("💾 Lagre profil")

        if saved:
            updated_user = user.copy()
            updated_user.update({
                "phone": (edited_phone or "").strip(),
                "age": int(edited_age),
                "gender": edited_gender,
                "seeking": edited_seeking,
                "bio": (edited_bio or "").strip() or "Ny på RegnbueMatch 🌈",
            })

            if remove_photo:
                updated_user["photo_data"] = ""
                updated_user["photo_url"] = ""
            else:
                new_photo_data = make_uploaded_image_data_url(uploaded_photo)
                if new_photo_data:
                    updated_user["photo_data"] = new_photo_data
                    updated_user["photo_url"] = ""
                else:
                    cleaned_photo_url = (photo_url or "").strip()
                    if cleaned_photo_url:
                        updated_user["photo_url"] = cleaned_photo_url
                        updated_user["photo_data"] = ""

            updated_user["profile_completed"] = bool(
                (updated_user.get("photo_data") or updated_user.get("photo_url"))
                and updated_user.get("phone")
                and updated_user.get("bio")
            )
            update_user_record(updated_user)
            st.success("Profilen din er oppdatert ✅")
            st.rerun()


def render_matches_tab():
    current_user = normalize_user(st.session_state.user)
    incoming_like_names = {user['username'] for user in get_incoming_likes(current_user)}
    suggestions = find_matches(current_user)

    st.header("Finn noen")
    st.caption("Det er enkelt: se profil → trykk `Lik` → hvis dere liker hverandre, havner chatten i `Inbox`.")

    if incoming_like_names:
        st.success(f"💜 {len(incoming_like_names)} person(er) liker deg allerede. Åpne `Inbox` for å svare.")

    if not suggestions:
        st.info("Ingen nye profiler akkurat nå. Sjekk inboxen eller kom tilbake litt senere.")
        return

    for match in suggestions:
        with st.container(border=True):
            top_col, info_col = st.columns([0.3, 0.7], gap="medium")
            with top_col:
                st.image(get_profile_image(match), use_container_width=True)
            with info_col:
                badge = "💘 Liker deg" if match['username'] in incoming_like_names else "✨ Ny profil"
                st.markdown(f"**{badge}**")
                st.markdown(f"### {match['username']}, {match['age']}")
                st.caption(match['bio'])
                st.write(f"{match.get('gender', 'Annet')} · Søker {match.get('seeking', 'Annet')}")
                button_label = "💘 Lik tilbake" if match['username'] in incoming_like_names else f"💜 Lik {match['username']}"
                if st.button(button_label, key=f"match_{match['username']}"):
                    made_match, message = add_match(st.session_state.user['username'], match['username'])
                    if made_match:
                        st.success(message)
                    else:
                        st.info(message)
                    st.rerun()


def render_inbox_tab():
    current_user = normalize_user(st.session_state.user)
    incoming_likes = get_incoming_likes(current_user)
    matched_users = get_matched_users(current_user)
    notifications = get_user_notifications(current_user["username"])
    unread_notifications = count_unread_notifications(current_user["username"])

    st.header("Inbox")
    st.caption("Alt viktig vises her: varsler, likes, matcher og meldinger.")

    summary_cols = st.columns(3)
    summary_cols[0].metric("Likes", len(incoming_likes))
    summary_cols[1].metric("Matcher", len(matched_users))
    summary_cols[2].metric("Varsler", unread_notifications)

    notice_col, action_col = st.columns([0.7, 0.3])
    with notice_col:
        st.markdown(f"**🔔 Varsler ({unread_notifications} uleste)**")
    with action_col:
        if unread_notifications and st.button("Marker som lest", key="mark_notifications_read_btn"):
            mark_notifications_read(current_user["username"])
            st.rerun()

    if notifications:
        for index, item in enumerate(notifications[:8]):
            with st.container(border=True):
                status = "🟣 Ulest" if not item.get("read", False) else "⚪ Lest"
                st.markdown(f"**{item.get('title', 'Varsel')}** · {status}")
                st.caption(item.get("message", ""))
                st.caption(item.get("created_at", ""))
    else:
        st.info("Ingen varsler ennå. Likes, matcher og meldinger dukker opp her.")

    if incoming_likes:
        st.subheader("💜 Liker deg")
        for admirer in incoming_likes:
            with st.container(border=True):
                info_col, action_col = st.columns([0.72, 0.28], gap="medium")
                with info_col:
                    st.markdown(f"**{admirer['username']}**, {admirer['age']} år")
                    st.caption(admirer.get('bio') or 'Vil gjerne bli kjent med deg.')
                with action_col:
                    if st.button(f"💘 Match med {admirer['username']}", key=f"like_back_{admirer['username']}"):
                        made_match, message = add_match(current_user['username'], admirer['username'])
                        if made_match:
                            st.success(message)
                        else:
                            st.info(message)
                        st.rerun()
    else:
        st.info("Ingen nye likes enda. Når noen liker deg, dukker de opp her.")

    st.subheader("💬 Samtaler")
    if not matched_users:
        st.info("Ingen matcher ennå. Gå til `Utforsk` og lik noen profiler for å starte en samtale.")
        return

    partner_names = [match['username'] for match in matched_users]
    if st.session_state.active_chat_user not in partner_names:
        st.session_state.active_chat_user = partner_names[0]

    for match in matched_users:
        history = get_chat(current_user['username'], match['username'])
        last_message = history[-1]['message'] if history else "Ingen meldinger ennå — si hei 👋"
        with st.container(border=True):
            summary_col, open_col = st.columns([0.72, 0.28], gap="medium")
            with summary_col:
                st.markdown(f"**{match['username']}**")
                st.caption(last_message)
            with open_col:
                if st.button(f"Åpne chat", key=f"open_chat_{match['username']}"):
                    open_chat_with(match['username'])
                    st.rerun()

    active_partner = st.session_state.active_chat_user
    if active_partner:
        st.markdown(f"### Chat med {active_partner}")
        for item in get_chat(current_user['username'], active_partner):
            role = "user" if item["sender"] == current_user['username'] else "assistant"
            with st.chat_message(role):
                st.write(item["message"])

        message = st.text_input("Skriv melding", key=f"private_message_input_{active_partner}")
        if st.button("Send melding", key=f"send_chat_btn_{active_partner}"):
            send_message(current_user['username'], active_partner, message)
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
    user = normalize_user(st.session_state.user)
    st.session_state.user = user
    st.success(f"Velkommen tilbake, {user['username']}!")

    render_priority_notifications(user)

    if not is_profile_complete(user):
        st.info("💡 Start med `Min profil`, så blir resten mye enklere.")

    incoming_likes = get_incoming_likes(user)
    unread_notifications = count_unread_notifications(user["username"])
    stats = st.columns(3)
    stats[0].metric("Matcher", len(user.get("matches", [])))
    stats[1].metric("Varsler", unread_notifications)
    stats[2].metric("Profil", "Komplett" if is_profile_complete(user) else "Ufullstendig")

    st.markdown("### Slik bruker du appen")
    st.markdown(
        "1. **Finn noen** og trykk `Lik` på profiler du liker.  \n"
        "2. Se **Inbox** når du får likes, matcher eller meldinger.  \n"
        "3. Oppdater **Min profil** når du vil legge til bilde eller bio."
    )

    section_options = ["Finn noen", "Inbox", "Min profil"]
    if user.get("is_paid", False):
        section_options.append("Felles chat")

    if st.session_state.get("dashboard_section") not in section_options:
        if unread_notifications or incoming_likes:
            st.session_state.dashboard_section = "Inbox"
        elif not is_profile_complete(user):
            st.session_state.dashboard_section = "Min profil"
        else:
            st.session_state.dashboard_section = "Finn noen"

    quick_cols = st.columns(len(section_options))
    for index, section_name in enumerate(section_options):
        if quick_cols[index].button(section_name, key=f"quick_nav_{section_name}"):
            set_dashboard_section(section_name)
            st.rerun()

    selected_section = st.radio(
        "Velg side",
        section_options,
        key="dashboard_section",
        horizontal=True,
        label_visibility="collapsed",
    )

    if selected_section == "Finn noen":
        render_matches_tab()
    elif selected_section == "Inbox":
        render_inbox_tab()
    elif selected_section == "Min profil":
        render_profile_tab()
    elif selected_section == "Felles chat":
        render_group_chat_tab()


def main():
    render_sidebar()
    render_header()

    if st.session_state.registration_success:
        st.success("Profil opprettet! Du er nå logget inn og kan fullføre profilen under `Min profil`.")
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
