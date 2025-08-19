from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import NewsArticle
from .serializers import NewsArticleSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

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

