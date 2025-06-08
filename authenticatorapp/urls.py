from django.urls import path,include
from . import views
from django.views.decorators.csrf import csrf_exempt



urlpatterns = [
    path('register/',views.register ,name= 'register' ),
    path('login/',csrf_exempt(views.login_view) ,name= 'login' ),
    path('reset_password/',views.reset_password ,name= 'reset_password' ),
    path('new_password/<uidb64>/<token>/',views.new_password ,name= 'new_password' ),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    
   
]