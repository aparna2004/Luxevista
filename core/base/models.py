from django.db import models

# Create your models here.
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator


class Room(models.Model):
    hotel = models.ForeignKey("Hotel", null=False, on_delete=models.CASCADE)
    room_number = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{1}\d{3}$",
                message="Enter a valid registration number in the format ABC123.",
                code="invalid_registration",
            ),
        ],
    )
    is_available = models.BooleanField(default=True)

    class RoomType(models.TextChoices):
        SUITE = "SUITE", "Suite"
        DELUXE = "DELUXE", "Deluxe"
        SUPER_DELUXE = "SUPER_DELUXE", "Super_deluxe"

    type = models.CharField(choices=RoomType.choices, default=RoomType.SUITE, max_length=20)
    isAC = models.BooleanField(default=True)
    number_of_beds = models.PositiveIntegerField(_("number of beds"), default=1)

class PaymentStatus(models.TextChoices):
    PAID = "PAID", "Paid"
    PENDING = "PENDING", "Pending"
    CANCELLED = "CANCELLED", "Cancelled"


def validatePhoneNumber(value):
    if value < 1000000000 or value > 9999999999:
        raise ValidationError("Invalid phone number entered")
    else:
        return value


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = "USER", "User"
        AGENT = "AGENT", "Agent"
        STAFF = "STAFF", "Staff"
        ADMIN = "ADMIN", "Admin"

    class Gender(models.TextChoices):
        MALE = ("MALE", "Male")
        FEMALE = ("FEMALE", "Female")
        OTHER = "OTHER", "Other"

    base_role = Role.ADMIN

    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name","username")   
    name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=True)
    gender = models.CharField(
        choices=Gender.choices, default=Gender.OTHER, max_length=30
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN)
    phoneNumber = models.PositiveBigIntegerField(
        null=True,
        validators=[
            validatePhoneNumber,
        ],
    )
    dob = models.DateField(null=True)
    preference = models.CharField(choices=Room.RoomType.choices ,null=True, max_length=20)

    created_on = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # agent fields

    agency = models.CharField(max_length=50, null=True)
    commission = models.IntegerField(default=0, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name=} ,{self.email=}, {self.role=}"


class Bill(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    booking = models.ForeignKey("Reservation", on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField(default=0)
    status = models.CharField(
        choices=PaymentStatus.choices, default=PaymentStatus.PENDING , max_length=10
    )


class Hotel(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to="hotel_images/", null=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0,
        null=True,
    )
    location = models.CharField(_("location"), max_length=50)



class Service(models.Model):

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey("Reservation", on_delete=models.CASCADE)

    type = models.CharField(_("type of service"), max_length=30)
    amount = models.PositiveIntegerField(_("amount charged for the service"))
    status = models.CharField(
        choices=PaymentStatus.choices, default=PaymentStatus.PENDING, max_length=10
    )


class RoomPrice(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    base = models.PositiveIntegerField(_("Base price"))
    weekend = models.PositiveIntegerField(_("Weekend charge"))
    seasonal = models.PositiveIntegerField(_("Seasonal charge"))
    per_person = models.PositiveIntegerField(_("Per person charge"))


class Reservation(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CANCELLED = "CANCELLED", "Cancelled"
        BLOCKED = "BLOCKED", "Blocked"

    class PaymentMethod(models.TextChoices):
        UPI = "UPI", "UPI"
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()

    number_of_occupants = models.PositiveIntegerField(
        _("number of occupants"),
        validators=[MinValueValidator(1), MaxValueValidator(4)],
    )
    advance = models.PositiveIntegerField(
        _("advance amount"),
        validators=[MinValueValidator(2000)],
    )

    booked_from = models.DateTimeField()
    booked_till = models.DateTimeField()
    booked_time = models.DateTimeField(auto_now_add=True)

    isCancelled = models.BooleanField(default=False)
    method = models.CharField(choices=PaymentMethod.choices, max_length=10)
    payment_status = models.CharField(choices=PaymentStatus.choices, default=PaymentStatus.PENDING, max_length=10)