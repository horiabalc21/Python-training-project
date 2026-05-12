from django.db import models
from django.contrib.auth.models import User

class SitterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    years_experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} — {self.city}"
    
class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class SitterService(models.Model):
    sitter = models.ForeignKey(
        SitterProfile,
        on_delete=models.CASCADE,
        related_name="services"
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ("sitter", "service")

    def __str__(self):
        return f"{self.sitter.user.first_name} — {self.service.name} (${self.price_per_day}/day)"
    
class Pet(models.Model):
    SPECIES_CHOICES = [
        ("dog", "Dog"),
        ("cat", "Cat"),
        ("bird", "Bird"),
        ("other", "Other"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pets"
    )
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"
    
class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    sitter_service = models.ForeignKey(
        SitterService,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    pets = models.ManyToManyField(
        Pet,
        related_name="bookings"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def num_days(self):
        days = (self.end_date - self.start_date).days
        return days if days > 0 else 1

    @property
    def total_price(self):
        return self.sitter_service.price_per_day * self.num_days

    def __str__(self):
        return f"Booking #{self.id} — {self.owner.username}"

