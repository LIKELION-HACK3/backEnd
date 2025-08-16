from django.urls import path
from .views import BookmarkListView, BookmarkToggleView

app_name="bookmarks"

urlpatterns = [
    path("", BookmarkListView.as_view(), name="bookmark-list"),
    path("<int:room_id>/toggle/", BookmarkToggleView.as_view(), name="bookmark-toggle"),
]