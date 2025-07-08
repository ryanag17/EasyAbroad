from fastapi import APIRouter, Request
import stripe

router = APIRouter()

stripe.api_key = "***REMOVED***51RihYQQKocCiGQPZa5BdlzfskhW6hNJ40lVu5v6Sl5jwp3WeLKYizArkMwSDwCtiUKxvg2dmZQxvSlu44AnSoYTJ00HErlduUp"

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
