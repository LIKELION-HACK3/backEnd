from django.contrib import admin
from .models import NewsArticle, NewsSource

admin.site.register(NewsArticle)
admin.site.register(NewsSource)