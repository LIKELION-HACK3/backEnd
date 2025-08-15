from rest_framework import serializers
from .models import AIComparisonReport
from rooms.serializers import RoomSerializer

class AIComparisonReportSerializer(serializers.ModelSerializer):
    room_a = RoomSerializer(read_only=True)
    room_b = RoomSerializer(read_only=True)
    room_a_id = serializers.IntegerField(write_only=True)
    room_b_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = AIComparisonReport
        fields = [
            'id', 'room_a', 'room_b', 'room_a_id', 'room_b_id',
            'comparison_criteria', 'analysis_summary', 'detailed_comparison',
            'recommendation', 'reasoning', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'analysis_summary', 'detailed_comparison', 'recommendation', 'reasoning', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        room_a_id = attrs.get('room_a_id')
        room_b_id = attrs.get('room_b_id')
        
        if room_a_id == room_b_id:
            raise serializers.ValidationError("같은 방을 비교할 수 없습니다.")
        
        return attrs

class AIComparisonRequestSerializer(serializers.Serializer):
    """AI 비교 분석 요청을 위한 시리얼라이저"""
    room_a_id = serializers.IntegerField(help_text="비교할 첫 번째 방 ID")
    room_b_id = serializers.IntegerField(help_text="비교할 두 번째 방 ID")
    comparison_criteria = serializers.JSONField(
        default=dict,
        help_text="비교 기준 (예: {'price_weight': 0.4, 'location_weight': 0.3, 'area_weight': 0.3})"
    )
    user_preferences = serializers.CharField(
        max_length=500,
        required=False,
        help_text="사용자 선호사항 (예: '가격이 중요하고, 교통편이 좋았으면 좋겠어요')"
    )
