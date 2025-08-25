from django.db import models
from django.conf import settings
from django.db.models import F

#=== 뉴스 ===
class NewsSource(models.Model):
  name=models.CharField(max_length=100, unique=True, db_index=True)
  homepage=models.URLField(blank=True)
  rss_url=models.URLField(blank=True)
  enabled=models.BooleanField(default=True)

  def __str__(self):
    return self.name 

class Category(models.TextChoices):
    NEWS = "뉴스", "뉴스"
    POLICY = "정책", "정책"
    LIFE = "생활", "생활"
    INFO = "정보", "정보"

class NewsArticle(models.Model):
  source=models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name="articles")
  title=models.CharField(max_length=500)
  url=models.URLField(unique=True)
  published_at=models.DateTimeField(null=True, blank=True)
  thumbnail=models.URLField(blank=True)
  category=models.CharField(max_length=10, choices=Category.choices, default=Category.NEWS)
  created_at=models.DateTimeField(auto_now_add=True)

  class Meta:
    indexes=[
      models.Index(fields=["-published_at"]),
      models.Index(fields=["source", "-published_at"]),
      models.Index(fields=["category"]),
    ]
    ordering=["-published_at", "-id"]

  def __str__(self):
    return self.title

#=== 함께해요 ===
class Region(models.TextChoices):
  IMUN="이문동", "이문동"
  HOEGI="회기동", "회기동"
  HWIGYUNG="휘경동", "휘경동"
  CHEONGLYANGRI="청량리동", "청량리동"
  JEAGI="제기동", "제기동"
  JEONNONG="전농동", "전농동"
  JANGAN="장안동", "장안동"
  DABSHIBLI="답십리동", "답십리동"
  YONGSHIN="용신동", "용신동"

class Category(models.TextChoices):
  LOOKING="구해요", "구해요"
  LOCAL="동네소식", "동네소식"
  TIPS="자취꿀팁", "자취꿀팁"
  ETC="기타", "기타"

class CommunityPost(models.Model):
  author=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_posts")
  region=models.CharField(max_length=10, choices=Region.choices, db_index=True)
  category=models.CharField(max_length=10, choices=Category.choices, db_index=True)
  title=models.CharField(max_length=200, db_index=True)
  content=models.TextField()
  views=models.PositiveBigIntegerField(default=0, db_index=True)
  like_count=models.PositiveBigIntegerField(default=0, db_index=True)
  comment_count=models.PositiveIntegerField(default=0, db_index=True)
  created_at=models.DateTimeField(auto_now_add=True, db_index=True)
  updated_at=models.DateTimeField(auto_now=True)

  class Meta:
    indexes=[
      models.Index(fields=["region", "-created_at"]),
      models.Index(fields=["category", "-created_at"]),
      models.Index(fields=["-views"]),
      models.Index(fields=["-like_count"]),
    ]
    ordering=["-created_at"]

  def __str__(self):
    return f"[{self.region}/{self.category}] {self.title}"
  
  def bump_views(self, by:int=1):
    CommunityPost.objects.filter(pk=self.pk).update(views=F("views") + by)
    self.refresh_from_db(fields=["views"])

  def bump_like_count(self, by:int=1):
    CommunityPost.objects.filter(pk=self.pk).update(like_count=F("like_count") + by)
    self.refresh_from_db(fields=["like_count"])

  def bump_comment_count(self, by: int=1):
    CommunityPost.objects.filter(pk=self.pk).update(comment_count=F("comment_count") + by)
    self.refresh_from_db(fields=["comment_count"])

  
class PostLike(models.Model):
  user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_likes")
  post=models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="likes")
  created_at=models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together=("user", "post")
    indexes=[
      models.Index(fields=["user", "post"]),
    ]

class PostReport(models.Model):
  user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reports")
  post=models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="reports")
  reason=models.TextField()
  created_at=models.DateTimeField(auto_now_add=True)

  class Meta:
    indexes=[models.Index(fields=["post", "created_at"])]
  
class Comment(models.Model):
  post=models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="comments")
  author=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
  parent=models.ForeignKey("self",on_delete=models.CASCADE, null=True, blank=True, db_index=True, related_name="replies")
  content=models.TextField()
  created_at=models.DateTimeField(auto_now_add=True, db_index=True)

  class Meta:
    indexes=[
      models.Index(fields=["post", "-created_at"]),
      models.Index(fields=["parent", "-created_at"])
    ]
    ordering=["created_at"]

class CommentLike(models.Model):
  user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_likes")
  comment=models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
  created_at=models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together=("user", "comment")
    indexes=[models.Index(fields=["user", "comment"])]

class CommentReport(models.Model):
  user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_reports")
  comment=models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_reports")
  reason=models.TextField()
  created_at=models.DateTimeField(auto_now_add=True)

  class Meta:
    indexes=[models.Index(fields=["comment", "created_at"])]

#=== 알림 ===
class NotificationType(models.TextChoices):
  COMMENT_ON_POST="comment_post", "게시글에 새로운 댓글"
  REPLY_ON_COMMENT="reply_comment", "내 댓글에 대댓글"

class Notification(models.Model):
  recipient=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
  actor=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="notification_actors")
  type=models.CharField(max_length=20, choices=NotificationType.choices)
  post=models.ForeignKey(CommunityPost, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
  comment=models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
  message=models.CharField(max_length=255, blank=True)
  is_read=models.BooleanField(default=False, db_index=True)
  created_at=models.DateTimeField(auto_now_add=True, db_index=True)

  class Meta:
    indexes=[
      models.Index(fields=["recipient", "is_read", "-created_at"]),
    ]
    ordering=["-created_at", "-id"]