import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(email):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=email,
        line_items=[{
            "price": "price_1RpgzkFydB3OobQ8EsDD5zOT",  # ✅ CORRECT ID from Stripe dashboard
            "quantity": 1,
        }],
        success_url=f"https://jobagent.streamlit.app/Application_Generator?email={email}&paid=1",
        cancel_url="https://jobagent.streamlit.app/Application_Generator",
    )
    return session.url
