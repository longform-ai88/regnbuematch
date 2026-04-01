import os
import json
from flask import Flask, request, jsonify
import stripe

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
stripe.api_key = STRIPE_SECRET_KEY

app = Flask(__name__)

USERS_FILE = "users.json"
PAID_EMAILS_FILE = "paid_emails.json"

def load_json_file(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json_file(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

def save_paid_email(email):
    if not email:
        return
    paid_emails = load_json_file(PAID_EMAILS_FILE, [])
    if email not in paid_emails:
        paid_emails.append(email)
        save_json_file(PAID_EMAILS_FILE, paid_emails)

# Hjelpefunksjon for å oppdatere bruker som har betalt
def mark_user_paid(email):
    save_paid_email(email)
    if not os.path.exists(USERS_FILE):
        return False

    users = load_json_file(USERS_FILE, [])
    updated = False
    for user in users:
        if user.get("email") == email:
            user["is_paid"] = True
            updated = True
    if updated:
        save_json_file(USERS_FILE, users)
    return updated

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
        return jsonify({"error": "Missing Stripe environment variables"}), 500

    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Håndter checkout.session.completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email")
        if customer_email:
            mark_user_paid(customer_email)
    return "", 200

if __name__ == "__main__":
    app.run(port=4242)
