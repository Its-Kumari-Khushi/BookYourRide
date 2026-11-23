
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('booking/', views.booking, name='booking'),

    path('my-bookings/', views.my_bookings, name='my_bookings'),

    path('register/', views.register, name='register'),

    path(
        'driver-register/',
        views.driver_register,
        name='driver_register'
    ),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='core/login.html',
            next_page='home'
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='home'),
        name='logout'
    ),

    path(
        'cancel-booking/<int:booking_id>/',
        views.cancel_booking,
        name='cancel_booking'
    ),

    path('dashboard/', views.dashboard, name='dashboard'),

    path(
        'edit-booking/<int:booking_id>/',
        views.edit_booking,
        name='edit_booking'
    ),
    path(
    'driver-dashboard/',
    views.driver_dashboard,
    name='driver_dashboard'
),
path(
    'update-booking-status/<int:booking_id>/',
    views.update_booking_status,
    name='update_booking_status'
),

path(
    'toggle-driver-availability/',
    views.toggle_driver_availability,
    name='toggle_driver_availability'
),

]


