from typing import Optional

POLICY_KEYWORDS=[
  "정부지원", "정부 지원", "지원금", "보조금", "정책", "대책", "공고", "모집", "신청", "접수",
  "발표", "시행", "개편", "개정", "지침", "안내문", "국토부", "국토교통부", "복지부", "기재부",
  "지자체", "서울시", "경기도", "조례", "공공임대", "청년월세", "전세대출", "대출제도",
]

LIFE_KEYWORDS=[
   "자취", "원룸", "생활", "꿀팁", "노하우", "체크리스트", "청소", "정리",
  "인테리어", "이사", "계약 팁", "생활 팁", "절약", "공과금", "하숙", "기숙사",
]

INFO_KEYWORDS=[
  "가이드", "총정리", "정리", "핵심", "FAQ", "Q&A", "알아두면", "해설", "분석",
  "데이터", "통계", "리포트", "전망", "인사이트", "리서치", "브리핑",
]

def _contains_any(text:str, keywords) -> bool:
  return any(kw in text for kw in keywords)

def categorize_article(title: str, summary: Optional[str]=None, section_title:Optional[str]=None) -> str:
  t=(title or "").strip()
  s=(summary or "").strip()
  sec=(section_title or "").strip()
  blob=" ".join([t,s,sec])

  if _contains_any(blob, POLICY_KEYWORDS):
    return "정책"
  if _contains_any(blob, LIFE_KEYWORDS):
    return "생활"
  if _contains_any(blob, INFO_KEYWORDS):
    return "정보"
  
  return "뉴스"
