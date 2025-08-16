from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import (Category, CommunityPost, Comment, PostLike, CommentLike, PostReport, CommentReport, RoommatePost, RoommateType)

User=get_user_model()

class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ["id", "name", "slug"]

class CommunityPostListSerializer(serializers.ModelSerializer):
  user=serializers.StringRelatedField(read_only=True)
  category=CategorySerializer(read_only=True)
  comment_count=serializers.SerializerMethodField()
  like_count=serializers.SerializerMethodField()
  report_count=serializers.SerializerMethodField()
  image=serializers.ImageField(read_only=True)

  class Meta:
    model = CommunityPost
    fields=["id", "title", "user", "category", "image", "is_active", "comment_count",
            "like_count", "report_count", "created_at", "updated_at"]
    
    read_only_fields=["user", "category", "image", "is_active", "comment_count",
                      "like_count", "report_count", "created_at", "updated_at",]
    
    def get_comment_count(self, obj):
      return obj.comments.count()
    
    def get_like_count(self, obj):
      return obj.likes.count()
    
    def get_report_count(self, obj):
      return obj.reports.count()
    
class CommunityPostDetailSerializer(serializers.ModelSerializer):
  user=serializers.StringRelatedField(read_only=True)
  category=CategorySerializer(read_only=True)
  comment_count=serializers.SerializerMethodField()
  like_count=serializers.SerializerMethodField()
  report_count=serializers.SerializerMethodField()
  image=serializers.ImageField(read_only=True)

  class Meta:
    fields=["id", "title", "content", "user", "category", "image",
            "is_active", "comment_count", "like_count", "report_count", "created_at", "updated_at"]
    
    read_only_fields=["user", "category", "image", "is_active",
                      "comment_count", "like_count", "report_count", "created_at", "updated_at"]
    
    def get_comment_count(self,obj):
      return obj.comments.count()
    
    def get_like_count(self, obj):
      return obj.likes.count()
    
    def get_report_count(Self, obj):
      return obj.reports.count()
    
class CommunityPostCreateUpdateSerializer(serializers.ModelSerializer):
  user=serializers.HiddenField(default=serializers.CurrentUserDefault())

  class Meta:
    model=CommunityPost
    fields=["id", "user", "category", "title", "content", "image", "is_active"]
    read_only_fields=["is_active"]

class CommentSerializer(serializers.ModelSerializer):
  user=serializers.HiddenField(default=serializers.CurrentUserDefault())
  post=serializers.PrimaryKeyRelatedField(queryset=CommunityPost.objects.all())

  class Meta:
    model=Comment
    fields=["id", "user", "post", "comment", "parent", "is_active",
            "created_at", "updated_at"]
    read_only_fields=["is_active", "created_at", "updated_at"]

    def validate(self, attrs):
      parent=attrs.get("parent")
      post=attrs.get("post")
      if parent and post and parent.post_id != post.id:
        raise serializers.ValidationError("부모 댓글과 게시글이 일치해야 합니다.")
      return attrs 
    
class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PostLike
        fields = ["id", "user", "post", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=PostLike.objects.all(),
                fields=("user", "post"),
                message="이미 이 게시글에 좋아요를 눌렀습니다.",
            )
        ]


class CommentLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CommentLike
        fields = ["id", "user", "comment", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=CommentLike.objects.all(),
                fields=("user", "comment"),
                message="이미 이 댓글에 좋아요를 눌렀습니다.",
            )
        ]

class PostReportSerializer(serializers.ModelSerializer):
    reporter = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PostReport
        fields = ["id", "reporter", "post", "reason", "detail", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=PostReport.objects.all(),
                fields=("reporter", "post"),
                message="이 게시글을 이미 신고했습니다.",
            )
        ]


class CommentReportSerializer(serializers.ModelSerializer):
    reporter = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CommentReport
        fields = ["id", "reporter", "comment", "reason", "detail", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=CommentReport.objects.all(),
                fields=("reporter", "comment"),
                message="이 댓글을 이미 신고했습니다.",
            )
        ]

class RoommatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoommatePost
        fields = [
            "id", "kind", "conditions", "location",
            "budget_min", "budget_max", "move_in_date",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]