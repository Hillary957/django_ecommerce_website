from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMessage, send_mail
from .models import OTP
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from django.utils import timezone
from datetime import timedelta
from .models import Profile  
from decouple import config
import logging
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
logger = logging.getLogger(__name__)
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password


#  User Registration View
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        # Validation checks
        if not first_name or not last_name or not email or not password or not phone_number:
            messages.error(request, 'All fields are required!')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return render(request, 'register.html')
        
        if Profile.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "This phone number is already registered.")
            return redirect('register')

        # Create user 
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_active = False  # Require OTP verification before activation
        user.save()

        # Create Profile for storing phone number
        Profile.objects.create(user=user, phone_number=phone_number)

        # Send OTP
        try:
            send_otp(user, email, phone_number)
        except Exception as e:
            messages.error(request, f'Failed to send OTP: {e}')
            return render(request, 'register.html')

        messages.success(request, 'Registration successful! Please check your email or phone for the OTP.')
        
        #  Redirect to verify_otp with email in query string
        return redirect(f"{reverse('verify_otp')}?email={email}")

    return render(request, 'register.html')



# Otp verification
def send_otp(user, email, force_resend=False):
    from django.utils.crypto import get_random_string

    try:
        otp_obj = OTP.objects.get(email=email)
        if otp_obj.expires_at < timezone.now() or force_resend:
            otp_code = get_random_string(6, allowed_chars='1234567890')
            otp_obj.otp = otp_code
            otp_obj.expires_at = timezone.now() + timedelta(minutes=5)
            otp_obj.attempts = 0
            otp_obj.save()
        else:
            otp_code = otp_obj.otp
    except OTP.DoesNotExist:
        otp_code = get_random_string(6, allowed_chars='1234567890')
        OTP.objects.create(user=user, email=email, otp=otp_code, expires_at=timezone.now() + timedelta(minutes=5))

    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP is {otp_code}. It expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )




def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        try:
            otp_obj = OTP.objects.get(email=email)
        except OTP.DoesNotExist:
            messages.error(request, "OTP not found.")
            return redirect('register')

        if timezone.now() > otp_obj.expires_at:
            messages.error(request, "OTP expired.")
            return redirect(f"{reverse('verify_otp')}?email={email}")

        if otp != otp_obj.otp:
            otp_obj.attempts += 1
            otp_obj.save()
            messages.error(request, "Invalid OTP.")
            return redirect(f"{reverse('verify_otp')}?email={email}")

        # OTP is valid
        otp_obj.verified = True
        otp_obj.save()

        # Activate the user
        try:
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('register')

        messages.success(request, "OTP verified successfully! You can now log in.")
        return redirect('login')

    #  GET request — render form with email
    email = request.GET.get('email')
    if not email:
        messages.error(request, "Email is missing.")
        return redirect('register')
    return render(request, 'verify_otp.html', {'email': email})




def resend_otp(request):
    email = request.GET.get('email')

    if not email:
        messages.error(request, "Email address is required.")
        return redirect('register')

    otp = get_random_string(length=6, allowed_chars='1234567890')
    expires_at = timezone.now() + timedelta(minutes=5)

    otp_record, _ = OTP.objects.update_or_create(
        email=email,
        defaults={'otp': otp, 'expires_at': expires_at, 'attempts': 0, 'verified': False}
    )

    send_mail(
        subject='Your OTP Code',
        message=f'Your OTP code is: {otp}. It expires in 5 minutes.',
        from_email='noreply@yourdomain.com',
        recipient_list=[email],
        fail_silently=False,
    )

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect(f"{reverse('verify_otp')}?email={email}")






def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()  
        password = request.POST.get('password', '').strip()

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return render(request, 'login.html')

        user = authenticate(request, username=email, password=password)  # Use `username=email` because Django uses `username`

        if user is not None:
            login(request,user)
            messages.success(request, "Login successful!")
            return redirect('courses')  
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


# reset password
def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account with that email exists.')
            return redirect('reset_password')

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = request.build_absolute_uri(
            reverse('new_password', kwargs={'uidb64': uid, 'token': token})
        )

        subject = 'Password Reset Request'
        message = f"Hi {user.first_name},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, ignore this email."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        messages.success(request, 'We sent you a password reset link via email.')
        return redirect('login')

    return render(request, 'reset_password.html')

def new_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect(request.path)

            user.password = make_password(password)
            user.save()
            messages.success(request, "Password reset successful! You can now log in.")
            return redirect('login')

        return render(request, 'new_password.html', {'validlink': True})
    else:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('reset_password')