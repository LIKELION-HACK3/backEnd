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
    # 피그마 카테고리(벌레)와 내부 필드(rating_clean) 매핑
    rating_bug = serializers.IntegerField(source='rating_clean', required=False, allow_null=True)

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
            # 내부 호환을 위해 rating_clean도 유지하되, 외부에서는 rating_bug 사용 가능
            "rating_clean",
            "rating_bug",
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


# ----- 리뷰 평점 통계 응답 -----
class ReviewListItemSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    rating_bug = serializers.IntegerField(source='rating_clean', required=False, allow_null=True)

    class Meta:
        model = Review
        fields = (
            'id', 'username', 'content', 'created_at',
            'rating_safety', 'rating_noise', 'rating_light', 'rating_traffic', 'rating_clean', 'rating_bug'
        )
        read_only_fields = fields

class _CategoryAveragesSerializer(serializers.Serializer):
    safety = serializers.FloatField(allow_null=True)
    noise = serializers.FloatField(allow_null=True)
    light = serializers.FloatField(allow_null=True)
    traffic = serializers.FloatField(allow_null=True)
    bug = serializers.FloatField(allow_null=True)
    overall = serializers.FloatField(allow_null=True)


class _StarDistributionSerializer(serializers.Serializer):
    # 1~5점 분포. 키는 문자열 유지(프론트 정렬 편의)
    _1 = serializers.IntegerField(source='1')
    _2 = serializers.IntegerField(source='2')
    _3 = serializers.IntegerField(source='3')
    _4 = serializers.IntegerField(source='4')
    _5 = serializers.IntegerField(source='5')


class _CategoryDistributionsSerializer(serializers.Serializer):
    safety = _StarDistributionSerializer()
    noise = _StarDistributionSerializer()
    light = _StarDistributionSerializer()
    traffic = _StarDistributionSerializer()
    bug = _StarDistributionSerializer()


class RoomRatingStatsResponseSerializer(serializers.Serializer):
    reviews_count = serializers.IntegerField()
    averages = _CategoryAveragesSerializer()
    distributions = _CategoryDistributionsSerializer()
    reviews = ReviewListItemSerializer(many=True)


