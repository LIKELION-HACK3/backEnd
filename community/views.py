from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import NewsArticle
from .serializers import NewsArticleSerializer

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

