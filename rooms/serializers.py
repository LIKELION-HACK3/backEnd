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


# -------- Swagger 응답 전용 Serializer들 --------
class _RoomTypeStatSerializer(serializers.Serializer):
    room_type = serializers.CharField(allow_null=True, required=False)
    count = serializers.IntegerField()


class _RegionStatSerializer(serializers.Serializer):
    region = serializers.CharField()
    count = serializers.IntegerField()


class _SearchOptionsSerializer(serializers.Serializer):
    room_types = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    regions = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class RoomStatsResponseSerializer(serializers.Serializer):
    total_rooms = serializers.IntegerField()
    room_type_stats = _RoomTypeStatSerializer(many=True)
    region_stats = _RegionStatSerializer(many=True)
    search_options = _SearchOptionsSerializer()


class _FiltersAppliedSerializer(serializers.Serializer):
    search_query = serializers.BooleanField()
    room_type = serializers.BooleanField()


class RoomSearchResponseSerializer(serializers.Serializer):
    rooms = RoomSerializer(many=True)
    total_count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    search_query = serializers.CharField(allow_blank=True)
    room_type = serializers.CharField(allow_blank=True)
    filters_applied = _FiltersAppliedSerializer()


class ImportRoomsResponseSerializer(serializers.Serializer):
    created = serializers.IntegerField()
    updated = serializers.IntegerField()
    rooms = RoomSerializer(many=True)


