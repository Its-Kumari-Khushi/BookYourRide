from django.contrib import admin
from .models import Booking, Driver, Pricing



@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'pickup',
        'drop_location',
        'trip_type',
        'cab_type',
        'fare',
        'status',
        'payment_method',
        'payment_status',
    )

    list_filter = (
        'status',
        'trip_type',
        'cab_type',
        'payment_method',
        'payment_status',
    )

    search_fields = (
        'customer_name',
        'pickup',
        'drop_location',
    )

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'mobile_number',
        'vehicle_type',
        'vehicle_number',
        'is_verified',
        'is_available',
    )

    list_filter = ('vehicle_type', 'is_verified', 'is_available')
    search_fields = ('full_name', 'mobile_number', 'vehicle_number')


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = (
        'cab_type',
        'one_way_rate',
        'round_trip_rate',
        'is_active',
    )

    list_filter = ('cab_type', 'is_active')