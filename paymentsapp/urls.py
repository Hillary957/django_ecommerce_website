from django.urls import path
from . import views
from django.views.generic import TemplateView 

urlpatterns = [
    path('mpesa/service/<int:service_id>/', views.mpesa, name='mpesa_service'),
    path('mpesa/course/<int:courses_id>/', views.mpesa, name='mpesa_course'),

    path('paypal/service/<int:service_id>/', views.paypal, name='paypal_service'),
    path('paypal/course/<int:courses_id>/', views.paypal, name='paypal_course'),


    path('payment_checkout/<int:transaction_id>/', views.payment_checkout, name='payment_checkout'),

    path('create_payment/service/<int:service_id>/', views.create_payment, name='create_service_payment'),
    path('create_payment/course/<int:courses_id>/', views.create_payment, name='create_course_payment'),

    path('process_payment/<int:transaction_id>/', views.process_payment, name='process_payment'),
    path('execute_payment/', views.execute_payment, name='execute_payment'),

    path('payment_success/', TemplateView.as_view(template_name="payment_success.html"), name='payment_success'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
]
