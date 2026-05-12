from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import SitterProfile, Pet, Booking
from .serializers import (
    SitterProfileSerializer,
    PetSerializer,
    BookingSerializer,
)


# ---------- Sitters (public) ----------

@api_view(["GET"])
@permission_classes([AllowAny])
def sitter_list(request):
    """GET /api/sitters/  —  filter by ?city= and/or ?service="""
    qs = SitterProfile.objects.select_related("user").prefetch_related(
        "services__service"
    )

    city = request.query_params.get("city")
    if city:
        qs = qs.filter(city__iexact=city)

    service = request.query_params.get("service")
    if service:
        qs = qs.filter(services__service__name__iexact=service)

    max_price = request.query_params.get("max_price")
    if max_price:
        qs = qs.filter(services__price_per_day__lte=max_price)

    qs = qs.distinct()
    serializer = SitterProfileSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def sitter_detail(request, pk):
    """GET /api/sitters/<id>/"""
    try:
        sitter = SitterProfile.objects.select_related("user").prefetch_related(
            "services__service"
        ).get(pk=pk)
    except SitterProfile.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SitterProfileSerializer(sitter)
    return Response(serializer.data)


# ---------- Pets (auth required, own only) ----------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def pet_list_create(request):
    """
    GET  /api/pets/  —  list current user's pets
    POST /api/pets/  —  add a pet (owner auto-set)
    """
    if request.method == "GET":
        pets = Pet.objects.filter(owner=request.user)
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data)

    serializer = PetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(owner=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------- Bookings (auth required, own only) ----------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def booking_list_create(request):
    """
    GET  /api/bookings/  —  list current user's bookings
    POST /api/bookings/  —  create a booking (owner auto-set)
    """
    if request.method == "GET":
        bookings = Booking.objects.filter(owner=request.user).select_related(
            "sitter_service__service", "sitter_service__sitter__user"
        ).prefetch_related("pets")
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    serializer = BookingSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save(owner=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def booking_update_status(request, pk):
    """PATCH /api/bookings/<id>/  —  sitter can confirm/cancel"""
    try:
        booking = Booking.objects.select_related(
            "sitter_service__sitter__user"
        ).get(pk=pk)
    except Booking.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    # Only the sitter or the booking owner may update status
    is_sitter = booking.sitter_service.sitter.user == request.user
    is_owner = booking.owner == request.user
    if not (is_sitter or is_owner):
        return Response(
            {"detail": "You do not have permission to update this booking."},
            status=status.HTTP_403_FORBIDDEN,
        )

    new_status = request.data.get("status")
    valid_statuses = [c[0] for c in Booking.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response(
            {"status": f"Must be one of {valid_statuses}."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    booking.status = new_status
    booking.save(update_fields=["status"])
    serializer = BookingSerializer(booking)
    return Response(serializer.data)
