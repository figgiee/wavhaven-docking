import os

# Stripe Settings
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'your_stripe_public_key')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'your_stripe_secret_key')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'your_stripe_webhook_secret')

# PayPal Settings
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', 'your_paypal_client_id')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', 'your_paypal_client_secret')
PAYPAL_MODE = 'sandbox'  # Change to 'live' for production

# Payment Gateway Settings
PAYMENT_SUCCESS_URL = 'store:payment_success'
PAYMENT_CANCEL_URL = 'store:payment_cancel'
PAYMENT_ERROR_URL = 'store:payment_error' 