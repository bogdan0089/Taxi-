import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:

    @staticmethod
    async def charge(amount: float, payment_method_id: str) -> None:
        stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency="usd",
            payment_method=payment_method_id,
            confirm=True,
        )
