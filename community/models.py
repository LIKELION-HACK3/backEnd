from django.db import models

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
