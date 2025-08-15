from django.db import models
from django.conf import settings
from rooms.models import Room

class AIComparisonReport(models.Model):
    """
    AI가 두 방을 비교 분석한 리포트 모델
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_reports')
    room_a = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='comparison_reports_as_a')
    room_b = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='comparison_reports_as_b')
    
    # 비교 기준 (사용자가 선택한 비교 요소들)
    comparison_criteria = models.JSONField(default=dict, help_text="비교 기준 (예: 가격, 위치, 면적 등)")
    
    # AI 분석 결과
    analysis_summary = models.TextField(help_text="AI 분석 요약")
    detailed_comparison = models.JSONField(default=dict, help_text="상세 비교 분석")
    recommendation = models.CharField(max_length=50, help_text="AI 추천 (room_a 또는 room_b)")
    reasoning = models.TextField(help_text="추천 이유")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'room_a', 'room_b']  # 같은 사용자가 같은 두 방을 중복 비교 방지
    
    def __str__(self):
        return f"AI Comparison: {self.room_a.title} vs {self.room_b.title} by {self.user.username}"
    
    @property
    def rooms(self):
        """비교 대상 방들을 리스트로 반환"""
        return [self.room_a, self.room_b]
    
    @property
    def winner(self):
        """AI가 추천한 방 반환"""
        if self.recommendation == 'room_a':
            return self.room_a
        elif self.recommendation == 'room_b':
            return self.room_b
        return None













