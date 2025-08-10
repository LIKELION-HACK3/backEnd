import json
from typing import List, Dict, Any

from django.db import transaction
from django.db.models import Q, Count
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room, RoomImage, Review
from .serializers import RoomSerializer, ReviewSerializer


class RoomStatsView(APIView):
    """
    방 타입별 통계 및 검색 옵션 제공 API
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # 방 타입별 개수
        room_type_stats = Room.objects.values('room_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 전체 방 개수
        total_rooms = Room.objects.count()
        
        # 지역별 방 개수 (구 단위)
        region_stats = []
        for room in Room.objects.values('address').distinct():
            if room['address']:
                # 주소에서 구 추출 (예: "중랑구 중화동" -> "중랑구")
                address_parts = room['address'].split()
                if len(address_parts) > 0:
                    region = address_parts[0]
                    region_stats.append(region)
        
        # 구별 개수 집계
        from collections import Counter
        region_counts = Counter(region_stats)
        region_stats = [{'region': region, 'count': count} for region, count in region_counts.most_common()]
        
        return Response({
            'total_rooms': total_rooms,
            'room_type_stats': list(room_type_stats),
            'region_stats': region_stats,
            'search_options': {
                'room_types': [item['room_type'] for item in room_type_stats if item['room_type']],
                'regions': [item['region'] for item in region_stats]
            }
        })


class RoomSearchView(APIView):
    """
    피그마 디자인에 맞는 방 검색 API
    - 지역명, 지하철역, 단지명으로 검색
    - 방 타입별 필터링
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # 검색 파라미터
        search_query = request.query_params.get('q', '').strip()  # 검색어
        room_type = request.query_params.get('room_type', '').strip()  # 방 타입
        
        # 기본 쿼리셋
        queryset = Room.objects.all().prefetch_related('images')
        
        # 검색어가 있는 경우: 제목, 주소에서 검색
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |  # 제목에서 검색
                Q(address__icontains=search_query)   # 주소에서 검색
            )
        
        # 방 타입 필터링
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        # 검색 결과 정렬 (최신순)
        queryset = queryset.order_by('-id')
        
        # 페이지네이션 (선택사항)
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        rooms = queryset[start:end]
        total_count = queryset.count()
        
        # 시리얼라이징
        serialized_rooms = RoomSerializer(rooms, many=True).data
        
        return Response({
            'rooms': serialized_rooms,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'search_query': search_query,
            'room_type': room_type,
            'filters_applied': {
                'search_query': bool(search_query),
                'room_type': bool(room_type)
            }
        })


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all().prefetch_related('images')
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all().prefetch_related('images')
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]


class ImportRoomsView(APIView):
    permission_classes = [AllowAny]

    KOREAN_KEY_MAP = {
        "매물ID": "external_id",
        "제목": "title",
        "방종류": "room_type",
        "월세": "monthly_fee",
        "보증금": "deposit",
        "관리비": "maintenance_cost",
        "공급면적": "supply_area",
        "전용면적": "real_area",
        "층수": "floor",
        "계약형태": "contract_type",
        "주소": "address",
        "위도": "latitude",
        "경도": "longitude",
        "이미지URL": "images",
    }

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        norm = {}
        for k, v in item.items():
            if k not in self.KOREAN_KEY_MAP:
                continue
            target = self.KOREAN_KEY_MAP[k]
            if target == "images":
                norm["images"] = v or []
            else:
                norm[target] = v
        return norm

    def _load_payload(self, request) -> List[Dict[str, Any]]:
        if 'file' in request.FILES:
            data = json.loads(request.FILES['file'].read().decode('utf-8'))
        else:
            data = request.data
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("items", "data", "results"):
                if key in data and isinstance(data[key], list):
                    return data[key]
        raise ValueError("리스트 형태의 JSON 또는 items/data/results 키로 리스트를 전달해주세요.")

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            raw_items = self._load_payload(request)
        except Exception as e:
            return Response({"detail": f"입력 파싱 오류: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        created, updated = 0, 0
        room_ids = []

        for raw in raw_items:
            item = self._normalize_item(raw)
            images = item.pop("images", [])
            external_id = item.get("external_id", None)

            if external_id is not None:
                room, is_created = Room.objects.update_or_create(
                    external_id=external_id, defaults=item
                )
            else:
                room = Room.objects.create(**item)
                is_created = True

            RoomImage.objects.filter(room=room).delete()
            for idx, url in enumerate(images):
                if url:
                    RoomImage.objects.create(room=room, image_url=url, ordering=idx)

            created += 1 if is_created else 0
            updated += 0 if is_created else 1
            room_ids.append(room.id)

        qs = Room.objects.filter(id__in=room_ids).prefetch_related('images')
        serialized = RoomSerializer(qs, many=True).data
        return Response(
            {"created": created, "updated": updated, "rooms": serialized},
            status=status.HTTP_201_CREATED
        )


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return Review.objects.filter(room_id=room_id).select_related('user', 'room')

    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        serializer.save(user=self.request.user, room_id=room_id)
