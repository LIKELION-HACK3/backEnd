import json
from typing import List, Dict, Any, Optional
from django.db import transaction, IntegrityError
from django.utils.dateparse import parse_datetime
from community.models import NewsArticle, NewsSource
from community.utils.category_utils import categorize_article

def _get_or_create_source(name:Optional[str]) -> NewsSource:
  name=(name or "Unknown").strip() or "Unknown"
  src, _ = NewsSource.objects.get_or_create(name=name)
  return src

def _parse_dt(s: Optional[str]):
    if not s:
        return None
    return parse_datetime(s)  

@transaction.atomic
def import_news_from_json(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        blob = json.load(f)

    if not isinstance(blob, list):
        return 0

    created_count = 0

    for top in blob:
        data = top.get("data") or {}
        doc = data.get("document") or {}
        inner = doc.get("data") or {}
        section_title = (inner.get("title") or "").strip()        
        contents: List[Dict[str, Any]] = inner.get("contents") or []
        if not isinstance(contents, list):
            continue

        for item in contents:
            if not isinstance(item, dict):
                continue

            title = (item.get("title") or "").strip()
            summary = (item.get("summary") or "").strip()
            pc_url = (item.get("pcUrl") or "").strip()
            if not title or not pc_url:
                continue

            source = _get_or_create_source(item.get("cpName"))
            category = categorize_article(title=title, summary=summary, section_title=section_title)

            defaults = {
                "source": source,
                "title": title,
                "published_at": _parse_dt(item.get("createdAt")),
                "thumbnail": (item.get("image") or "").strip(),
                "category": category,  
            }

            try:
                _, created = NewsArticle.objects.update_or_create(
                    url=pc_url,
                    defaults=defaults,
                )
                if created:
                    created_count += 1
            except IntegrityError:
                continue

    return created_count
