from django.urls import path
from . import views

urlpatterns = [
    path("sitters/", views.sitter_list, name="sitter-list"),
    path("sitters/<int:pk>/", views.sitter_detail, name="sitter-detail"),
    path("pets/", views.pet_list_create, name="pet-list-create"),
    path("bookings/", views.booking_list_create, name="booking-list-create"),
    path("bookings/<int:pk>/", views.booking_update_status, name="booking-update-status"),
]
