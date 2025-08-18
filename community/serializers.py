from rest_framework import serializers
from .models import NewsSource, NewsArticle

class NewsSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsSource
        fields = ("id", "name", "homepage", "rss_url", "enabled")

class NewsArticleSerializer(serializers.ModelSerializer):
    source = NewsSourceSerializer()

    class Meta:
        model = NewsArticle
        fields = (
            "id", "title", "url", "thumbnail", "category",
            "published_at", "created_at", "source"
        )
