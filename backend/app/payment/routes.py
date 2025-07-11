from fastapi import APIRouter, Request
import stripe
from app.config import settings

# Get Stripe secret key from environment
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/payment")

@router.post("/create-payment-intent")
async def create_payment_intent(request: Request):
    data = await request.json()
    payment_method_id = data.get("payment_method")
    amount = data.get("amount")

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="eur",
            payment_method=payment_method_id,
            payment_method_types=["card"],
            confirmation_method="manual",
            confirm=True,
        )
        return {"client_secret": intent.client_secret}
    except Exception as e:
        return {"error": str(e)}