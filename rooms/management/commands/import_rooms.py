import json
from typing import Any, Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from rooms.models import Room, RoomImage


class Command(BaseCommand):
    help = "Import rooms from a JSON file with Korean keys (supports list or items/data/results keys)."

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

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str, help="Path to JSON file to import")

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        norm: Dict[str, Any] = {}
        for k, v in item.items():
            if k not in self.KOREAN_KEY_MAP:
                continue
            target = self.KOREAN_KEY_MAP[k]
            if target == "images":
                norm["images"] = v or []
            else:
                norm[target] = v
        return norm

    def _load_payload(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise CommandError(f"Failed to read JSON: {e}")

        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("items", "data", "results"):
                if key in data and isinstance(data[key], list):
                    return data[key]
        raise CommandError("JSON must be a list or contain items/data/results list.")

    @transaction.atomic
    def handle(self, *args, **options):
        path: str = options["json_path"]
        raw_items = self._load_payload(path)

        created, updated = 0, 0
        for raw in raw_items:
            item = self._normalize_item(raw)
            images = item.pop("images", [])
            external_id = item.get("external_id")

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

            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import completed. created={created}, updated={updated}"
        ))


