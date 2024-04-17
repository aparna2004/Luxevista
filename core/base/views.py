from datetime import datetime
from  django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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


def book(request):
    hotels = Hotel.objects.all().order_by("-rating")
    context = {"hotels": hotels}
    return render(request, "base/select_hotel.html", context)


# def bookRoom(request, pk):
#     rooms = Room.objects.filter(hotel=pk)
#     # fill here
#     # select * from rooms where ... <join?> ;
#     if request.method == "POST":
#         from_date = request.POST.get("from_date")
#         to_date = request.POST.get("to")
#         type = request.POST.get("room_type")
#         num = request.POST.get("num")

#         rooms = Room.objects.filter(hotel=pk) # select * from room where hotel = pk, from_date

#     return render(request, "base/book_room.html", {"rooms": rooms})


def bookRoom(request,pk):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        num_occupants = request.POST.get('num')
        room_type = request.POST.get('room_type')
        hotel_id = pk # Assuming you have the hotel ID in the form
        print(room_type)
        # Convert from_date and to_date strings to datetime objects
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

        # Retrieve rooms of the specified type in the selected hotel
        rooms_of_type = Room.objects.filter(hotel=hotel_id, type=room_type)

        # Filter reservations that overlap with the given date range
        overlapping_reservations = Reservation.objects.filter(
            Q(check_in__lte=to_date, check_out__gte=from_date)
            | Q(check_in__gte=from_date, check_out__lte=to_date)
            | Q(check_in__lte=from_date, check_out__gte=to_date),
            room__in=rooms_of_type
        )

        print("overlap= ",overlapping_reservations)
        # Exclude rooms with overlapping reservations
        available_rooms = rooms_of_type.exclude(id__in=overlapping_reservations.values_list('room_id', flat=True))
        print("Available = ", available_rooms)
        # Filter available rooms based on the number of occupants
        available_rooms = available_rooms.filter(number_of_beds__gte=num_occupants)

        if available_rooms.exists():
            # Allocate the first available room (you may adjust the allocation logic)
            room = available_rooms.first()
            Reservation.objects.create(
                room=room,
                customer=request.user,
                check_in=from_date,
                check_out=to_date,
                number_of_occupants=num_occupants,
                advance=0,  # You may adjust this based on your business logic
                booked_from=timezone.now(),
                booked_till=timezone.now(),
                method='',  # You may set payment method based on your business logic
                payment_status=''  # You may set payment status based on your business logic
            )
            # Redirect or render a success message
            return render(request, 'base/success.html', {'room': room})
        else:
            # If no available room found, render a message
            return render(request, 'base/no_available_rooms.html')

    # If GET request, render the search form
    return render(request, 'base/book_room.html')
