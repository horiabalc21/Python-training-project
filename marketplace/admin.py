from django.contrib import admin
from .models import SitterProfile, Service, SitterService, Pet, Booking


@admin.register(SitterProfile)
class SitterProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "years_experience")
    search_fields = ("user__username", "user__first_name", "user__last_name", "city")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(SitterService)
class SitterServiceAdmin(admin.ModelAdmin):
    list_display = ("sitter", "service", "price_per_day")
    search_fields = ("sitter__user__username", "service__name")


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "species", "breed", "age", "owner")
    search_fields = ("name", "breed", "owner__username")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "sitter_service", "start_date", "end_date", "status", "created_at")
    search_fields = ("owner__username", "sitter_service__sitter__user__username")
    list_filter = ("status",)
