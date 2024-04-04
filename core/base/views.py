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
            user.username = ""
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


def bookRoom(request, pk):
    rooms = Room.objects.filter(hotel=pk)
    return render(request, "base/book_room.html", {"rooms": rooms})
