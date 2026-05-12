from rest_framework import serializers
# from django.contrib.auth.models import User
from .models import SitterProfile, Service, SitterService, Pet, Booking


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "description"]


class SitterServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = SitterService
        fields = ["id", "service", "price_per_day"]


class SitterProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    services = SitterServiceSerializer(many=True, read_only=True)

    class Meta:
        model = SitterProfile
        fields = [
            "id", "username", "first_name", "last_name",
            "bio", "city", "years_experience", "services",
        ]


class PetSerializer(serializers.ModelSerializer):
    species_display = serializers.CharField(source="get_species_display", read_only=True)

    class Meta:
        model = Pet
        fields = ["id", "name", "species", "species_display", "breed", "age"]
        # owner is auto-set from request.user


class BookingSerializer(serializers.ModelSerializer):
    num_days = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "sitter_service", "pets", "start_date", "end_date",
            "status", "notes", "created_at", "num_days", "total_price",
        ]
        read_only_fields = ["status", "created_at"]

    def validate(self, data):
        # end_date must be after start_date
        if data["end_date"] <= data["start_date"]:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        # pets must belong to the booking owner
        request = self.context["request"]
        for pet in data.get("pets", []):
            if pet.owner_id != request.user.id:
                raise serializers.ValidationError(
                    {"pets": f"Pet '{pet.name}' does not belong to you."}
                )

        return data
