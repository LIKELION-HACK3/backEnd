from django.contrib import admin
from .models import (
  NewsArticle, NewsSource,
  CommunityPost, PostLike, PostReport,
  Comment, CommentLike, CommentReport,
  )

admin.site.register(NewsArticle)
admin.site.register(NewsSource)
admin.site.register(CommunityPost)
admin.site.register(PostLike)
admin.site.register(PostReport)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(CommentReport)
