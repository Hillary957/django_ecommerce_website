
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecommerceapp.urls')),
    path('paymentsapp/', include('paymentsapp.urls')),
    path('authenticatorapp/', include('authenticatorapp.urls')),
    path('', include('paypal.standard.ipn.urls')),

]
