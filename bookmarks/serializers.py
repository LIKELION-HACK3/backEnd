from rest_framework import serializers 
from rooms.models import Room
from .models import Bookmark

class RoomCardSerializer(serializers.ModelSerializer):
  thumbnail_url=serializers.SerializerMethodField()
  price_label=serializers.SerializerMethodField()
  maintenance_label=serializers.SerializerMethodField()

  class Meta:
    model=Room
    fields=["id", "title", "address",
            "deposit", "monthly_fee", "maintenance_cost", #백엔드용(숫자필드 그대로)
            "price_label", "maintenance_label",#UI용 라벨
            "thumbnail_url",
            ]
    
  def get_thumbnail_url(self, obj):
    first=obj.images.first()
    return first.image_url if first else None
  
  def get_price_label(self, obj):
    dep, mon= obj.deposit, obj.monthly_fee
    def fmt(n): return f"{n:,}" if n is not None else None 
    if dep is not None and mon is not None:
      return f"{fmt(dep)}/{fmt(mon)}"
    if dep is not None:
      return fmt(dep)
    if mon is not None:
      return fmt(mon)
    return None
  
  def get_maintenance_label(self, obj):
    mnt=obj.maintenance_cost
    return f"{mnt:,}" if mnt is not None else None
  

class BookmarkSerializer(serializers.ModelSerializer):
  room=RoomCardSerializer(read_only=True)
  
  class Meta:
    model = Bookmark
    fields=["id", "room", "created_at"]
    read_only_fields=fields
