import json
import os

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
PROFILE_DIR = os.path.join(BASE_PATH, "user_configs")

FREE_USES = 3  # You can tweak this if needed

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
    return {}

def save_user_profile(email, profile):
    path = get_user_config_path(email)
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)

def increment_usage(email):
    profile = load_user_profile(email)
    
    # Track usage
    usage = profile.get("usage_count", 0)
    profile["usage_count"] = usage + 1

    # Deduct credit if applicable
    if profile.get("credit_balance", 0) > 0:
        profile["credit_balance"] -= 1

    save_user_profile(email, profile)

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

def can_generate_application(profile):
    if profile.get("subscription_status") == "pro":
        return True
    if profile.get("usage_count", 0) < FREE_USES:
        return True
    if profile.get("credit_balance", 0) > 0:
        return True
    return False

def increment_paid_applications(email, credits=1):
    profile = load_user_profile(email)
    profile["credit_balance"] = profile.get("credit_balance", 0) + credits
    save_user_profile(email, profile)
