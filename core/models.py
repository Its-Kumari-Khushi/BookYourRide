
from django.db import models
from django.conf import settings


class Booking(models.Model):

    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Accepted', 'Accepted'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    TRIP_TYPE_CHOICES = [
        ('One-way', 'One-way'),
        ('Round-trip', 'Round-trip'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    driver = models.ForeignKey(
        'Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )

    customer_name = models.CharField(max_length=100)
    pickup = models.CharField(max_length=200)
    drop_location = models.CharField(max_length=200)

    trip_type = models.CharField(
        max_length=20,
        choices=TRIP_TYPE_CHOICES,
        default='One-way'
    )

    travel_date = models.DateField()
    travel_time = models.TimeField(null=True, blank=True)

    return_date = models.DateField(
        null=True,
        blank=True
    )

    passengers = models.PositiveIntegerField(default=1)

    cab_type = models.CharField(max_length=50)

    # UPDATED DISTANCE FIELD
    distance = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    # UPDATED FARE FIELD
    fare = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Confirmed'
    )

    payment_method = models.CharField(
        max_length=50,
        default='Cash on Pickup'
    )

    payment_status = models.CharField(
        max_length=20,
        default='Pending'
    )

    def __str__(self):
        return self.customer_name


# DRIVER MODEL

class Driver(models.Model):

    VEHICLE_CHOICES = [
        ('Hatchback', 'Hatchback'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()

    license_number = models.CharField(
        max_length=30,
        unique=True
    )

    vehicle_number = models.CharField(
        max_length=20,
        unique=True
    )

    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_CHOICES
    )

    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


# CAB PRICING MODEL

class Pricing(models.Model):

    CAB_CHOICES = [
        ('Hatchback', 'Hatchback'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
    ]

    cab_type = models.CharField(
        max_length=20,
        choices=CAB_CHOICES,
        unique=True
    )

    one_way_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    round_trip_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.cab_type
