from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .mpesa_credentials import MpesaAccessToken, LipanaMpesaPassword
import requests
import json
from .forms import MpesaForm
from django.conf import settings
import paypalrestsdk
from django.urls import reverse
from paymentsapp.paypal_credentials import PAYPAL_SECRET, PAYPAL_CLIENT_ID
from . models import Transaction
from django.shortcuts import get_object_or_404
from ecommerceapp.models import Services, Courses
import uuid
import paypalrestsdk
import logging
from paymentsapp.models import Payment 
from decouple import config 


def mpesa(request, service_id=None, courses_id=None):
    service = get_object_or_404(Services, id=service_id) if service_id else None
    course = get_object_or_404(Courses, id=courses_id) if courses_id else None

    if request.method == 'POST':
        form = MpesaForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']

            # Get Mpesa Access Token
            access_token = MpesaAccessToken.validated_mpesa_access_token()
            if not access_token:
                return JsonResponse({"status": "error", "message": "Failed to get access token."}, status=400)

            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "BusinessShortCode": "174379",
                "Password": LipanaMpesaPassword.decode_password,
                "Timestamp": LipanaMpesaPassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": "174379",
                "PhoneNumber": phone_number,
                "CallBackURL": "https://yourdomain.com/callback/",
                "AccountReference": f"Payment for {'Service' if service else 'Course'}",
                "TransactionDesc": "Payment for service/course"
            }

            try:
                response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                mpesa_response = response.json()
            except requests.exceptions.RequestException as e:
                return JsonResponse({"status": "error", "message": "Network error occurred.", "details": str(e)}, status=500)

            if response.status_code == 200:
                return JsonResponse({
                    "status": "success",
                    "message": "Payment request sent. Check your phone.",
                    "response": mpesa_response
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Payment request failed.",
                    "response": mpesa_response
                }, status=400)
    else:
        form = MpesaForm()

    return render(request, 'mpesa.html', {
        'form': form,
        'service': service,
        'service_id': service.id if service else None,
        'course': course,
        'courses_id': course.id if course else None
    })

def paypal(request):
    return render (request, 'paypal.html')




# paypal configuration

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})



def create_payment(request, service_id=None, courses_id=None): 
    service = None
    courses = None

    if service_id:
        service = Services.objects.filter(id=service_id).first()
    elif courses_id:
        courses = Courses.objects.filter(id=courses_id).first()

    if not service and not courses:
        return JsonResponse({"status": "error", "message": "Service or Course not found."}, status=404)

    unique_checkout_id = str(uuid.uuid4())
    payment_method = request.POST.get('payment_method', 'paypal')
    mpesa_code = str(uuid.uuid4())[:10] if payment_method == 'mpesa' else None

    transaction = Transaction.objects.create(
        courses=courses,
        service=service,
        amount=service.price if service else courses.price,
        currency="USD",
        status="Pending",
        checkout_id=unique_checkout_id,
        mpesa_code=mpesa_code
    )

    request.session['transaction_id'] = transaction.id
    return redirect('payment_checkout', transaction_id=transaction.id)





def payment_checkout(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    # Retrieve related service or course
    service = transaction.service
    courses = transaction.courses  
    # Ensure the transaction has a checkout ID
    if not transaction.checkout_id:
        transaction.checkout_id = str(uuid.uuid4())
        transaction.save()

    context = {
        'transaction': transaction,
        'service': service,
        'courses': courses,
    }
    return render(request, 'checkout.html', context)





def process_payment(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    # Ensure the transaction has an associated service or course
    if not transaction.service and not transaction.courses:
        return render(request, 'payment_failed.html', {
            'error': "No service or course associated with this transaction."
        })

    # Determine service or course
    service = transaction.service
    course = transaction.courses  # (you may rename to course later for clarity)

    # Ngrok configuration
    ngrok_url = "https://3f19-102-135-172-140.ngrok-free.app"
    return_url = request.build_absolute_uri(reverse('execute_payment'))
    cancel_url = request.build_absolute_uri(reverse('payment_failed'))

    # Replace localhost with Ngrok URL for external callbacks
    for key, url in {'return_url': return_url, 'cancel_url': cancel_url}.items():
        if "127.0.0.1" in url or "localhost" in url:
            updated_url = url.replace("127.0.0.1:8000", ngrok_url).replace("localhost:8000", ngrok_url)
            if key == 'return_url':
                return_url = updated_url
            else:
                cancel_url = updated_url

    # Create PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url,
        },
        "transactions": [{
            "amount": {
                "total": str(service.price if service else course.price),
                "currency": transaction.currency,
            },
            "description": f"Payment for {service.name if service else course.name}",
        }],
    })

    # Handle payment creation
    if payment.create():
        # Redirect user to PayPal approval URL
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    else:
        return render(request, 'payment_failed.html', {'error': payment.error})



logger = logging.getLogger(__name__)

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        return render(request, 'payment_failed.html', {'error': 'Missing payment details.'})

    try:
        logger.debug(f"Fetching PayPal Payment ID: {payment_id}")

        #  Check if the payment already exists in the database
        existing_payment = Payment.objects.filter(payment_id=payment_id, status="approved").exists()
        if existing_payment:
            logger.warning("Payment already processed. Redirecting to success page.")
            return redirect('payment_success')

        payment = paypalrestsdk.Payment.find(payment_id)
        logger.debug(f"PayPal Payment Status: {payment.state}")

        #  Check if payment is already approved
        if payment.state == "approved":
            logger.warning("Payment was already executed. Redirecting to success page.")
            return redirect('payment_success')

        #  Execute the payment if it's not approved yet
        if payment.execute({"payer_id": payer_id}):
            logger.debug("Payment executed successfully!")

            #  Save the successful payment in your database
            Payment.objects.create(payment_id=payment_id, status="approved")

            return redirect('payment_success')
        else:
            logger.error(f"Payment execution failed: {payment.error}")
            return render(request, 'payment_failed.html', {'error': payment.error})

    except paypalrestsdk.ResourceNotFound as e:
        logger.error(f"Payment not found: {e}")
        return render(request, 'payment_failed.html', {'error': f"Payment not found: {str(e)}"})

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return render(request, 'payment_failed.html', {'error': f"An error occurred: {str(e)}"})



def payment_failed(request):
    return render(request, 'payment_failed.html', {'error': 'Payment was cancelled or failed.'})


def payment_success(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
     # Retrieve related service or course
    service = transaction.service
    courses = transaction.courses 

    # Ensure the transaction has a checkout ID

    context = {
        'transaction': transaction,
        'service': service,
        'courses': courses,
    }

    return render(request, 'payment_success.html', context)
