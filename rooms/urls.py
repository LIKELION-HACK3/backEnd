from django.urls import path
from .views import (
    RoomListCreateView,
    RoomDetailView,
    ImportRoomsView,
    ReviewListCreateView,
    RoomSearchView,
    RoomStatsView,
)

urlpatterns = [
    path('', RoomListCreateView.as_view(), name='room-list'),
    path('search/', RoomSearchView.as_view(), name='room-search'),
    path('stats/', RoomStatsView.as_view(), name='room-stats'),
    path('<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('import/', ImportRoomsView.as_view(), name='room-import'),
    path('<int:room_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
]