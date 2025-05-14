#!/usr/bin/env python3
# Payment gateway detection module
# Author: Created for @amkuush

import re
import logging
from typing import List
from bs4 import BeautifulSoup

# Configure logger
logger = logging.getLogger(__name__)

# Payment gateway patterns to check - enhanced for better detection
PAYMENT_GATEWAY_PATTERNS = {
    "PayPal": [
        r"paypal\.com",
        r"PayPal",
        r"paypal",
        r"xoon[_-]?checkout",
        r"pp[_-]?checkout",
        r"paypal[_-]?button",
        r"paypal[_-]?sdk",
        r"paypal[_-]?checkout",
        r"braintree/paypal",
        r"paypal[_-]?bn",
        r"paypal_payment",
        r"paypalCheckout",
        r"data-paypal",
        r"paypal-button-container",
        r"paypal-smart-payment-buttons"
    ],
    "Stripe": [
        r"stripe\.com",
        r"Stripe",
        r"stripe-js",
        r"stripeJsV3",
        r"stripe\.js",
        r"stripe[_-]?button",
        r"stripe[_-]?checkout",
        r"data-stripe",
        r"stripe-button",
        r"stripe-account",
        r"stripePublishableKey",
        r"stripeToken",
        r"stripe_elements",
        r"stripe\.elements",
        r"stripeBillingDetails",
        r"stripeSessions",
        r"stripe_payment_intent",
        r"stripe-payment-element",
        r"stripe-checkout",
        r"data-stripe-publishable-key",
        r"pk_live_",
        r"pk_test_",
        r"data-secret=\"pi_",
        r"card-element",
        r"StripePaymentElement",
        r"StripeElements"
    ],
    "Braintree": [
        r"braintree-web",
        r"braintree",
        r"braintreegateway",
        r"braintree[_-]?token",
        r"braintree[_-]?client",
        r"braintree[_-]?sdk",
        r"braintree[_-]?merchant",
        r"client_token",
        r"dropin-container",
        r"braintree-hosted-fields",
        r"braintree-dropin",
        r"braintree\.setup"
    ],
    "Square": [
        r"squareup\.com",
        r"square\.js",
        r"SqPaymentForm",
        r"square-web-sdk",
        r"square[_-]?sdk",
        r"square-payment-form",
        r"sqPaymentForm",
        r"square[_-]?payment",
        r"square-checkout",
        r"squarejs",
        r"squarewebpayments",
        r"data-square",
        r"square-web-payments-sdk",
        r"SquarePaymentFlow",
        r"squareSdkConfig",
        r"card-container-sq",
        r"sq-payment-form",
        r"square_sdk",
        r"square-hosted-fields",
        r"square_payments"
    ],
    "Authorize.Net": [
        r"authorize\.net",
        r"authorizenet",
        r"AcceptUI",
        r"authorize-data",
        r"authorize-checkout",
        r"auth-net",
        r"accept\.js",
        r"acceptHosted",
        r"authData",
        r"authNetPayment"
    ],
    "Adyen": [
        r"adyen\.com",
        r"adyen",
        r"checkoutSDK",
        r"adyen-checkout",
        r"adyenjs",
        r"AdyenCheckout",
        r"adyen-dropin",
        r"adyen-encrypted-data",
        r"adyen-checkout-input"
    ],
    "Klarna": [
        r"klarna\.com",
        r"klarna",
        r"klarnaCheckout",
        r"klarna-checkout",
        r"klarna-payments",
        r"klarna_payments",
        r"klarna-credit",
        r"klarnaPayments",
        r"klarna-payment-method"
    ],
    "Afterpay": [
        r"afterpay\.com",
        r"afterpay",
        r"afterpayjs",
        r"afterpay-express",
        r"afterpay-button",
        r"afterpayButton",
        r"afterpay-checkout",
        r"afterpay_button",
        r"afterpay-widget"
    ],
    "Affirm": [
        r"affirm\.com",
        r"affirm",
        r"_affirm_config",
        r"affirm-checkout",
        r"affirm-payment",
        r"affirm-as-low-as",
        r"affirm_checkout",
        r"affirmPromo",
        r"affirm-ui-components"
    ],
    "Amazon Pay": [
        r"amazon\.com/payments",
        r"amazonpayments",
        r"amazonpay",
        r"amazon-pay-button",
        r"amazon_payments",
        r"amazonPayButton",
        r"amazon-payments-widget",
        r"amazon-checkout-button"
    ],
    "Apple Pay": [
        r"apple-pay",
        r"applepay",
        r"ApplePaySession",
        r"apple-pay-button",
        r"apple-pay-setup",
        r"applePayButton",
        r"support-apple-pay",
        r"applepay-button"
    ],
    "Google Pay": [
        r"google\.com/pay",
        r"googlepay",
        r"googlepaymentsapi",
        r"google-pay-button",
        r"googlepayConfig",
        r"google-pay-js",
        r"google-pay-container",
        r"gpay"
    ],
    "Venmo": [
        r"venmo\.com",
        r"venmo",
        r"venmoWeb",
        r"venmo-button",
        r"venmo_sdk",
        r"venmoCheckout",
        r"venmo-checkout",
        r"venmo-payment"
    ],
    "Shop Pay": [
        r"shop\.app",
        r"shopifycdn",
        r"shop-pay",
        r"shopify_pay",
        r"data-shopify",
        r"shopify-payment",
        r"shopify-section-shop-pay",
        r"shopify-payment-button"
    ],
    "Checkout.com": [
        r"checkout\.com",
        r"checkoutApi",
        r"frames\.js",
        r"checkout-frames",
        r"checkout-com",
        r"checkoutToken",
        r"checkout-payment-method",
        r"checkout_token",
        r"checkout-com-frames"
    ],
    "2Checkout": [
        r"2checkout\.com",
        r"2checkout",
        r"2co\.js",
        r"2co_setup",
        r"twocheckout",
        r"2checkout_token",
        r"twocheckout-form",
        r"2co_checkout",
        r"2checkout-payment"
    ],
    "PayU": [
        r"payu\.(in|com)",
        r"PayUmoney",
        r"payumoney",
        r"payu_checkout",
        r"payu-checkout",
        r"payu-form",
        r"payuForm",
        r"payu_payment",
        r"payu-payment-method"
    ],
    "Worldpay": [
        r"worldpay\.com",
        r"worldpay",
        r"Worldpay\.",
        r"worldpay-js",
        r"worldpay-payment",
        r"worldpay_checkout",
        r"worldpay-form",
        r"worldpayToken",
        r"worldpay-payment-button"
    ],
    "Razorpay": [
        r"razorpay\.com",
        r"razorpay",
        r"Razorpay",
        r"razorpay-checkout",
        r"razorpay-payment",
        r"razorpay-button",
        r"razorpay_key",
        r"razorpay-embed",
        r"razorpay-container"
    ],
    "Skrill": [
        r"skrill\.com",
        r"skrill",
        r"skrillpayments",
        r"skrill-checkout",
        r"skrill_payment",
        r"skrill-payment-form",
        r"skrill-button",
        r"skrillPaymentForm",
        r"skrill-container"
    ],
    "Payoneer": [
        r"payoneer\.com",
        r"payoneer",
        r"Payoneer",
        r"payoneer-checkout",
        r"payoneer_payment",
        r"payoneer-button",
        r"payoneer-form",
        r"payoneer-container"
    ],
    "BlueSnap": [
        r"bluesnap\.com",
        r"bluesnap",
        r"BlueSnap",
        r"bluesnap-hosted-payment",
        r"bluesnap_checkout",
        r"bluesnap-checkout",
        r"bluesnap-form",
        r"bluesnapPaymentForm",
        r"bluesnap-payment-field"
    ],
    "Paytm": [
        r"paytm\.com",
        r"paytm",
        r"Paytm",
        r"paytm-button",
        r"paytm_payment",
        r"paytm-checkout",
        r"paytm-form",
        r"paytmChecksum",
        r"paytm-container"
    ],
    "Mollie": [
        r"mollie\.com",
        r"mollie",
        r"mollie-api",
        r"mollie-checkout",
        r"mollie_payment",
        r"mollie-payment-form",
        r"mollie-button",
        r"molliePaymentForm",
        r"mollie-container"
    ],
    "Alipay": [
        r"alipay\.com",
        r"alipay",
        r"Alipay",
        r"alipay-button",
        r"alipay_checkout",
        r"alipay-checkout",
        r"alipay-form",
        r"alipay-container"
    ],
    "WeChat Pay": [
        r"wechat\.com/pay",
        r"wechatpay",
        r"WeChatPay",
        r"wechat-pay-button",
        r"wechat_payment",
        r"wechat-checkout",
        r"wechat-pay-form",
        r"wechatPayment",
        r"wechat-pay-container"
    ],
    "Coinbase": [
        r"coinbase\.com",
        r"coinbase",
        r"coinbase-commerce",
        r"coinbase_button",
        r"coinbase-checkout",
        r"coinbase-commerce-button",
        r"coinbase-payment"
    ],
    "BitPay": [
        r"bitpay\.com",
        r"bitpay",
        r"BitPay",
        r"bitpay-button",
        r"bitpay_checkout",
        r"bitpay-checkout",
        r"bitpay-payment"
    ],
    "CashApp": [
        r"cash\.app",
        r"cashapp",
        r"cash-app",
        r"cashapp-pay",
        r"cash-app-pay",
        r"cashapp-button",
        r"cashapp_payment"
    ],
    "Zelle": [
        r"zellepay\.com",
        r"zelle",
        r"Zelle",
        r"zelle-button",
        r"zelle_payment",
        r"zelle-checkout",
        r"zelle-integration"
    ],
    "Mercado Pago": [
        r"mercadopago\.com",
        r"mercadopago",
        r"MercadoPago",
        r"mercadopago-button",
        r"mercadopago_checkout",
        r"mercadopago-checkout",
        r"mercadopago-payment"
    ],
    "Sezzle": [
        r"sezzle\.com",
        r"sezzle",
        r"Sezzle",
        r"sezzle-button",
        r"sezzle_checkout",
        r"sezzle-checkout",
        r"sezzle-widget"
    ],
    "Recurly": [
        r"recurly\.com",
        r"recurly",
        r"Recurly",
        r"recurly-element",
        r"recurly_checkout",
        r"recurly-checkout",
        r"recurly-payment"
    ],
    "Paysafe": [
        r"paysafe\.com",
        r"paysafe",
        r"Paysafe",
        r"paysafe-button",
        r"paysafe_checkout",
        r"paysafe-checkout",
        r"paysafecard"
    ]
}

def detect_payment_gateways(html_content: str, soup: BeautifulSoup) -> List[str]:
    """
    Detect payment gateways used by the website with enhanced accuracy.
    Version 2.0 - Improved detection for main domains and checkout pages
    
    Args:
        html_content: The raw HTML content
        soup: BeautifulSoup object of the parsed HTML
        
    Returns:
        List of detected payment gateway names
    """
    detected_gateways = []
    confidence_scores = {}
    
    try:
        # 1. Check standard HTML content for patterns
        for gateway, patterns in PAYMENT_GATEWAY_PATTERNS.items():
            confidence = 0
            for pattern in patterns:
                # Check raw HTML for patterns
                if re.search(pattern, html_content, re.IGNORECASE):
                    confidence += 1
                
                # Check specific elements that are more likely to contain gateway info
                for element_type in ['script', 'link', 'meta', 'div', 'form', 'input', 'button']:
                    elements = soup.find_all(element_type)
                    for element in elements:
                        # Check element attributes if it has any
                        if hasattr(element, 'attrs') and element.attrs:
                            for attr, value in element.attrs.items():
                                if isinstance(value, str):
                                    if re.search(pattern, value, re.IGNORECASE):
                                        confidence += 2  # Higher confidence for attribute matches
                                elif isinstance(value, list):
                                    joined_value = " ".join([str(v) for v in value if v])
                                    if re.search(pattern, joined_value, re.IGNORECASE):
                                        confidence += 2
                        
                        # Check element content if it has any
                        if element.string:
                            element_text = str(element.string)
                            if re.search(pattern, element_text, re.IGNORECASE):
                                confidence += 1
            
            # Calculate final confidence score
            if confidence > 0:
                confidence_scores[gateway] = confidence
        
        # 2. Deep script inspection for JavaScript variables and API keys
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                script_content = str(script.string)
                
                # Check for initialization patterns (very specific gateway signatures)
                # Stripe specific patterns in JS
                if re.search(r'Stripe\([\'\"]([a-zA-Z0-9_]+)[\'\"]', script_content) or re.search(r'pk_(test|live)_[a-zA-Z0-9]{10,}', script_content):
                    confidence_scores['Stripe'] = confidence_scores.get('Stripe', 0) + 5
                
                # PayPal specific patterns in JS
                if re.search(r'paypal\.Buttons', script_content) or re.search(r'xo\.paypal\.com', script_content):
                    confidence_scores['PayPal'] = confidence_scores.get('PayPal', 0) + 5
                
                # Square specific patterns in JS
                if re.search(r'SquarePaymentFlow', script_content) or re.search(r'SqPaymentForm', script_content):
                    confidence_scores['Square'] = confidence_scores.get('Square', 0) + 5
                
                # General API key patterns for various gateways
                for gateway in PAYMENT_GATEWAY_PATTERNS.keys():
                    gateway_lower = gateway.lower().replace(' ', '').replace('.', '')
                    if re.search(fr'{gateway_lower}_?api_?key', script_content, re.IGNORECASE):
                        confidence_scores[gateway] = confidence_scores.get(gateway, 0) + 3
        
        # 3. Form analysis for payment-specific fields
        forms = soup.find_all('form')
        for form in forms:
            # Check for credit card fields (strong indicator of payment processing)
            card_field_patterns = ['card', 'credit', 'ccnum', 'cardnumber', 'payment']
            
            has_card_fields = False
            input_fields = form.find_all('input') if hasattr(form, 'find_all') else []
            
            for input_field in input_fields:
                input_id = str(input_field.get('id', '')).lower() if hasattr(input_field, 'get') else ''
                input_name = str(input_field.get('name', '')).lower() if hasattr(input_field, 'get') else ''
                
                # Handle class attribute which could be a list
                input_class = ''
                if hasattr(input_field, 'get'):
                    class_attr = input_field.get('class', [])
                    if isinstance(class_attr, list):
                        input_class = ' '.join([str(c) for c in class_attr if c])
                    else:
                        input_class = str(class_attr).lower()
                
                for pattern in card_field_patterns:
                    if (pattern in input_id or pattern in input_name or pattern in input_class):
                        has_card_fields = True
                        break
            
            # If we found card fields, check which gateway the form might be using
            if has_card_fields:
                form_html = str(form)
                for gateway, patterns in PAYMENT_GATEWAY_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, form_html, re.IGNORECASE):
                            confidence_scores[gateway] = confidence_scores.get(gateway, 0) + 4
        
        # 4. Check for links to payment gateway domains
        links = soup.find_all('a', href=True)
        for link in links:
            if hasattr(link, 'get') and link.get('href'):
                href = str(link.get('href'))
                for gateway, patterns in PAYMENT_GATEWAY_PATTERNS.items():
                    # Only check domain patterns (containing .com, etc.)
                    domain_patterns = [p for p in patterns if '\\.' in p]
                    for pattern in domain_patterns:
                        if re.search(pattern, href, re.IGNORECASE):
                            confidence_scores[gateway] = confidence_scores.get(gateway, 0) + 2
        
        # Add gateways that meet minimum confidence threshold (avoid false positives)
        for gateway, score in confidence_scores.items():
            if score >= 1:  # Reduced threshold to improve detection rate
                detected_gateways.append(gateway)
                logger.info(f"Detected payment gateway: {gateway} with confidence score: {score}")
    
    except Exception as e:
        logger.error(f"Error detecting payment gateways: {e}")
    
    return detected_gateways