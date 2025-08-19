from django.urls import path
from .views import NewsArticleListView

urlpatterns = [
    path("news/", NewsArticleListView.as_view(), name="news_list"),
]

