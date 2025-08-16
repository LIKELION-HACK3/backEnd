from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
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

@extend_schema(
  tags=['bookmarks'],
  summary='북마크 목록 조회',
  description='로그인한 사용자의 북마크 목록을 페이지네이션하여 반환합니다.',
  responses={
    200: OpenApiResponse(
      response=BookmarkSerializer(many=True),
      description='북마크 목록',
    )
  }
)
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

@extend_schema(
  tags=['bookmarks'],
  summary='북마크 토글',
  description='지정한 방을 북마크에 추가하거나 제거합니다.',
  responses={
    201: OpenApiResponse(
      description='북마크 추가됨',
      examples=[OpenApiExample('created', value={'bookmarked': True, 'room_id': 1}, response_only=True, status_codes=['201'])]
    ),
    200: OpenApiResponse(
      description='북마크 해제됨',
      examples=[OpenApiExample('deleted', value={'bookmarked': False, 'room_id': 1}, response_only=True, status_codes=['200'])]
    ),
    404: OpenApiResponse(description='방을 찾을 수 없습니다'),
  }
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