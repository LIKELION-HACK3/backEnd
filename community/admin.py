from django.contrib import admin
# community/admin.py
from django.contrib import admin
from .models import (
    Category,
    CommunityPost,
    Comment,
    PostLike,
    CommentLike,
    PostReport,
    CommentReport,
    RoommatePost,
)

admin.site.register(Category)
admin.site.register(CommunityPost)
admin.site.register(Comment)
admin.site.register(PostLike)
admin.site.register(CommentLike)
admin.site.register(PostReport)
admin.site.register(CommentReport)
admin.site.register(RoommatePost)
