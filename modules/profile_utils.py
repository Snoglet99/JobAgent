import json
import os

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
PROFILE_DIR = os.path.join(BASE_PATH, "user_configs")

FREE_USES = 3
PAID_CREDITS_PER_PURCHASE = 10

def get_user_config_path(email):
    safe_email = email.replace("@", "_at_").replace(".", "_dot_")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    return os.path.join(PROFILE_DIR, f"{safe_email}.json")

def get_history_path(email):
    safe_email = email.replace("@", "_at_").replace(".", "_dot_")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    return os.path.join(PROFILE_DIR, f"{safe_email}_history.json")

def load_user_profile(email):
    path = get_user_config_path(email)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "usage_count": 0,
        "credit_balance": 0,
        "pending_payment": False,
        "tone": "Default"
    }

def save_user_profile(email, profile):
    path = get_user_config_path(email)
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)

def ensure_profile_keys(profile):
    defaults = {
        "usage_count": 0,
        "credit_balance": 0,
        "pending_payment": False,
        "tone": "Default"
    }
    for key, value in defaults.items():
        if key not in profile:
            profile[key] = value
    return profile

def can_generate_application(profile):
    return profile.get("usage_count", 0) < FREE_USES or profile.get("credit_balance", 0) > 0

def increment_usage(email):
    profile = load_user_profile(email)

    if profile.get("usage_count", 0) < FREE_USES:
        profile["usage_count"] += 1
    else:
        profile["credit_balance"] = max(profile.get("credit_balance", 0) - 1, 0)
        profile["usage_count"] += 1  # Still track total usage

    save_user_profile(email, profile)

def increment_paid_applications(email, credits=PAID_CREDITS_PER_PURCHASE):
    profile = load_user_profile(email)
    profile["credit_balance"] = profile.get("credit_balance", 0) + credits
    profile["pending_payment"] = False
    save_user_profile(email, profile)

def mark_payment_pending(email):
    profile = load_user_profile(email)
    profile["pending_payment"] = True
    save_user_profile(email, profile)

def is_payment_pending(profile):
    return profile.get("pending_payment", False)

def save_application_to_history(email, job_title, company, content):
    path = get_history_path(email)
    entry = {
        "job_title": job_title,
        "company": company,
        "content": content
    }
    if os.path.exists(path):
        with open(path, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.insert(0, entry)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)
