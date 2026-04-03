
from dotenv import load_dotenv
import os

load_dotenv()

import json
import os

PAID_EMAILS_FILE = "paid_emails.json"

def load_users():
	if os.path.exists("users.json"):
		with open("users.json", "r") as f:
			return json.load(f)
	return []

def save_users(users):
	with open("users.json", "w") as f:
		json.dump(users, f)

def load_paid_emails():
	if os.path.exists(PAID_EMAILS_FILE):
		with open(PAID_EMAILS_FILE, "r") as f:
			return json.load(f)
	return []

def save_paid_email(email):
	if not email:
		return
	paid_emails = load_paid_emails()
	if email not in paid_emails:
		paid_emails.append(email)
		with open(PAID_EMAILS_FILE, "w") as f:
			json.dump(paid_emails, f)

def is_email_paid(email):
	if not email:
		return False
	return email in load_paid_emails()
# TEST NEDERST






import streamlit as st
import stripe
import random
import string
import smtplib
from typing import List, Dict

if "users" not in st.session_state:
	users_loaded = load_users()
	if not users_loaded:
		# Generer 100 fake brukere
		import random
		fake_names = [
			f"Bruker{n}" for n in range(1, 101)
		]
		fake_users = []
		for name in fake_names:
			fake_users.append({
				"username": name,
				"password": "pass123",
				"email": f"{name.lower()}@fake.com"
			})
		save_users(fake_users)
		users_loaded = fake_users
	st.session_state.users = users_loaded

# --- SIDEBAR MENY ---
st.sidebar.title("Meny")
if st.sidebar.button("Logg inn"):
	st.session_state.mode = "login"
	st.rerun()
if st.sidebar.button("Registrer"):
	st.session_state.mode = "register"
	st.rerun()


# --- EPOST VERIFISERING ---
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(to_email, code):
	smtp_server = "smtp.gmail.com"
	smtp_port = 587
	smtp_user = "tobias.mikkelsen02@gmail.com"
	smtp_pass = "qfrt nlmk dqeq rkwn"

	msg = MIMEMultipart()
	msg["From"] = smtp_user
	msg["To"] = to_email
	msg["Subject"] = "Verifiseringskode"

	body = f"Din kode er: {code}"
	msg.attach(MIMEText(body, "plain"))

	try:
		server = smtplib.SMTP(smtp_server, smtp_port)
		server.starttls()
		server.login(smtp_user, smtp_pass)
		server.send_message(msg)
		server.quit()
		print("🚀 E-post sendt!")
		return True
	except Exception as e:
		print("❌ Feil:", e)
		return str(e)

# ---------------- DATABASE (enkel) ----------------
if "users" not in st.session_state:
	st.session_state.users = []

# ---------------- MODE ----------------
if "mode" not in st.session_state:
	st.session_state.mode = "register"

# ---------------- VERIFY STATE ----------------
for key, default in [
	("verification_code", None),
	("verification_email", None),
	("email_verified", False),
]:
	if key not in st.session_state:
		st.session_state[key] = default

# ---------------- REGISTER ----------------
if st.session_state.mode == "register":
	st.write("---")

	username = st.text_input("Brukernavn")
	password = st.text_input("Passord", type="password")
	email = st.text_input("E-post")

	st.title("Registrer deg")

	# SEND KODE
	if st.button("Send verifiseringskode"):
		if not email:
			st.error("Skriv inn e-post først")
		else:
			code = "".join(random.choices(string.digits, k=6))
			st.session_state.verification_code = code
			st.session_state.verification_email = email
			st.session_state.email_verified = False

			result = send_verification_email(email, code)

			if result is True:
				st.success("Kode sendt til e-post 📧")
			else:
				st.error(result)

	# VERIFY INPUT
	if st.session_state.verification_code:
		code_input = st.text_input("Skriv inn kode")

		if st.button("Bekreft kode"):
			if code_input == st.session_state.verification_code:
				st.success("E-post verifisert ✅")
				st.session_state.email_verified = True
				st.session_state.verification_code = None
			else:
				st.error("Feil kode")

	# REGISTER BUTTON
	if st.button("Registrer", disabled=not st.session_state.email_verified):
		if not username or not password:
			st.error("Fyll ut alle felt")
		else:
			st.session_state.users.append({
				"username": username,
				"password": password,
				"email": email
			})
			save_users(st.session_state.users)

			st.success("Bruker opprettet 🎉")

			# reset state
			st.session_state.email_verified = False

			# gå til login
			st.session_state.mode = "login"
			st.rerun()

# ---------------- LOGIN ----------------
elif st.session_state.mode == "login":
	st.title("Logg inn")

	login_user = st.text_input("Brukernavn")
	login_pass = st.text_input("Passord", type="password")

	if st.button("Logg inn", key="login_btn_main"):
		user = next(
			(u for u in st.session_state.users
			 if u["username"] == login_user and u["password"] == login_pass),
			None
		)

		if user:
			st.success(f"Velkommen {login_user} 🚀")
		else:
			st.error("Feil brukernavn eller passord")

	if st.button("Gå til registrering", key="goto_register_btn"):
		st.session_state.mode = "register"
		st.rerun()
# Rainbow background CSS + sidebar styling + animert finger



# Rainbow background CSS + sidebar styling + animert finger

# Ny bakgrunn med svak gradient, blur og opacity
rainbow_css = """
<style>
body {
	min-height: 100vh;
	background: linear-gradient(120deg, rgba(255,0,90,0.7) 0%, rgba(255,153,0,0.6) 20%, rgba(255,255,0,0.5) 40%, rgba(51,204,51,0.5) 60%, rgba(0,102,255,0.5) 80%, rgba(102,0,204,0.5) 100%);
	backdrop-filter: blur(8px);
}
.stApp {
	background: rgba(255,255,255,0.7);
	border-radius: 18px;
	box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
	padding: 12px 0 12px 0;
}
section[data-testid="stSidebar"] {
	background: rgba(162,89,198,0.85) !important;
	backdrop-filter: blur(4px);
}
</style>
"""
st.markdown(rainbow_css, unsafe_allow_html=True)







st.set_page_config(page_title="RegnbueMatch", page_icon="🌈", layout="centered")

# Initier session state tidlig
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'goto_register' not in st.session_state:
    st.session_state.goto_register = False
if 'mode' not in st.session_state:
    st.session_state.mode = 'main'  # Verdier: 'main', 'register', 'login'


# 'Lag Profil' knapp på forsiden
if not st.session_state.logged_in and st.session_state.mode == 'main':
	if st.button("✨ Lag Profil / Kom i gang", key="create_profile_btn"):
		st.session_state.mode = 'register'
st.title("🌈 RegnbueMatch")


# Nullstill mode til 'main' etter utlogging eller etter registreringsflyt
if not st.session_state.logged_in and st.session_state.mode != 'main':
	if st.sidebar.button("Tilbake til forsiden", key="back_to_main"):
		st.session_state.mode = 'main'


# Styr flyt med mode og vis kun én meny
choice = None
if st.session_state.mode == 'register':
	choice = "Registrer"
elif st.session_state.mode == 'login':
	choice = "Logg inn"
elif not st.session_state.logged_in:
	menu = ["Logg inn", "Registrer"]
	choice = st.sidebar.selectbox("Meny", menu, key="sidebar_menu_selectbox")

# Etter registrering: vis stor suksessmelding og gå til login
if st.session_state.get('registration_success', False):
	st.markdown("""
	<div style='background: #d4edda; color: #155724; border-radius: 16px; padding: 32px 18px; text-align: center; font-size: 1.35em; margin-bottom: 24px; border: 2px solid #28a745;'>
		<b>Bruker registrert!</b><br>Du kan nå logge inn med din nye konto.
	</div>
	""", unsafe_allow_html=True)
	st.session_state['registration_success'] = False
	st.session_state.mode = 'login'
	st.stop()

if 'logged_in' not in st.session_state:
	st.session_state.logged_in = False
	st.session_state.user = None




if choice == "Registrer":
	st.subheader("Opprett ny profil")
	# Betalingssystem: vis kjøp-knapp og status

	# --- STRIPE INTEGRASJON ---
	STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
	STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
	APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")

	stripe_config_ok = bool(STRIPE_SECRET_KEY and STRIPE_PRICE_ID)
	if stripe_config_ok:
		stripe.api_key = STRIPE_SECRET_KEY
	else:
		st.info("Stripe er ikke konfigurert ennå. Sett STRIPE_SECRET_KEY og STRIPE_PRICE_ID i miljøvariabler for å teste betaling.")

	if not APP_BASE_URL:
		st.info("Sett APP_BASE_URL i miljøvariabler (f.eks. https://din-app.onrender.com) for korrekt Stripe-redirect i produksjon.")

	query_params = st.query_params
	if query_params.get("success") == "true":
		session_id = query_params.get("session_id", "")
		if stripe_config_ok and session_id:
			try:
				checkout_session = stripe.checkout.Session.retrieve(session_id)
				if checkout_session.get("payment_status") == "paid":
					st.session_state.is_paid = True
					paid_email = checkout_session.get("customer_email")
					if not paid_email:
						customer_details = checkout_session.get("customer_details") or {}
						paid_email = customer_details.get("email")
					save_paid_email(paid_email)
					st.success("Betaling bekreftet av Stripe. Du har aktivt abonnement!")
				else:
					st.warning("Betalingen er ikke bekreftet enda hos Stripe.")
			except Exception as e:
				st.error(f"Kunne ikke verifisere Stripe-betalingen: {e}")
		query_params.clear()
	elif query_params.get("canceled") == "true":
		st.info("Betalingen ble avbrutt.")
		query_params.clear()

	if "is_paid" not in st.session_state:
		st.session_state.is_paid = False
	if not st.session_state.is_paid:
		st.warning("Du må ha abonnement for å chatte med brukere!")
		if st.button("Kjøp abonnement (kr 199)", key="buy_subscription", disabled=not (stripe_config_ok and bool(APP_BASE_URL))):
			# Opprett Stripe Checkout Session
			try:
				session_payload = {
					"payment_method_types": ["card"],
					"line_items": [{
						"price": STRIPE_PRICE_ID,
						"quantity": 1,
					}],
					"mode": "subscription",
					"success_url": f"{APP_BASE_URL}/?success=true&session_id={{CHECKOUT_SESSION_ID}}",
					"cancel_url": f"{APP_BASE_URL}/?canceled=true",
				}
				if st.session_state.get("reg_email"):
					session_payload["customer_email"] = st.session_state["reg_email"]

				session = stripe.checkout.Session.create(**session_payload)
				st.markdown(f"[Klikk her for å betale med Stripe]({session.url})", unsafe_allow_html=True)
				st.info("Fullfør betalingen i Stripe-vinduet. Du blir sendt tilbake hit for automatisk bekreftelse.")
			except Exception as e:
				st.error(f"Stripe-feil ved oppretting av betaling: {e}")
	else:
		st.success("Du har aktivt abonnement!")

	# Vis 10 fake brukere som 'Online nå' (kun hvis ikke logget inn)
	if not st.session_state.get('logged_in', False):
		st.markdown("<b>Online nå:</b>", unsafe_allow_html=True)
		fake_online = st.session_state.users[:10]
		for idx, user in enumerate(fake_online):
			btn = st.button(f"{user['username']}", key=f"fakeuser_{idx}")
			st.image(f"https://api.dicebear.com/7.x/adventurer/svg?seed={user['username']}", width=60)
			if btn:
				if st.session_state.is_paid:
					st.success(f"Du kan nå chatte med {user['username']}! (demo)")
				else:
					st.info(f"Dette er en demo-konto. Kjøp abonnement for å chatte med brukere som {user['username']}!")
		st.info("Kjøp abonnement for å chatte med disse brukerne!")

	reg_username = st.text_input("Brukernavn", key="reg_user")
	reg_password = st.text_input("Passord", type="password", key="reg_pass")
	reg_email = st.text_input("E-postadresse", key="reg_email")
	if reg_email and is_email_paid(reg_email):
		st.session_state.is_paid = True
		st.success("Denne e-posten har allerede en bekreftet betaling.")
	reg_phone = st.text_input("Telefonnummer", key="reg_phone")
	reg_gender = st.selectbox("Kjønn", ["Mann", "Kvinne", "Annet"], key="reg_gender")
	reg_seeking = st.selectbox("Hva søker du etter?", ["Mann", "Kvinne", "Annet", "Swingers"], key="reg_seeking")
	reg_age = st.number_input("Alder", min_value=18, max_value=99, value=25, key="reg_age")
	reg_bio = st.text_area("Om deg selv", key="reg_bio")


	# Initier session state for verifisering og e-post
	if 'pending_verification' not in st.session_state:
		st.session_state['pending_verification'] = None
	if 'verification_code' not in st.session_state:
		st.session_state['verification_code'] = None
	if 'verification_email' not in st.session_state:
		st.session_state['verification_email'] = None
	if 'email_sent' not in st.session_state:
		st.session_state['email_sent'] = False
	if 'email_verified' not in st.session_state:
		st.session_state['email_verified'] = False
	if 'verification_attempts' not in st.session_state:
		st.session_state['verification_attempts'] = 0

	import random
	import string
	import smtplib
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart





	# Suksessmelding etter registrering
	if st.session_state.get('registration_success', False):
		st.markdown("""
		<div style='background: #d4edda; color: #155724; border-radius: 16px; padding: 32px 18px; text-align: center; font-size: 1.35em; margin-bottom: 24px; border: 2px solid #28a745;'>
			<b>Bruker registrert!</b><br>Du kan nå logge inn med din nye konto.
		</div>
		""", unsafe_allow_html=True)
		st.session_state['registration_success'] = False
		st.stop()

	# Send kode-knapp og logikk
	st.write("\n---\n")
	if st.button("Send kode"):
		code = ''.join(random.choices(string.digits, k=6))
		st.session_state['verification_code'] = code
		st.session_state['verification_email'] = reg_email
		st.session_state['pending_verification'] = reg_username if reg_username else reg_email
		st.session_state['email_verified'] = False
		st.session_state['verification_attempts'] = 0
		st.session_state['last_code_sent'] = code
		st.session_state['last_email_sent'] = reg_email
		result = send_verification_email(reg_email, code)
		if result is True:
			st.info(f"En kode er sendt til e-post: {reg_email} (sjekk innboksen din)")
			st.session_state.email_sent = True
		else:
			st.error(f"Kunne ikke sende e-post: {result}")
			st.warning("Sjekk at e-post og app-passord er riktig satt opp. Kontakt support hvis problemet vedvarer.")

	if st.session_state['pending_verification'] and not st.session_state.get('email_verified', False):
		# Vis kun info-melding, ikke send e-post på nytt
		st.info(f"En kode er sendt til e-post: {st.session_state['verification_email']} (sjekk innboksen din)")
		input_code = st.text_input("Skriv inn koden du har mottatt:", key="verify_code")
		if st.button("Bekreft kode"):
			if input_code == st.session_state['verification_code']:
				st.success("Verifisering vellykket! Du kan nå registrere deg.")
				st.session_state['email_verified'] = True
				st.session_state['verification_code'] = None
				st.session_state['pending_verification'] = None
				st.session_state['email_sent'] = False
				st.session_state['verification_attempts'] = 0
				st.session_state['last_code_sent'] = None
				st.session_state['last_email_sent'] = None
				# Ikke rerun, behold bruker på registreringssiden
			else:
				st.session_state['verification_attempts'] += 1
				if st.session_state['verification_attempts'] >= 3:
					st.error("For mange feil forsøk. Be om ny kode.")
					st.session_state['verification_code'] = None
					st.session_state['pending_verification'] = None
					st.session_state['email_sent'] = False
					st.session_state['verification_attempts'] = 0
					st.session_state['last_code_sent'] = None
					st.session_state['last_email_sent'] = None
				else:
					st.error("Feil kode. Prøv igjen.")

	# Registreringsskjemaet vises alltid, men knappen er deaktivert hvis ikke verifisert
	registrer_disabled = not st.session_state.get('email_verified', False)
	if registrer_disabled and not st.session_state.get('pending_verification', False):
		st.info("Du må verifisere e-postadressen din før du kan registrere deg.")
	else:
		if st.button("Registrer", disabled=registrer_disabled):
			if not reg_password:
				st.error("Du må skrive inn et passord.")
			elif not reg_email or not reg_phone:
				st.error("E-post og telefonnummer må fylles ut.")
			else:
				register_user(
					reg_username, reg_password, reg_gender, reg_age, reg_bio, reg_seeking,
					email=reg_email, phone=reg_phone
				)
				st.session_state['registration_success'] = True
				st.session_state.mode = 'login'   # 👈 viktig fix
				st.rerun()

# Vis demo 'Online nå' kun hvis ikke innlogget og ikke på registreringssiden
if not st.session_state.logged_in and not st.session_state.goto_register:
		st.markdown("<hr>", unsafe_allow_html=True)
		st.subheader("Online nå 🟢")
		demo_online = [
				{"username": "PrideAlex", "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=facearea&w=128&q=80&facepad=2"},
				{"username": "RainbowSara", "img": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=facearea&w=128&q=80&facepad=2"},
				{"username": "QueerChris", "img": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=facearea&w=128&q=80&facepad=2"}
		]
		for user in demo_online:
				st.markdown(f"""
				<div style='display:flex;align-items:center;background:rgba(255,255,255,0.92);border-radius:14px;padding:10px 12px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);'>
					<img src='{user['img']}' width='54' height='54' style='border-radius:50%;margin-right:14px;border:2px solid #ff3399;'>
					<div>
						<b style='font-size:1.1em;color:#ff3399'>{user['username']}</b> <span style='color:#2ecc40'>🟢 Online</span>
					</div>
				</div>
				""", unsafe_allow_html=True)


if st.session_state.mode == "Login":
	st.subheader("Logg inn")
	# Nullstill inputfelter hvis man nettopp har registrert
	if "login_user" not in st.session_state:
		st.session_state["login_user"] = ""
	if "login_pass" not in st.session_state:
		st.session_state["login_pass"] = ""
	login_username = st.text_input("Brukernavn", key="login_user")
	login_password = st.text_input("Passord", type="password", key="login_pass")
	if st.button("Logg inn"):
		user = next((u for u in users if u['username'] == login_username and u['password'] == login_password), None)
		if user:
			st.session_state.logged_in = True
			st.session_state.user = user
			st.success(f"Velkommen, {login_username}!")
			st.session_state["login_user"] = ""
			st.session_state["login_pass"] = ""
			st.rerun()
		else:
			st.error("Feil brukernavn eller passord.")


if st.session_state.logged_in and st.session_state.user:
	st.sidebar.write(f"Innlogget som: {st.session_state.user['username']}")
	# Simuler betaling/oppgradering
	if not st.session_state.user.get('is_paid', False):
		if st.sidebar.button("🔒 Oppgrader til betalende (demo)"):
			st.session_state.user['is_paid'] = True
			st.success("Du er nå betalende medlem og har tilgang til felles chat!")
			st.rerun()
	# Tabs for alle brukere
	tab_labels = ["Matcher", "Online nå", "Chat", "AI-assistent"]
	if st.session_state.user.get('is_paid', False):
		tab_labels.insert(3, "Felles Chat")
	tabs = st.tabs(tab_labels)

	tab_idx = 0
	with tabs[tab_idx]:  # Matcher
		st.header("Dine matcher")
		matches = find_matches(st.session_state.user)
		if matches:
			for m in matches:
				st.markdown(f"""
				<div style='display:flex;align-items:center;background:rgba(255,255,255,0.85);border-radius:14px;padding:10px 12px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);'>
				  <img src='https://api.dicebear.com/7.x/adventurer/svg?seed={m['username']}' width='54' height='54' style='border-radius:50%;margin-right:14px;border:2px solid #a259c6;'>
				  <div>
					<b style='font-size:1.1em;color:#a259c6'>{m['username']}</b> <span style='color:#888'>({m['age']} år)</span><br>
					<span style='font-size:0.98em;'>{m['bio']}</span>
				  </div>
				</div>
				""", unsafe_allow_html=True)
				if st.button(f"Match med {m['username']}", key=f"match_{m['username']}"):
					st.session_state.user['matches'].append(m['username'])
					m['matches'].append(st.session_state.user['username'])
					st.success(f"Du har matchet med {m['username']}!")
		else:
			st.info("Ingen matcher funnet ennå.")

	tab_idx += 1
	with tabs[tab_idx]:  # Online nå
		st.header("Online nå 🟢")
		demo_online = [
			{"username": "PrideAlex", "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=facearea&w=128&q=80&facepad=2"},
			{"username": "RainbowSara", "img": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=facearea&w=128&q=80&facepad=2"},
			{"username": "QueerChris", "img": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=facearea&w=128&q=80&facepad=2"}
		]
		for user in demo_online:
			st.markdown(f"""
			<div style='display:flex;align-items:center;background:rgba(255,255,255,0.92);border-radius:14px;padding:10px 12px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);'>
			  <img src='{user['img']}' width='54' height='54' style='border-radius:50%;margin-right:14px;border:2px solid #ff3399;'>
			  <div>
				<b style='font-size:1.1em;color:#ff3399'>{user['username']}</b> <span style='color:#2ecc40'>🟢 Online</span>
			  </div>
			</div>
			""", unsafe_allow_html=True)

	tab_idx += 1
	with tabs[tab_idx]:  # Chat med matcher
		st.header("Chat med matcher")
		if st.session_state.user['matches']:
			chat_partner = st.selectbox("Velg match for chat", st.session_state.user['matches'])
			chat_history = get_chat(st.session_state.user['username'], chat_partner)
			for c in chat_history:
				st.write(f"{c['sender']}: {c['message']}")
			msg = st.text_input("Skriv melding")
			if st.button("Send"):
				send_message(st.session_state.user['username'], chat_partner, msg)
				st.rerun()
		else:
			st.info("Du har ingen matcher å chatte med.")

	# Felles chat kun for betalende brukere
	if st.session_state.user.get('is_paid', False):
		tab_idx += 1
		with tabs[tab_idx]:
			st.header("Felles Chat (kun for betalende)")
			group_history = get_group_chat()
			for c in group_history:
				st.write(f"{c['sender']}: {c['message']}")
			group_msg = st.text_input("Skriv melding til felles chat")
			if st.button("Send til felles chat"):
				send_group_message(st.session_state.user['username'], group_msg)
				st.rerun()

	tab_idx = len(tabs) - 1
	with tabs[tab_idx]:  # AI-assistent
		st.header("AI-assistent")
		question = st.text_input("Spør AI-assistenten om dating, sikkerhet, tips osv.")
		if st.button("Spør AI"):
			response = ai_assistant_response(question)
			st.write(response)

	if st.button("Logg ut"):
		st.session_state.logged_in = False
		st.session_state.user = None
		st.rerun()
