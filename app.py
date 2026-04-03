from dotenv import load_dotenv
import json
import os
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
import stripe

load_dotenv()
st.set_page_config(page_title="RegnbueMatch", page_icon="🌈", layout="centered")

USERS_FILE = "users.json"
PAID_EMAILS_FILE = "paid_emails.json"

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
    border-radius: 24px;
    padding: 22px 18px;
    color: #ffffff;
    box-shadow: 0 18px 38px rgba(91, 36, 122, 0.22);
    margin-bottom: 14px;
}
.hero-card h1, .hero-card p {
    color: #ffffff !important;
    margin: 0;
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
.stButton > button, .stLinkButton > a {
    width: 100%;
    border-radius: 14px !important;
    min-height: 48px;
    font-size: 1rem;
    font-weight: 600;
}
.stImage img {
    border-radius: 18px;
}
[data-testid="stSidebar"] {
    background: rgba(162, 89, 198, 0.08) !important;
    border-right: 1px solid rgba(162, 89, 198, 0.12);
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(162, 89, 198, 0.16);
    border-radius: 16px;
    padding: 10px 12px;
}
.profile-card {
    background: rgba(255,255,255,0.88);
    border-radius: 18px;
    padding: 14px;
    border: 1px solid rgba(162,89,198,0.14);
    box-shadow: 0 8px 24px rgba(69, 38, 100, 0.08);
    margin-bottom: 12px;
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
        "is_paid": bool(user.get("is_paid", False) or is_email_paid(email)),
    }


def save_users(users):
    save_json_file(USERS_FILE, [normalize_user(user) for user in users])


def load_users():
    users = [normalize_user(user) for user in load_json_file(USERS_FILE, [])]
    existing_names = {user["username"] for user in users}
    for demo_user in DEMO_PROFILES:
        if demo_user["username"] not in existing_names:
            users.append(normalize_user(demo_user))
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
        "registration_success": False,
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


def create_verification_code():
    return "".join(random.choices(string.digits, k=6))


def send_verification_email(to_email, code):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "tobias.mikkelsen02@gmail.com")
    smtp_pass = os.getenv("SMTP_PASS", "qfrt nlmk dqeq rkwn")

    if not to_email:
        return "Skriv inn en gyldig e-postadresse først."

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = "Verifiseringskode for RegnbueMatch"
    msg.attach(MIMEText(f"Din kode er: {code}", "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as error:
        return str(error)


def register_user(username, password, gender, age, bio, seeking, email, phone):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    phone = (phone or "").strip()

    if not username or not password or not email or not phone:
        return False, "Fyll ut brukernavn, passord, e-post og telefonnummer."

    if any(user["username"].lower() == username.lower() for user in st.session_state.users):
        return False, "Brukernavnet er allerede i bruk."

    if any(user["email"].lower() == email for user in st.session_state.users):
        return False, "E-postadressen er allerede registrert."

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
        "is_paid": st.session_state.is_paid or is_email_paid(email),
    })
    st.session_state.users.append(new_user)
    save_users(st.session_state.users)
    return True, new_user


def authenticate_user(username, password):
    username = (username or "").strip().lower()
    for user in st.session_state.users:
        if user["username"].lower() == username and user["password"] == password:
            return normalize_user(user)
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
        medlemskap = "Aktivt" if st.session_state.user.get("is_paid", False) else "Gratis"
        st.sidebar.caption(f"Medlemskap: {medlemskap}")
        if st.sidebar.button("🏠 Forside", key="sidebar_home_logged"):
            st.session_state.mode = "main"
            st.rerun()
        if not st.session_state.user.get("is_paid", False):
            if st.sidebar.button("💎 Aktiver demo-medlemskap", key="sidebar_demo_upgrade"):
                st.session_state.user["is_paid"] = True
                update_user_record(st.session_state.user)
                st.success("Demo-medlemskap aktivert!")
                st.rerun()
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
            <h1>🌈 RegnbueMatch</h1>
            <p>En renere, raskere og mer mobilvennlig datingside med PWA-støtte.</p>
            <div class="pill-row">
                <span class="pill">Mobilklar</span>
                <span class="pill">PWA</span>
                <span class="pill">Stripe</span>
                <span class="pill">E-postverifisering</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("📲 Installer appen", "/app/static/index.html", use_container_width=True)
    with col2:
        st.link_button("🖼️ Åpne splash/PWA", "/app/static/index.html", use_container_width=True)
    st.caption("På mobil kan du velge ‘Legg til på startskjerm’, og på PC kan du bruke ‘Installer app’ i nettleseren.")


def render_home():
    stats = st.columns(3)
    stats[0].metric("Profiler", len(st.session_state.users))
    stats[1].metric("Online nå", len(ONLINE_SHOWCASE))
    stats[2].metric("PWA", "Klar")

    if os.path.exists("static/icons/splashscreen.png"):
        st.image("static/icons/splashscreen.png", use_container_width=True)

    with st.container(border=True):
        st.subheader("✨ Hvorfor RegnbueMatch?")
        st.write(
            "- trygg registrering med e-postkode  \n"
            "- Stripe-støtte for abonnement  \n"
            "- matcher, chat og fellesskap  \n"
            "- installér som app på mobil og PC"
        )

    st.subheader("🟢 Online nå")
    for person in ONLINE_SHOWCASE:
        with st.container(border=True):
            st.image(person["img"], use_container_width=True)
            st.markdown(f"**{person['username']}**, {person['age']} år")
            st.caption(person["bio"])
            if st.button(f"💜 Vis interesse for {person['username']}", key=f"showcase_{person['username']}"):
                if st.session_state.logged_in:
                    st.success(f"Hyggelig! {person['username']} er lagt til i dine forslag.")
                else:
                    st.info("Logg inn eller registrer deg for å begynne å chatte.")


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

    if reg_email and is_email_paid(reg_email):
        st.session_state.is_paid = True
        st.success("Denne e-posten har allerede en bekreftet betaling.")

    with st.container(border=True):
        st.markdown("#### 💎 Abonnement")
        if st.session_state.is_paid:
            st.success("Du har aktivt abonnement og tilgang til chat-funksjoner.")
        else:
            st.warning("Du kan registrere deg gratis, men abonnement trengs for full chat-tilgang.")
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
        if result is True:
            st.success(f"Kode sendt til {reg_email} 📧")
        else:
            st.error(f"Kunne ikke sende e-post: {result}")

    if st.session_state.pending_verification and not st.session_state.email_verified:
        code_input = st.text_input("Skriv inn koden du har mottatt", key="verify_code")
        if st.button("Bekreft kode", key="confirm_code_main_btn"):
            if code_input == st.session_state.verification_code:
                st.session_state.email_verified = True
                st.session_state.verification_code = None
                st.session_state.pending_verification = None
                st.success("E-post verifisert ✅")
            else:
                st.session_state.verification_attempts += 1
                if st.session_state.verification_attempts >= 3:
                    reset_verification_state()
                    st.error("For mange feil forsøk. Be om ny kode.")
                else:
                    st.error("Feil kode. Prøv igjen.")

    if not st.session_state.email_verified:
        st.info("Du må verifisere e-postadressen før du kan registrere profilen.")

    if st.button("✅ Registrer profil", key="register_main_btn", disabled=not st.session_state.email_verified):
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
            reset_verification_state()
            st.session_state.registration_success = True
            st.session_state.mode = "login"
            st.rerun()
        else:
            st.error(payload)


def render_login():
    st.subheader("Logg inn")
    login_username = st.text_input("Brukernavn", key="login_user")
    login_password = st.text_input("Passord", type="password", key="login_pass")

    if st.button("Logg inn", key="login_submit"):
        user = authenticate_user(login_username, login_password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.is_paid = user.get("is_paid", False)
            st.success(f"Velkommen, {login_username}! 🚀")
            st.rerun()
        else:
            st.error("Feil brukernavn eller passord.")


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
    st.header("Felles Chat (kun for betalende)")
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
    stats[1].metric("Medlemskap", "Aktivt" if user.get("is_paid", False) else "Gratis")
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
        st.success("Bruker registrert! Du kan nå logge inn med den nye profilen.")
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
