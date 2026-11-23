
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class DriverRegistrationForm(UserCreationForm):

    email = forms.EmailField()
    full_name = forms.CharField(max_length=100)
    mobile_number = forms.CharField(max_length=15)
    license_number = forms.CharField(max_length=30)
    vehicle_number = forms.CharField(max_length=20)

    VEHICLE_CHOICES = [
        ('Hatchback', 'Hatchback'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
    ]

    vehicle_type = forms.ChoiceField(
        choices=VEHICLE_CHOICES
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
