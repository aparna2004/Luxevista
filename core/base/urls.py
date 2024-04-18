from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register_customer/", views.registerCustomer, name="register_customer"),
    path("additional_details/", views.additionalDetails, name="personal_details"),
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("book/", views.book, name="book"),
    path("hotel/<str:pk>", views.bookRoom, name="hotel"),
    path("reservations/", views.listReservations, name="list"),
    path("cancel/<str:pk>", views.cancel, name="cancel"),
    path("about/", views.aboutView, name="about"),
]
