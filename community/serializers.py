from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    NewsSource, NewsArticle,
    CommunityPost, PostLike, PostReport,
    Comment, CommentLike, CommentReport, Notification,
    )

User=get_user_model()

#=== 뉴스 ===
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

#=== 함께해요 ===
class UserTinySerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("id", "username")

class CommentSerializer(serializers.ModelSerializer):
    author=UserTinySerializer(read_only=True)
    replies=serializers.SerializerMethodField(read_only=True)
    like_count=serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model=Comment
        fields=(
            "id", "post", "author", "parent", 
            "content", "created_at", "like_count", "replies",
        )
        read_only_fields=("id", "post", "author","created_at", "like_count", "replies")

    def get_replies(self, obj):
        qs=obj.replies.select_related("author").all().order_by("created_at")
        return CommentSerializer(qs, many=True, context=self.context).data

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields=("parent", "content")
    
    def validate(self, attrs):
        parent=attrs.get("parent", None)
        post=self.context.get("post", None)
        if parent and post:
            if parent.post_id != post.id:
                raise serializers.ValidationError()

        return attrs
    
    def create(self, validated_data):
        request=self.context.get("request")
        validated_data["author"]=request.user
        comment=super().create(validated_data)

        post=comment.post
        post.bump_comment_count(+1)
        return comment

class PostListSerializer(serializers.ModelSerializer):
    author=UserTinySerializer(read_only=True)
    region_display=serializers.CharField(source="get_region_display", read_only=True)
    category_display=serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model=CommunityPost
        fields=(
            "id", "title", "author", 
            "region", "region_display","category", "category_display",
            "views", "like_count", "comment_count", "created_at",
        )
        read_only_fields=("id","author","views","like_count", "comment_count", "created_at")

class PostDetailSerializer(serializers.ModelSerializer):
    author=UserTinySerializer(read_only=True)
    region_display=serializers.CharField(source="get_region_display", read_only=True)
    category_display=serializers.CharField(source="get_category_display", read_only=True)
    comments=serializers.SerializerMethodField(read_only=True)

    class Meta:
        model=CommunityPost
        fields=(
            "id", "title", "content","author", 
            "region", "region_display","category", "category_display",
            "views", "like_count", "comment_count", "created_at", "updated_at",
            "comments",
        )

        read_only_fields=(
            "id", "author", "views", "like_count", "comment_count", "created_at", "updated_at", "comments"
        )

    def get_comments(self, obj):
        root_qs=obj.comments.select_related("author").filter(parent__isnull=True).order_by("created_at")
        return CommentSerializer(root_qs, many=True, context=self.context).data

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=CommunityPost
        fields=("title", "content", "region", "category")

    def create(self, validated_data):
        request=self.context.get("request")
        validated_data["author"]=request.user
        return super().create(validated_data)
    
class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model=PostLike
        fields=("post",)

    def create(self, validated_data):
        request=self.context.get("request")
        validated_data["user"]=request.user
        obj, created=PostLike.objects.get_or_create(**validated_data)
        if created:obj.post.bump_like_count(+1)
        return obj
    
class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model=CommentLike
        fields=("comment",)

    def create(self, validated_data):
        request=self.context.get("request")
        validated_data["user"]=request.user
        obj, _ = CommentLike.objects.get_or_create(**validated_data)
        return obj
    
class PostReportSerializer(serializers.ModelSerializer):
    class Meta:
        model=PostReport
        fields=("reason",)

    def create(self, validated_data):
        request=self.context.get("request")
        validated_data["user"]=request.user
        return super().create(validated_data)
    
class CommentReportSerializer(serializers.ModelSerializer):
    class Meta: 
        model=CommentReport
        fields=("reason",)

    def create(self, validated_data):
        request=self.context.get("request")
        validated_data["user"]=request.user
        return super().create(validated_data)

#=== 알림 ===
class NotificationSerializer(serializers.ModelSerializer):
    actor = UserTinySerializer(read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id", "type", "message", "actor", "post", "comment", "is_read", "created_at"
        )
        read_only_fields = (
            "id", "type", "message", "actor", "post", "comment", "is_read", "created_at"
        )

class NotificationMarkReadSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)