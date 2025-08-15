from django.contrib import admin
from .models import AIComparisonReport

@admin.register(AIComparisonReport)
class AIComparisonReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'room_a', 'room_b', 'recommendation', 'created_at']
    list_filter = ['recommendation', 'created_at', 'room_a__room_type', 'room_b__room_type']
    search_fields = ['user__username', 'room_a__title', 'room_b__title', 'analysis_summary']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'room_a', 'room_b', 'comparison_criteria')
        }),
        ('AI 분석 결과', {
            'fields': ('analysis_summary', 'detailed_comparison', 'recommendation', 'reasoning')
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
