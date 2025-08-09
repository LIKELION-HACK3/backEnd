from rest_framework import serializers
from .models import Room, RoomImage, Review


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ("id", "image_url", "ordering")
        read_only_fields = ("id",)


class RoomSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = (
            "id",
            "title",
            "room_type",
            "deposit",
            "monthly_fee",
            "maintenance_cost",
            "supply_area",
            "real_area",
            "floor",
            "contract_type",
            "address",
            "latitude",
            "longitude",
            "external_id",
            "images",
        )
        read_only_fields = ("id",)


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "room",
            "rating_safety",
            "rating_noise",
            "rating_light",
            "rating_traffic",
            "rating_clean",
            "content",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "user")


