import json
from typing import List, Dict, Any

from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room, RoomImage, Review
from .serializers import RoomSerializer, ReviewSerializer


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
