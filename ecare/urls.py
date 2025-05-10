"""
URL configuration for ecare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hospital.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('signup/', SignUp, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('shopmedicine/', shopmedicine, name='shopmedicine'),
    path('medicine_details/<int:medicine_id>/', medicine_details, name='medicine_details'),
    path('appointments/', appointments, name='appointments'),
    path('doctor/<int:doctor_id>/', doctor_details, name='doctor_details'),
    path('book_appointment/<int:schedule_id>/', book_appointment, name='book_appointment'),
    path('appointment_confirmation/<int:appointment_id>/', appointment_confirmation, name='appointment_confirmation'),
    path('hospital_details/<int:hospital_id>/', hospital_details, name='hospital_details'),
    path('user_profile/', user_profile, name='user_profile'),
    path('cart/', cart, name='cart'),  
    path('cart/add/<int:medicine_id>/', add_to_cart, name='add_to_cart'),  
    path('cart/remove/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'), 
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('cart/increase/<int:cart_item_id>/', increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:cart_item_id>/', decrease_quantity, name='decrease_quantity'),
    path('checkout/', checkout, name='checkout'),
    path('order_confirmation/<str:order_id>/', order_confirmation, name='order_confirmation'),
    path('manage_orders/', manage_orders, name='manage_orders'),
    path('lab-tests/', lab_test_view, name='lab_tests'),
    path('lab-bookings/', lab_booking_list, name='lab_booking_list'),
    path('emergency-ambulance/', emergency_ambulance, name='emergency_ambulance'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()