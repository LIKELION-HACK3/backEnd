from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import F
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from .models import (
    NewsArticle,CommunityPost, Comment,
    PostLike, CommentLike, PostReport, CommentReport,
    Region,Category, Notification, NotificationType
    )
from .serializers import (
    NewsArticleSerializer,PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, PostLikeSerializer, CommentLikeSerializer,
    PostReportSerializer, CommentReportSerializer, NotificationSerializer,
    )

@extend_schema(
    tags=['community'],
    summary='뉴스/커뮤니티 기사 목록',
    description='뉴스 기사 목록을 검색/정렬/필터링하여 조회합니다.\n\n'
                '- 검색: q(title, category)\n'
                '- 필터: source_id, category, date_from~date_to(YYYY-MM-DD)\n'
                '- 정렬: ordering (예: -published_at, created_at)',
    parameters=[
        OpenApiParameter(name='q', description='제목/카테고리 검색어', required=False, type=str),
        OpenApiParameter(name='source_id', description='뉴스 소스 ID', required=False, type=int),
        OpenApiParameter(name='category', description='카테고리(정확 일치)', required=False, type=str),
        OpenApiParameter(name='date_from', description='게시일 시작 (YYYY-MM-DD)', required=False, type=str),
        OpenApiParameter(name='date_to', description='게시일 종료 (YYYY-MM-DD)', required=False, type=str),
        OpenApiParameter(name='ordering', description='정렬 필드(콤마 구분). 예: -published_at,-id', required=False, type=str),
    ],
    responses={
        200: OpenApiResponse(
            response=NewsArticleSerializer(many=True),
            description='기사 목록',
            examples=[
                OpenApiExample(
                    '예시',
                    value=[
                        {
                            'id': 1,
                            'title': '부동산 시장 동향',
                            'url': 'https://example.com/article/1',
                            'thumbnail': 'https://example.com/thumb.jpg',
                            'category': '부동산',
                            'published_at': '2025-08-12T09:00:00Z',
                            'created_at': '2025-08-12T10:00:00Z',
                            'source': {
                                'id': 3,
                                'name': '뉴스타임',
                                'homepage': 'https://newstime.example.com',
                                'rss_url': 'https://newstime.example.com/rss',
                                'enabled': True
                            }
                        }
                    ],
                    response_only=True,
                    status_codes=['200']
                )
            ]
        )
    }
)
class NewsArticleListView(generics.ListAPIView):
    permission_classes=[AllowAny]
    
    serializer_class = NewsArticleSerializer
    queryset = NewsArticle.objects.select_related("source").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "category"]             
    ordering_fields = ["published_at", "created_at"]
    ordering = ["-published_at", "-id"]
    filterset_fields = ["source", "category"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(category__icontains=q))

        source_id = self.request.query_params.get("source_id")
        if source_id:
            qs = qs.filter(source_id=source_id)

        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(published_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(published_at__date__lte=date_to)

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)  
        return qs

@extend_schema_view(
    get=extend_schema(
        tags=['community'],
        summary='커뮤니티 게시글 목록',
        description='커뮤니티 게시글을 최신순으로 조회합니다.',
        responses=PostListSerializer(many=True),
    ),
    post=extend_schema(
        tags=['community'],
        summary='커뮤니티 게시글 생성',
        request=PostCreateUpdateSerializer,
        responses=PostDetailSerializer,
    ),
)
class PostListView(generics.ListCreateAPIView):
    queryset = CommunityPost.objects.all().select_related("author").order_by("-created_at")
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateUpdateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema_view(
    get=extend_schema(
        tags=['community'],
        summary='게시글 상세',
        responses=PostDetailSerializer,
    ),
    put=extend_schema(
        tags=['community'],
        summary='게시글 전체 수정',
        request=PostCreateUpdateSerializer,
        responses=PostDetailSerializer,
    ),
    patch=extend_schema(
        tags=['community'],
        summary='게시글 일부 수정',
        request=PostCreateUpdateSerializer,
        responses=PostDetailSerializer,
    ),
    delete=extend_schema(
        tags=['community'],
        summary='게시글 삭제',
        responses={204: OpenApiResponse(description='삭제 성공')},
    ),
)
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommunityPost.objects.all().select_related("author")
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        CommunityPost.objects.filter(pk=obj.pk).update(views=F("views") + 1)
        obj.refresh_from_db()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        tags=['community'],
        summary='댓글 목록',
        description='특정 게시글의 최상위 댓글 목록을 생성시간 오름차순으로 조회합니다.',
        responses=CommentSerializer(many=True),
    ),
    post=extend_schema(
        tags=['community'],
        summary='댓글 작성',
        request=CommentCreateSerializer,
        responses=CommentSerializer,
    ),
)
class CommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post_id=post_id, parent__isnull=True).select_related("author").order_by("created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == "POST":
            context["post"] = get_object_or_404(CommunityPost, pk=self.kwargs["post_id"]) 
        return context

    def perform_create(self, serializer):
        post = get_object_or_404(CommunityPost, pk=self.kwargs["post_id"])
        comment = serializer.save(author=self.request.user, post=post)

        # 알림 생성: 게시글 작성자에게 (본인 댓글은 제외)
        if post.author_id != self.request.user.id and comment.parent is None:
            Notification.objects.create(
                recipient=post.author,
                actor=self.request.user,
                type=NotificationType.COMMENT_ON_POST,
                post=post,
                comment=comment,
                message=f"'{post.title}'에 새 댓글이 달렸습니다.",
            )
        # 알림 생성: 대댓글인 경우 원댓글 작성자에게 (본인 제외)
        if comment.parent is not None and comment.parent.author_id != self.request.user.id:
            Notification.objects.create(
                recipient=comment.parent.author,
                actor=self.request.user,
                type=NotificationType.REPLY_ON_COMMENT,
                post=post,
                comment=comment,
                message="내 댓글에 대댓글이 달렸습니다.",
            )

class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['community'],
        summary='게시글 좋아요 토글',
        description='좋아요가 없으면 생성, 있으면 취소합니다.',
        responses={200: OpenApiResponse(description='토글 결과')},
    )
    def post(self, request, post_id):
        post = get_object_or_404(CommunityPost, pk=post_id)
        like = PostLike.objects.filter(user=request.user, post=post).first()

        if like:
            like.delete()
            CommunityPost.objects.filter(pk=post.pk).update(like_count=F("like_count") - 1)
            post.refresh_from_db(fields=["like_count"])
            return Response({"liked": False, "like_count": post.like_count}, status=status.HTTP_200_OK)

        PostLike.objects.create(user=request.user, post=post)
        CommunityPost.objects.filter(pk=post.pk).update(like_count=F("like_count") + 1)
        post.refresh_from_db(fields=["like_count"])
        return Response({"liked": True, "like_count": post.like_count}, status=status.HTTP_200_OK)

class CommentLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['community'],
        summary='댓글 좋아요 토글',
        description='좋아요가 없으면 생성, 있으면 취소합니다.',
        responses={200: OpenApiResponse(description='토글 결과')},
    )
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        like = CommentLike.objects.filter(user=request.user, comment=comment).first()

        if like:
            like.delete()
            liked = False
        else:
            CommentLike.objects.create(user=request.user, comment=comment)
            liked = True

        count = CommentLike.objects.filter(comment=comment).count()
        return Response({"liked": liked, "count": count}, status=status.HTTP_200_OK)


@extend_schema(
    tags=['community'],
    summary='게시글 신고',
    request=PostReportSerializer,
    responses=PostReportSerializer,
)
class PostReportView(generics.CreateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(CommunityPost, pk=self.kwargs["post_id"])
        serializer.save(user=self.request.user, post=post)


@extend_schema(
    tags=['community'],
    summary='댓글 신고',
    request=CommentReportSerializer,
    responses=CommentReportSerializer,
)
class CommentReportView(generics.CreateAPIView):
    serializer_class = CommentReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        comment = get_object_or_404(Comment, pk=self.kwargs["comment_id"])
        serializer.save(user=self.request.user, comment=comment)



@extend_schema(
    tags=['community'],
    summary='댓글/대댓글 삭제',
    responses={204: OpenApiResponse(description='삭제 성공')},
)
class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)

        # 작성자 또는 관리자 권한 확인
        if request.user != comment.author and not request.user.is_staff:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        post = comment.post

        # 하위 대댓글까지 포함된 총 삭제 개수 계산
        def count_descendants(node):
            total = 1
            for child in node.replies.all():
                total += count_descendants(child)
            return total

        to_delete_count = count_descendants(comment)

        with transaction.atomic():
            comment.delete()  # CASCADE로 대댓글 포함 삭제
            CommunityPost.objects.filter(pk=post.pk).update(
                comment_count=F("comment_count") - to_delete_count
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        tags=['community'],
        summary='읽지 않은 알림 목록',
        responses=NotificationSerializer(many=True),
    ),
)
class NotificationUnreadListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user, is_read=False).select_related("actor").order_by("-created_at")


@extend_schema(
    tags=['community'],
    summary='알림 읽음 처리',
    responses={200: OpenApiResponse(description='읽음 처리 완료')},
)
class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        notification_ids = request.data.get("ids", [])
        qs = Notification.objects.filter(recipient=request.user, id__in=notification_ids)
        updated = qs.update(is_read=True)
        return Response({"updated": updated}, status=status.HTTP_200_OK)

