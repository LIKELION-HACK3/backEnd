from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from rooms.models import Room
from .models import Bookmark
from .serializers import BookmarkSerializer

class BookmarkPagination(PageNumberPagination):
  page_size=6
  page_size_query_param="page_size"
  max_page_size=10

class BookmarkListView(generics.ListAPIView):
  permission_classes=[IsAuthenticated]
  serializer_class=BookmarkSerializer
  pagination_class=BookmarkPagination

  def get_queryset(self):
    return (
      Bookmark.objects
      .filter(user=self.request.user)
      .select_related("room")
      .prefetch_related("room__images")
      .order_by("-created_at", "-id")
    )

class BookmarkToggleView(APIView):
  permission_classes=[IsAuthenticated]

  def post(self, request, room_id:int):
    room=get_object_or_404(Room, pk=room_id)
    bookmark, created=Bookmark.objects.get_or_create(user=request.user, room=room)
    if created:
      return Response({"bookmarked": True, "room_id": room.id},
                      status=status.HTTP_201_CREATED,)
    bookmark.delete()
    return Response(
      {"bookmarked": False, "room_id":room.id},
      status=status.HTTP_200_OK
    )