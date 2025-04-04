import stripe
import paypalrestsdk
from django.conf import settings
from django.urls import reverse
from decimal import Decimal

class PaymentService:
    @staticmethod
    def setup_stripe_session(request, cart_items, cart_total):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Create line items for Stripe
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.beat.title,
                    'description': f'Beat by {item.beat.producer.username}',
                    'images': [item.beat.get_cover_image_url()],
                },
                'unit_amount': int(float(item.beat.price) * 100),  # Convert to cents
            },
            'quantity': 1,
        } for item in cart_items]

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse(settings.PAYMENT_SUCCESS_URL)),
            cancel_url=request.build_absolute_uri(reverse(settings.PAYMENT_CANCEL_URL)),
            metadata={
                'cart_id': str(cart_items[0].cart.id),
                'user_id': str(request.user.id)
            }
        )
        
        return {
            'session_id': session.id,
            'public_key': settings.STRIPE_PUBLIC_KEY
        }

    @staticmethod
    def setup_paypal_payment(request, cart_items, cart_total):
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })

        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse(settings.PAYMENT_SUCCESS_URL)),
                "cancel_url": request.build_absolute_uri(reverse(settings.PAYMENT_CANCEL_URL))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": item.beat.title,
                        "sku": f"beat_{item.beat.id}",
                        "price": str(item.beat.price),
                        "currency": "USD",
                        "quantity": 1
                    } for item in cart_items]
                },
                "amount": {
                    "total": str(cart_total),
                    "currency": "USD"
                },
                "description": "WavHaven Beats Purchase"
            }]
        })

        if payment.create():
            # Extract approval URL
            for link in payment.links:
                if link.rel == "approval_url":
                    return {
                        'approval_url': link.href,
                        'payment_id': payment.id
                    }
        else:
            raise Exception(payment.error) 