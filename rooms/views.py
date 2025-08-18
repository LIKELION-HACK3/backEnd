import json
from typing import List, Dict, Any

from django.db import transaction
from django.db.models import Q, Count
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Room, RoomImage, Review
from .serializers import RoomSerializer, ReviewSerializer, RoomStatsResponseSerializer, RoomSearchResponseSerializer, ImportRoomsResponseSerializer, RoomRatingStatsResponseSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

@extend_schema(
    tags=['rooms'],
    summary='방 통계 및 검색 옵션',
    description='방 타입별 통계, 지역별 통계, 검색 옵션을 제공합니다.',
    responses={
        200: OpenApiResponse(
            response=RoomStatsResponseSerializer,
            description='통계 정보',
            examples=[
                OpenApiExample(
                    '통계 예시',
                    value={
                        'total_rooms': 150,
                        'room_type_stats': [
                            {'room_type': '원룸', 'count': 80},
                            {'room_type': '투룸', 'count': 70}
                        ],
                        'region_stats': [
                            {'region': '강남구', 'count': 30},
                            {'region': '마포구', 'count': 25}
                        ],
                        'search_options': {
                            'room_types': ['원룸', '투룸'],
                            'regions': ['강남구', '마포구']
                        }
                    },
                    response_only=True,
                    status_codes=['200']
                )
            ]
        )
    }
)
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


@extend_schema(
    tags=['rooms'],
    summary='방 검색',
    description='지역명, 지하철역, 단지명으로 방을 검색하고 방 타입별로 필터링합니다.',
    parameters=[
        OpenApiParameter(name='q', description='검색어', required=False, type=str),
        OpenApiParameter(name='room_type', description='방 타입', required=False, type=str),
        OpenApiParameter(name='page', description='페이지 번호', required=False, type=int, default=1),
        OpenApiParameter(name='page_size', description='페이지 크기', required=False, type=int, default=20),
    ],
    examples=[
        OpenApiExample(
            '검색 예시',
            value={
                'q': '강남',
                'room_type': '원룸',
                'page': 1,
                'page_size': 20
            },
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=RoomSearchResponseSerializer,
            description='검색 결과',
            examples=[
                OpenApiExample(
                    '검색 결과 예시',
                    value={
                        'rooms': [
                            {
                                'id': 1,
                                'title': '강남 원룸',
                                'room_type': '원룸',
                                'monthly_fee': 500000,
                                'address': '강남구',
                                'images': []
                            }
                        ],
                        'total_count': 1,
                        'page': 1,
                        'page_size': 20,
                        'search_query': '강남',
                        'room_type': '원룸',
                        'filters_applied': {'search_query': True, 'room_type': True}
                    },
                    response_only=True,
                    status_codes=['200']
                )
            ]
        )
    }
)
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


@extend_schema(
    tags=['rooms'],
    summary='방 목록 조회 및 생성',
    description='모든 방 목록을 조회하거나 새로운 방을 생성합니다.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'title': {
                    'type': 'string',
                    'description': '방 제목',
                    'example': '강남 원룸'
                },
                'room_type': {
                    'type': 'string',
                    'description': '방 타입',
                    'example': '원룸',
                    'enum': ['원룸', '투룸', '쓰리룸', '오피스텔', '아파트']
                },
                'deposit': {
                    'type': 'integer',
                    'description': '보증금 (원)',
                    'example': 1000000
                },
                'monthly_fee': {
                    'type': 'integer',
                    'description': '월세 (원)',
                    'example': 500000
                },
                'maintenance_cost': {
                    'type': 'integer',
                    'description': '관리비 (원)',
                    'example': 50000
                },
                'supply_area': {
                    'type': 'number',
                    'description': '공급면적 (㎡)',
                    'example': 25.5
                },
                'real_area': {
                    'type': 'number',
                    'description': '전용면적 (㎡)',
                    'example': 20.3
                },
                'floor': {
                    'type': 'string',
                    'description': '층수',
                    'example': '3층'
                },
                'contract_type': {
                    'type': 'string',
                    'description': '계약형태',
                    'example': '월세',
                    'enum': ['월세', '전세', '반전세']
                },
                'address': {
                    'type': 'string',
                    'description': '주소',
                    'example': '강남구 역삼동'
                },
                'latitude': {
                    'type': 'number',
                    'description': '위도',
                    'example': 37.5665
                },
                'longitude': {
                    'type': 'number',
                    'description': '경도',
                    'example': 126.9780
                }
            },
            'required': ['title', 'room_type', 'monthly_fee', 'address']
        }
    },
    responses={
        200: OpenApiResponse(
            response=RoomSerializer(many=True),
            description='방 목록 조회 성공',
        ),
        201: OpenApiResponse(
            response=RoomSerializer,
            description='방 생성 성공',
        ),
        400: '잘못된 요청 데이터'
    }
)
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all().prefetch_related('images')
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=['rooms'],
    summary='방 상세 조회, 수정, 삭제',
    description='특정 방의 상세 정보를 조회, 수정, 삭제합니다.',
    parameters=[
        OpenApiParameter(name='pk', description='방 ID', required=True, type=int),
    ],
    responses={
        200: RoomSerializer,
        404: '방을 찾을 수 없습니다',
    }
)
class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all().prefetch_related('images')
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=['rooms'],
    summary='방 데이터 대량 임포트',
    description='JSON 파일이나 데이터를 통해 방 정보를 대량으로 임포트합니다. real-estate.json의 한글 키를 그대로 지원합니다.',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'real-estate.json 형식의 JSON 파일 업로드'
                }
            }
        },
        'application/json': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    '매물ID': {'type': 'integer', 'description': '외부 매물 식별자', 'example': 17851114},
                    '제목': {'type': 'string', 'example': '중화역3분 근저당X 초저가 지상층 풀옵션 원룸'},
                    '방종류': {'type': 'string', 'example': '원룸'},
                    '월세': {'type': 'integer', 'example': 400000},
                    '보증금': {'type': 'integer', 'example': 5000000},
                    '관리비': {'type': 'integer', 'example': 50000},
                    '공급면적': {'type': 'number', 'example': 19.84},
                    '전용면적': {'type': 'number', 'example': 16.53},
                    '층수': {'type': 'string', 'example': '2층/3층'},
                    '계약형태': {'type': 'string', 'example': '월세'},
                    '주소': {'type': 'string', 'example': '중랑구 중화동'},
                    '위도': {'type': 'number', 'example': 37.6036059},
                    '경도': {'type': 'number', 'example': 127.0766452},
                    '이미지URL': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': '이미지 URL 배열',
                        'example': [
                            'https://img.peterpanz.com/photo/20250723/17851114/68809f91e5e93_thumb.jpg'
                        ]
                    }
                },
                'required': ['제목', '방종류', '월세', '주소']
            },
            'examples': [
                {
                    '매물ID': 17851114,
                    '제목': '중화역3분 근저당X 초저가 지상층 풀옵션 원룸',
                    '방종류': '원룸',
                    '월세': 400000,
                    '보증금': 5000000,
                    '관리비': 50000,
                    '공급면적': 19.84,
                    '전용면적': 16.53,
                    '층수': '2층/3층',
                    '계약형태': '월세',
                    '주소': '중랑구 중화동',
                    '위도': 37.6036059,
                    '경도': 127.0766452,
                    '이미지URL': ['https://img.peterpanz.com/photo/20250723/17851114/68809f91e5e93_thumb.jpg']
                }
            ]
        }
    },
    responses={
        201: OpenApiResponse(
            response=ImportRoomsResponseSerializer,
            description='임포트 결과',
            examples=[
                OpenApiExample(
                    '임포트 성공 예시',
                    value={'created': 10, 'updated': 5, 'rooms': []},
                    response_only=True,
                    status_codes=['201']
                )
            ]
        ),
        400: OpenApiResponse(description='입력 파싱 오류')
    }
)
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


@extend_schema(
    tags=['rooms'],
    summary='방 리뷰 목록 및 생성',
    description='특정 방의 리뷰를 조회하거나 새로운 리뷰를 생성합니다.',
    parameters=[
        OpenApiParameter(name='room_id', description='방 ID', required=True, type=int),
    ],
    examples=[
        OpenApiExample(
            '리뷰 생성 요청 예시',
            value={
                'rating_safety': 4,
                'rating_noise': 3,
                'rating_light': 5,
                'rating_traffic': 4,
                'rating_bug': 5,  # 벌레(내부 필드 rating_clean)
                'content': '채광 좋고 벌레 거의 없어요.'
            },
            request_only=True,
        )
    ],
    responses={
        200: ReviewSerializer(many=True),
        201: ReviewSerializer,
    }
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


@extend_schema(
    tags=['rooms'],
    summary='방 리뷰 별점 통계',
    description='특정 방의 카테고리별 평균/분포 및 전체 평균을 제공합니다. 피그마 카테고리(채광/방음/벌레/보안/교통)에 맞춰 반환합니다.',
    parameters=[
        OpenApiParameter(name='room_id', description='방 ID', required=True, type=int),
    ],
    responses={
        200: OpenApiResponse(
            response=RoomRatingStatsResponseSerializer,
            description='별점 통계',
            examples=[
                OpenApiExample(
                    '별점 통계 예시',
                    value={
                        'reviews_count': 7,
                        'averages': {
                            'safety': 3.9,
                            'noise': 2.7,
                            'light': 4.1,
                            'traffic': 3.3,
                            'bug': 4.8,
                            'overall': 3.7
                        },
                        'distributions': {
                            'safety': {'_1': 0, '_2': 1, '_3': 2, '_4': 3, '_5': 1},
                            'noise': {'_1': 2, '_2': 1, '_3': 2, '_4': 1, '_5': 1},
                            'light': {'_1': 0, '_2': 0, '_3': 2, '_4': 3, '_5': 2},
                            'traffic': {'_1': 1, '_2': 1, '_3': 3, '_4': 1, '_5': 1},
                            'bug': {'_1': 0, '_2': 0, '_3': 1, '_4': 1, '_5': 5}
                        }
                    },
                    response_only=True,
                    status_codes=['200']
                )
            ]
        )
    }
)
class RoomRatingStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, room_id: int):
        qs = Review.objects.filter(room_id=room_id)

        def avg_or_none(values):
            values = [v for v in values if v is not None]
            if not values:
                return None
            return round(sum(values) / len(values), 2)

        def dist(values):
            base = {str(i): 0 for i in range(1, 6)}
            for v in values:
                if v in (1, 2, 3, 4, 5):
                    base[str(v)] += 1
            return base

        ratings = list(qs.values('rating_safety', 'rating_noise', 'rating_light', 'rating_traffic', 'rating_clean'))

        safety_vals = [r['rating_safety'] for r in ratings]
        noise_vals = [r['rating_noise'] for r in ratings]
        light_vals = [r['rating_light'] for r in ratings]
        traffic_vals = [r['rating_traffic'] for r in ratings]
        bug_vals = [r['rating_clean'] for r in ratings]  # 내부 필드명을 벌레로 매핑

        # 각 리뷰별 overall 계산(채워진 항목 평균)
        overall_vals = []
        for r in ratings:
            filled = [v for v in (r['rating_safety'], r['rating_noise'], r['rating_light'], r['rating_traffic'], r['rating_clean']) if v is not None]
            if filled:
                overall_vals.append(round(sum(filled) / len(filled)))

        data = {
            'reviews_count': qs.count(),
            'averages': {
                'safety': avg_or_none(safety_vals),
                'noise': avg_or_none(noise_vals),
                'light': avg_or_none(light_vals),
                'traffic': avg_or_none(traffic_vals),
                'bug': avg_or_none(bug_vals),
                'overall': avg_or_none(overall_vals),
            },
            'distributions': {
                'safety': dist(safety_vals),
                'noise': dist(noise_vals),
                'light': dist(light_vals),
                'traffic': dist(traffic_vals),
                'bug': dist(bug_vals),
            }
        }

        serializer = RoomRatingStatsResponseSerializer(data)
        return Response(serializer.data)
