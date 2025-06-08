from django.shortcuts import render, redirect
from paymentsapp.models import Transaction
from ecommerceapp.models import Services
import logging
from django.contrib import messages
from django.urls import reverse
from ecommerceapp.models import Services,Courses
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EmailForm
from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages




# Create your views here.

def home(request):
    transactions = Transaction.objects.all()
    services = Services.objects.all() 
    courses = Courses.objects.all()  

    # If you need a single service
    service = Services.objects.first()
    course = Courses.objects.first()    

    return render(request, 'home.html', {
        'transactions': transactions,
        'services': services,  
        'courses': courses, 
        'service_id': service.id if service else None, 
        'course_id': course.id if course else None,  
    })



def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')





logger = logging.getLogger(__name__)


def courses(request):
    courses = Courses.objects.all()
    services = Services.objects.all()  # Get all services
    course_payments = []

    for course in courses:
        payment_url = reverse('create_course_payment', args=[course.id])
        course_payments.append({
            'course': course,
            'payment_url': payment_url
        })

    return render(request, 'courses.html', {'course_payments': course_payments, 'courses': courses,'services': services })



def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        client_email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and client_email and subject and message:
            email_subject = f"New message from {name}: {subject}"
            email_body = f"Name: {name}\nEmail: {client_email}\n\nMessage:\n{message}"

            email_message = EmailMessage(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                reply_to=[client_email]
            )

            try:
                email_message.send()
                messages.success(request, "Your message was sent successfully!")
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")
        else:
            messages.error(request, "Please fill in all fields.")

        return redirect('contact')

    return render(request, 'contact.html')




def testimonial(request):
    return render(request, 'testimonial.html')

def error404(request):
    return render(request, '404.html')

def pricing(request):
    return render(request, 'price.html')


    
