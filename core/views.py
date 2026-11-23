from django.views.decorators.http import require_POST
from decimal import Decimal, InvalidOperation
from django.utils.dateparse import parse_date, parse_time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Booking, Driver, Pricing
from .forms import DriverRegistrationForm


def home(request):
    return render(request, 'core/home.html')

def register(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                'Registration successful!'
            )

            return redirect('home')

        else:
            messages.error(
                request,
                'Please correct the errors below.'
            )

    else:
        form = UserCreationForm()

    return render(
        request,
        'core/register.html',
        {'form': form}
    )


def driver_register(request):

    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            Driver.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                mobile_number=form.cleaned_data['mobile_number'],
                email=form.cleaned_data['email'],
                license_number=form.cleaned_data['license_number'],
                vehicle_number=form.cleaned_data['vehicle_number'],
                vehicle_type=form.cleaned_data['vehicle_type'],
                is_verified=False,
                is_available=False
            )

            messages.success(
                request,
                'Driver registration successful! Wait for admin verification.'
            )

            return redirect('login')

        else:
            messages.error(
                request,
                'Please correct the errors below.'
            )

    else:
        form = DriverRegistrationForm()

    return render(
        request,
        'core/driver_register.html',
        {'form': form}
    )




@login_required
def booking(request):

    if request.method == 'POST':

        name = request.POST.get('customer_name', '').strip()
        pickup = request.POST.get('pickup', '').strip()
        drop = request.POST.get('drop', '').strip()

        date = request.POST.get('travel_date')
        time = request.POST.get('travel_time') or None

        trip_type = request.POST.get('trip_type')
        return_date_value = request.POST.get('return_date')

        passengers = request.POST.get('passengers', 1)
        cab = request.POST.get('cab_type')
        distance = request.POST.get('distance')

        payment_method = request.POST.get(
            'payment_method',
            'Cash on Pickup'
        )

        # CHECK REQUIRED FIELDS

        if not all([name, pickup, drop, date, cab, distance]):
            messages.error(
                request,
                'Please fill all required fields.'
            )
            return redirect('booking')

        # VALIDATE TRIP TYPE

        if trip_type not in ['One-way', 'Round-trip']:
            messages.error(request, 'Please select a valid trip type.')
            return redirect('booking')

        # VALIDATE DATES

        travel_date = parse_date(date)

        if not travel_date:
            messages.error(request, 'Please enter a valid journey date.')
            return redirect('booking')

        return_date = None

        if trip_type == 'Round-trip':

            if not return_date_value:
                messages.error(
                    request,
                    'Please select your return date.'
                )
                return redirect('booking')

            return_date = parse_date(return_date_value)

            if not return_date:
                messages.error(
                    request,
                    'Please enter a valid return date.'
                )
                return redirect('booking')

            if return_date < travel_date:
                messages.error(
                    request,
                    'Return date cannot be before journey date.'
                )
                return redirect('booking')

        # VALIDATE DISTANCE AND PASSENGERS

        try:
            distance = int(distance)
            passengers = int(passengers)

            if distance <= 0 or passengers <= 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                'Enter valid distance and passengers.'
            )
            return redirect('booking')

            # FETCH CAB PRICING FROM DATABASE

        try:
            pricing = Pricing.objects.get(
                cab_type=cab,
                is_active=True
            )

        except Pricing.DoesNotExist:
            messages.error(
                request,
                'Pricing is not available for this cab. Please contact us.'
            )
            return redirect('booking')

        # CALCULATE FARE

        if trip_type == 'One-way':
            fare = distance * pricing.one_way_rate

        else:
            fare = distance * pricing.round_trip_rate

        # FIND AVAILABLE VERIFIED DRIVER

        driver = Driver.objects.filter(
            vehicle_type=cab,
            is_verified=True,
            is_available=True
        ).order_by('id').first()

        # CREATE BOOKING

        new_booking = Booking.objects.create(
            user=request.user,
            driver=driver,
            customer_name=name,
            pickup=pickup,
            drop_location=drop,

            trip_type=trip_type,
            travel_date=travel_date,
            travel_time=time,
            return_date=return_date,

            passengers=passengers,
            cab_type=cab,
            distance=distance,
            fare=fare,

            payment_method=payment_method,
            payment_status='Pending',
            status='Confirmed'
        )

               # UPDATE DRIVER AVAILABILITY

        if driver:
            driver.is_available = False
            driver.save()

            messages.success(
                request,
                'Your cab has been booked and a driver has been assigned!'
            )

        else:
            messages.success(
                request,
                'Your booking is confirmed. Driver will be assigned soon.'
            )

        return redirect('my_bookings')

    pricings = Pricing.objects.filter(is_active=True)

    return render(
        request,
        'core/booking.html',
        {
            'pricings': pricings
        }
    )


@login_required
def my_bookings(request):

    from django.db.models import Q

    bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-id')

    search = request.GET.get('search', '')
    selected_cab = request.GET.get('cab_type', '')
    selected_status = request.GET.get('status', '')

    if search:
        bookings = bookings.filter(
            Q(pickup__icontains=search) |
            Q(drop_location__icontains=search)
        )

    if selected_cab:
        bookings = bookings.filter(cab_type=selected_cab)

    if selected_status:
        bookings = bookings.filter(status=selected_status)

    return render(
        request,
        'core/my_bookings.html',
        {
            'bookings': bookings,
            'search': search,
            'selected_cab': selected_cab,
            'selected_status': selected_status,
        }
    )



@login_required
def dashboard(request):

    bookings = Booking.objects.filter(user=request.user)

    total_bookings = bookings.count()
    active_bookings = bookings.filter(
        status='Confirmed'
    ).count()

    cancelled_bookings = bookings.filter(
        status='Cancelled'
    ).count()

    return render(request, 'core/dashboard.html', {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'cancelled_bookings': cancelled_bookings,
    })


@login_required
@require_POST
def cancel_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.status == 'Cancelled':
        messages.error(request, 'Booking is already cancelled.')
        return redirect('my_bookings')

    booking.status = 'Cancelled'
    booking.save(update_fields=['status'])

    messages.success(
        request,
        'Booking cancelled successfully.'
    )

    return redirect('my_bookings')




@login_required
def edit_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.status == 'Cancelled':
        messages.error(request, 'Cancelled bookings cannot be edited.')
        return redirect('my_bookings')

    if request.method == 'POST':


        pickup = request.POST.get('pickup', '').strip()
        drop_location = request.POST.get('drop', '').strip()

        trip_type = request.POST.get('trip_type')
        travel_date = parse_date(request.POST.get('travel_date', ''))
        return_date = parse_date(request.POST.get('return_date', ''))
        travel_time = parse_time(request.POST.get('travel_time', ''))

        cab_type = request.POST.get('cab_type')

        try:
            passengers = int(request.POST.get('passengers', 1))
        except (ValueError, TypeError):
            passengers = 0

        if not pickup or not drop_location:
            messages.error(request, 'Please enter pickup and drop locations.')

        elif trip_type not in ['One-way', 'Round-trip']:
            messages.error(request, 'Invalid trip type.')

        elif not travel_date:
            messages.error(request, 'Please select a valid travel date.')

        elif trip_type == 'Round-trip' and not return_date:
            messages.error(request, 'Please select a return date.')

        elif trip_type == 'Round-trip' and return_date < travel_date:
            messages.error(request, 'Return date cannot be before travel date.')

        elif passengers < 1:
            messages.error(request, 'Passengers must be at least 1.')

        elif cab_type not in ['Hatchback', 'Sedan', 'SUV']:
            messages.error(request, 'Please select a valid cab type.')

        else:

            try:
                pricing = Pricing.objects.get(
                    cab_type=cab_type,
                    is_active=True
                )

                if trip_type == 'One-way':
                    fare = booking.distance * pricing.one_way_rate
                else:
                    fare = booking.distance * pricing.round_trip_rate

                booking.pickup = pickup
                booking.drop_location = drop_location
                booking.trip_type = trip_type
                booking.travel_date = travel_date
                booking.travel_time = travel_time
                booking.passengers = passengers
                booking.cab_type = cab_type
                booking.fare = fare

                if trip_type == 'Round-trip':
                    booking.return_date = return_date
                else:
                    booking.return_date = None

                booking.save()

                messages.success(request, 'Booking updated successfully.')
                return redirect('my_bookings')

            except Pricing.DoesNotExist:
                messages.error(
                    request,
                    'Pricing not found for this cab. Please contact support.'
                )

    return render(
        request,
        'core/edit_booking.html',
        {'booking': booking}
    )

@login_required
def driver_dashboard(request):

    try:
        driver = request.user.driver
    except Driver.DoesNotExist:
        messages.error(request, 'You are not registered as a driver.')
        return redirect('home')

    bookings = Booking.objects.filter(
        driver=driver
    ).order_by('-id')

    return render(
        request,
        'core/driver_dashboard.html',
        {
            'driver': driver,
            'bookings': bookings
        }
    )

@login_required
def update_booking_status(request, booking_id):

    try:
        driver = request.user.driver
    except Driver.DoesNotExist:
        messages.error(request, 'Only registered drivers can update bookings.')
        return redirect('home')

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        driver=driver
    )

    if request.method == 'POST':

        new_status = request.POST.get('status')

        allowed_statuses = [
            'Accepted',
            'In Progress',
            'Completed'
        ]

        if new_status in allowed_statuses:

            booking.status = new_status
            booking.save()

            messages.success(
                request,
                'Booking status updated successfully!'
            )

        else:
            messages.error(request, 'Invalid booking status.')

    return redirect('driver_dashboard')


@login_required
def toggle_driver_availability(request):

    try:
        driver = request.user.driver
    except Driver.DoesNotExist:
        messages.error(request, "You are not registered as a driver.")
        return redirect('home')

    if request.method == 'POST':

        if driver.is_verified:

            driver.is_available = not driver.is_available
            driver.save()

            messages.success(
                request,
                "Your availability has been updated successfully!"
            )

        else:
            messages.error(
                request,
                "Your account is not verified by admin yet."
            )

    return redirect('driver_dashboard')


