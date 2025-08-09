from django.db import models
from django.conf import settings

# Create your models here.

class Room(models.Model):
    title = models.CharField(max_length=255)
    room_type = models.CharField(max_length=50, null=True, blank=True)
    deposit = models.IntegerField(null=True, blank=True)
    monthly_fee = models.IntegerField(null=True, blank=True)
    maintenance_cost = models.IntegerField(null=True, blank=True)
    supply_area = models.FloatField(null=True, blank=True)
    real_area = models.FloatField(null=True, blank=True)
    floor = models.CharField(max_length=20, null=True, blank=True)
    contract_type = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # 외부 원본의 "매물ID"를 보관하여 import 중복 방지
    external_id = models.BigIntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.room_type or '-'})"


class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image_url = models.TextField()
    ordering = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['ordering', 'id']

    def __str__(self):
        return f"{self.room_id} - {self.ordering or 0}"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="reviews")

    rating_safety = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_noise = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_light = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_traffic = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_clean = models.PositiveSmallIntegerField(null=True, blank=True)

    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Review({self.id}) R{self.room_id} U{self.user_id}"
