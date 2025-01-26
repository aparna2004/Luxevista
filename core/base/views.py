from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

from  django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *


def home(request):
    return render(request, "base/index.html")


def registerCustomer(request):
    form = CustomerCreationForm()
    if request.method == "POST":
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.name.lower()
            user.save()
            login(request, user)
            return redirect("personal_details")

    return render(request, "base/register_customer.html", {"form": form})


def additionalDetails(request):
    if request.method == "POST":
        phone_no = request.POST.get("phone_no")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        preference = request.POST.get("pref")

        user = User.objects.get(pk=request.user.id)

        user.phoneNumber = phone_no
        user.dob = dob
        user.gender = gender
        user.preference = preference
        try:
            user.save()
        except:
            messages.error(request, "An error occured!")
        return redirect("home")
    return render(request, "base/additional_details.html")


def loginUser(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        mail = request.POST.get("email")
        passwd = request.POST.get("password")

        try:
            user = User.objects.get(email=mail)
        except:
            messages.error(request, "Invalid user!")

        user = authenticate(request, email=mail, password=passwd)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Incorrect username or password")
    return render(request, "base/login.html")


def logoutUser(request):
    logout(request)
    return redirect("home")


@login_required(login_url="login")
def book(request):
    hotels = Hotel.objects.all().order_by("-rating")
    context = {"hotels": hotels}
    return render(request, "base/select_hotel.html", context)


def calculate_bill_amount(booking):
    room = booking.room
    booking_date = booking.booked_time

    # Retrieve room price details
    try:
        room_price = RoomPrice.objects.get(room=room)
    except :
        return None
    
    # Determine if the booking date falls on a weekday or a weekend
    total_amount = 0
    current_date = booking.check_in
    d = 0
    while current_date <= booking.check_out:
        d+=1
        # Determine if the current night is a weekend night excluding the first night
        if current_date.weekday() in [5, 6]:
            total_amount += (room_price.base + room_price.weekend)
        else:
            total_amount += room_price.base

        # Increment current date
        current_date += timedelta(days=1)

    # Determine if the booking date falls within the seasonal period
    is_seasonal = False  # You need to implement logic to determine this based on your requirements

    # Calculate the total amount

    if is_seasonal:
        total_amount += room_price.seasonal

    return total_amount


@login_required(login_url="login")
def bookRoom(request, pk):
    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        num_occupants = int(request.POST.get("num"))
        room_type = request.POST.get("room_type")
        hotel_id = pk  # Assuming you have the hotel ID in the form

        # Convert from_date and to_date strings to datetime objects
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.strptime(to_date, "%Y-%m-%d")

        if from_date < datetime.now() or to_date < datetime.now():
            raise ValidationError("Dates cannot be in the past")

        booking_duration = (
            to_date - from_date
        ).days + 1  # Add 1 to include the last day

        # Validate booking duration to be between 1 and 10 nights
        if booking_duration < 1 or booking_duration > 10:
            raise ValidationError("Booking duration must be between 1 and 10 nights")

        # Retrieve rooms of the specified type in the selected hotel
        rooms_of_type = Room.objects.filter(hotel=hotel_id, type=room_type)

        # Filter reservations that overlap with the given date range
        overlapping_reservations = Reservation.objects.filter(
            Q(check_in__lte=to_date, check_out__gte=from_date)
            | Q(check_in__gte=from_date, check_out__lte=to_date)
            | Q(check_in__lte=from_date, check_out__gte=to_date),
            room__in=rooms_of_type,
        )

        # Exclude rooms with overlapping reservations
        available_rooms = rooms_of_type.exclude(
            id__in=overlapping_reservations.values_list("room_id", flat=True)
        )

        # Filter available rooms based on the number of occupants
        # available_rooms = available_rooms.filter(number_of_beds__gte=num_occupants)

        allocated_rooms = []
        remaining_occupants = num_occupants
        money = 0 
        for room in available_rooms:
            if remaining_occupants <= 0:
                break
            occupants_in_room = min(remaining_occupants, room.number_of_beds)
            reservation = Reservation.objects.create(
                room=room,
                customer=request.user,
                check_in=from_date,
                check_out=to_date,
                number_of_occupants=occupants_in_room,
                advance=0,  # You may adjust this based on your business logic
                booked_from=from_date,
                booked_till=to_date,
                method="",  # You may set payment method based on your business logic
                payment_status="",  # You may set payment status based on your business logic
            )
            # Create bill for the reservation
            bill_amount = calculate_bill_amount(
                reservation
            )  # You need to define this function
            if not bill_amount :
                messages.error(request, "Required type of rooms are full. Try booking another room type!")
                return render(request, "base/book_room.html")
            
            money += bill_amount
            Bill.objects.create(
                booking=reservation,
                customer=request.user,
                amount=bill_amount,
                status="PENDING",  # You can set the status as needed
            )
            allocated_rooms.append(room)
            remaining_occupants -= occupants_in_room

        if remaining_occupants > 0:
            return render(request, "base/no_available_rooms.html")

        # Redirect or render a success message
        return render(
            request, "base/success.html", {"allocated_rooms": allocated_rooms,"amount" : money }
        )

    # If GET request, render the search form
    return render(request, "base/book_room.html")


@login_required(login_url="login")
def listReservations(request):
    reservations = Reservation.objects.filter(customer = request.user, isCancelled = False)
    return render(request, "base/list_reservations.html",{"reservations" : reservations})


@login_required(login_url="login")
def cancel(request, pk):
    if request.method == "POST":
        reservation = Reservation.objects.get(id = pk)
        reservation.isCancelled = True
        reservation.save()
        b = Bill.objects.get(booking = reservation)
        b.status = "CANCELLED"
        b.save()
        return redirect('home')
    return render(request, "base/cancel.html")


def aboutView(request):
    return render(request, "base/about.html")
