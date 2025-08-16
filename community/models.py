from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()

class TimeStampedModel(models.Model):
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)

  class Meta:
    abstract=True

class Category(models.Model):
  name=models.CharField(max_length=50, unique=True)
  slug=models.SlugField(max_length=60, unique=True)

  def __str__(self):
    return self.name
  
class CommunityPost(TimeStampedModel):
  user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
  category=models.ForeignKey(
    Category,
    on_delete=models.SET_NULL,
    null=True, blank=True, related_name="posts"
  )
  title=models.CharField(max_length=100)
  content=models.TextField()
  image=models.ImageField(upload_to="post_images/", null=True, blank=True)
  is_active=models.BooleanField(default=True)

  class Meta:
    ordering=["-created_at"]
    indexes=[
      models.Index(fields=["title"]),
      models.Index(fields=["created_at"]),
    ]

class Comment(TimeStampedModel):
  user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
  post=models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="comments")
  content=models.TextField()
  parent=models.ForeignKey(
    "self", on_delete=models.CASCADE, 
    null=True, blank=True, related_name="replies"
  )
  is_active=models.BooleanField(default=True)

class PostLike(TimeStampedModel):
  user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
  post=models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="likes")

  class Meta:
    unique_together=("user", "post")

class CommentLike(TimeStampedModel):
  user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_likes")
  comment=models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")

  class Meta:
    unique_together = ("user", "comment")

class ReportReason(models.TextChoices):
    SPAM = "SPAM", "스팸/홍보"
    ABUSE = "ABUSE", "욕설/혐오/괴롭힘"
    ILLEGAL = "ILLEGAL", "불법/위험"
    OTHER = "OTHER", "기타"

class PostReport(TimeStampedModel):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_reports")
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=20, choices=ReportReason.choices)
    detail = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("reporter", "post")

class CommentReport(TimeStampedModel):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_reports")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=20, choices=ReportReason.choices)
    detail = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("reporter", "comment")

class RoommateType(models.TextChoices):
    RECRUIT = "RECRUIT", "모집 글"
    APPLY = "APPLY", "지원 글"

class RoommatePost(TimeStampedModel):
    post = models.OneToOneField(CommunityPost, on_delete=models.CASCADE, related_name="roommate")
    kind = models.CharField(max_length=10, choices=RoommateType.choices)
    conditions = models.TextField(help_text="입주 조건/지역/예산/기간 등")

    location = models.CharField(max_length=100, blank=True, default="")
    budget_min = models.PositiveIntegerField(null=True, blank=True)
    budget_max = models.PositiveIntegerField(null=True, blank=True)
    move_in_date = models.DateField(null=True, blank=True)
