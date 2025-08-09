from django.urls import path
from .views import (
    RoomListCreateView,
    RoomDetailView,
    ImportRoomsView,
    ReviewListCreateView,
)

urlpatterns = [
    path('', RoomListCreateView.as_view(), name='room-list'),
    path('<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('import/', ImportRoomsView.as_view(), name='room-import'),
    path('<int:room_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
]