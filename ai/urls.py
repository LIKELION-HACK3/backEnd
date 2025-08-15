from django.urls import path
from . import views

urlpatterns = [
    # AI 방 비교 분석
    path('compare/', views.AIComparisonView.as_view(), name='ai-compare'),
    
    # 비교 분석 히스토리
    path('history/', views.AIComparisonHistoryView.as_view(), name='ai-history'),
    
    # 특정 리포트 상세 조회
    path('reports/<int:report_id>/', views.AIComparisonDetailView.as_view(), name='ai-report-detail'),
    
    # 북마크된 방들 조회 (비교용)
    path('bookmarked-rooms/', views.get_bookmarked_rooms_for_comparison, name='ai-bookmarked-rooms'),
]