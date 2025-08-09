from django.contrib import admin
from .models import Room, RoomImage, Review


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'room_type', 'contract_type', 'monthly_fee', 'deposit', 'external_id')
    search_fields = ('title', 'address', 'room_type', 'contract_type')
    list_filter = ('room_type', 'contract_type')


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'ordering', 'image_url')
    list_select_related = ('room',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user', 'rating_safety', 'rating_noise', 'rating_light', 'rating_traffic', 'rating_clean', 'created_at')
    list_select_related = ('room', 'user')
    search_fields = ('content',)
