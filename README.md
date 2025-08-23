# backEnd

## Community API 명세서

- **Base URL**: `https://app.uniroom.shop`
- **인증**: 기본적으로 JWT Bearer 토큰. 공개 엔드포인트는 별도 표시

### 뉴스

#### GET /api/community/news/ (공개)
- **설명**: 뉴스 기사 목록 조회(검색/필터/정렬)
- **Query Params**
  - `q`: 제목/카테고리 검색어
  - `source_id`: 뉴스 소스 ID (정수)
  - `category`: 카테고리(정확 일치)
  - `date_from`: 게시일 시작 (YYYY-MM-DD)
  - `date_to`: 게시일 종료 (YYYY-MM-DD)
  - `ordering`: 정렬 필드(콤마 구분). 예: `-published_at,-id`
- **응답 200 예시**
```json
[
  {
    "id": 1,
    "title": "부동산 시장 동향",
    "url": "https://example.com/article/1",
    "thumbnail": "https://example.com/thumb.jpg",
    "category": "부동산",
    "published_at": "2025-08-12T09:00:00Z",
    "created_at": "2025-08-12T10:00:00Z",
    "source": {
      "id": 3,
      "name": "뉴스타임",
      "homepage": "https://newstime.example.com",
      "rss_url": "https://newstime.example.com/rss",
      "enabled": true
    }
  }
]
```

### 커뮤니티 게시글

#### GET /api/community/posts/ (공개)
- **설명**: 게시글 목록(최신순)
- **응답 200 예시**
```json
[
  {
    "id": 10,
    "title": "원룸 계약 팁",
    "author": { "id": 3, "username": "alice" },
    "region": "SOME_CODE",
    "region_display": "지역명",
    "category": "SOME_CAT",
    "category_display": "카테고리명",
    "views": 12,
    "like_count": 3,
    "comment_count": 4,
    "created_at": "2025-08-20T10:00:00Z"
  }
]
```

#### POST /api/community/posts/ (인증 필요)
- **설명**: 게시글 생성 (작성자는 토큰 사용자)
- **Body**
```json
{
  "title": "제목",
  "content": "내용",
  "region": "지역코드",
  "category": "카테고리코드"
}
```
- **응답 201**: 생성된 게시글 상세 반환

#### GET /api/community/posts/{post_id}/ (공개)
- **설명**: 게시글 상세 (호출 시 `views` 1 증가)
- **응답 200 예시**
```json
{
  "id": 11,
  "title": "제목",
  "content": "내용",
  "author": { "id": 3, "username": "alice" },
  "region": "지역코드",
  "region_display": "지역명",
  "category": "카테고리코드",
  "category_display": "카테고리명",
  "views": 1,
  "like_count": 0,
  "comment_count": 2,
  "created_at": "2025-08-20T10:00:00Z",
  "updated_at": "2025-08-20T10:10:00Z",
  "comments": []
}
```

#### PUT /api/community/posts/{post_id}/ (인증 필요)
- **설명**: 게시글 전체 수정
- **Body**: `title`, `content`, `region`, `category`

#### PATCH /api/community/posts/{post_id}/ (인증 필요)
- **설명**: 게시글 부분 수정

#### DELETE /api/community/posts/{post_id}/ (인증 필요)
- **설명**: 게시글 삭제 (204)

### 댓글

#### GET /api/community/posts/{post_id}/comments/ (공개)
- **설명**: 특정 게시글의 최상위 댓글 목록(작성 시간 오름차순), 각 항목은 `replies`로 대댓글 포함

#### POST /api/community/posts/{post_id}/comments/ (인증 필요)
- **설명**: 댓글 작성 (parent 지정 시 대댓글)
- **Body**
```json
{
  "parent": 100,
  "content": "대댓글 내용"
}
```

### 좋아요

#### POST /api/community/posts/{post_id}/like/ (인증 필요)
- **설명**: 게시글 좋아요 토글
- **응답 200 예시**
```json
{ "liked": true, "like_count": 4 }
```

#### POST /api/community/comments/{comment_id}/like/ (인증 필요)
- **설명**: 댓글 좋아요 토글
- **응답 200 예시**
```json
{ "liked": false, "count": 3 }
```

### 신고

#### POST /api/community/posts/{post_id}/report/ (인증 필요)
- **설명**: 게시글 신고
- **Body**
```json
{ "reason": "스팸/광고" }
```

#### POST /api/community/comments/{comment_id}/report/ (인증 필요)
- **설명**: 댓글 신고
- **Body**
```json
{ "reason": "욕설" }
```

### 오류 코드 공통
- 401 Unauthorized: 인증 필요 엔드포인트에 토큰 누락/만료
- 403 Forbidden: 권한 부족
- 404 Not Found: 대상 게시글/댓글 없음
- 400 Bad Request: 유효성 검증 실패