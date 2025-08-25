from django.urls import path
from .views import (
    NewsArticleListView,
    PostListView, PostDetailView,
    CommentListCreateView,
    PostLikeToggleView, CommentLikeToggleView,
    PostReportView, CommentReportView, CommentDeleteView,
    NotificationUnreadListView, NotificationMarkReadView,
)

app_name = "community"

urlpatterns = [
    path("news/", NewsArticleListView.as_view(), name="news_list"),
    path("posts/", PostListView.as_view(), name="post_list"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:post_id>/comments/", CommentListCreateView.as_view(), name="comment_list_create"),
    path("posts/<int:post_id>/like/", PostLikeToggleView.as_view(), name="post_like_toggle"),
    path("comments/<int:comment_id>/like/", CommentLikeToggleView.as_view(), name="comment_like_toggle"),
    path("posts/<int:post_id>/report/", PostReportView.as_view(), name="post_report"),
    path("comments/<int:comment_id>/report/", CommentReportView.as_view(), name="comment_report"),
    path("comments/<int:comment_id>/", CommentDeleteView.as_view(), name="comment_delete"),
    path("notifications/unread/", NotificationUnreadListView.as_view(), name="notifications_unread"),
    path("notifications/read/", NotificationMarkReadView.as_view(), name="notifications_mark_read"),
]

