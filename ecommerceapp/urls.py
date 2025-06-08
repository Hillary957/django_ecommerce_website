from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('',views.home ,name= 'home' ),
    path('about/',views.about ,name= 'about' ),
    path('contact/',views.contact ,name= 'contact' ),
    path('courses/',views.courses ,name= 'courses' ),
    path('testimonial/',views.testimonial,name= 'testimonial' ),
    path('error404/',views.error404 ,name= 'error404' ),
    path('pricing/',views.pricing ,name= 'pricing' ),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)