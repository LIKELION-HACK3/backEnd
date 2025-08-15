# API 명세서

## 📋 개요
- **Base URL**: `아직 미정.`
- **인증 방식**: JWT (JSON Web Token)
- **응답 형식**: JSON

---

## 🔐 사용자 인증 (Users)

### 1. 회원가입
- **URL**: `POST /api/users/signup/`
- **설명**: 새로운 사용자 계정을 생성합니다
- **인증**: 불필요
- **요청 데이터**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "password_confirm": "string"
  }
  ```
- **응답**:
  ```json
  {
    "message": "회원가입이 완료되었습니다.",
    "user": {
      "id": 1,
      "username": "string",
      "email": "string",
      "created_at": "2025-08-10T20:25:17Z"
    },
    "tokens": {
      "refresh": "string",
      "access": "string"
    }
  }
  ```

### 2. 로그인
- **URL**: `POST /api/users/login/`
- **설명**: 사용자 인증 후 JWT 토큰을 발급합니다
- **인증**: 불필요
- **요청 데이터**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **응답**:
  ```json
  {
    "message": "로그인 성공",
    "user": {
      "id": 1,
      "username": "string",
      "email": "string",
      "created_at": "2025-08-10T20:25:17Z"
    },
    "tokens": {
      "refresh": "string",
      "access": "string"
    }
  }
  ```

### 3. 내 정보 조회
- **URL**: `GET /api/users/me/`
- **설명**: 현재 로그인한 사용자의 정보를 조회합니다
- **인증**: 필요 (Authorization: Bearer {access_token})
- **응답**:
  ```json
  {
    "id": 1,
    "username": "string",
    "email": "string",
    "created_at": "2025-08-10T20:25:17Z"
  }
  ```

### 4. 토큰 갱신
- **URL**: `POST /api/users/token/refresh/`
- **설명**: 만료된 액세스 토큰을 리프레시 토큰으로 갱신합니다
- **인증**: 불필요
- **요청 데이터**:
  ```json
  {
    "refresh": "string"
  }
  ```
- **응답**:
  ```json
  {
    "access": "string"
  }
  ```

---

## 🏠 방 매물 (Rooms)

### 1. 방 목록 조회
- **URL**: `GET /api/rooms/`
- **설명**: 모든 방 매물의 목록을 조회합니다
- **인증**: 불필요
- **쿼리 파라미터**: 없음
- **응답**:
  ```json
  [
    {
      "id": 1,
      "title": "중화역3분 근저당X 초저가 지상층 풀옵션 원룸",
      "room_type": "원룸",
      "deposit": 5000000,
      "monthly_fee": 400000,
      "maintenance_cost": 50000,
      "supply_area": 19.84,
      "real_area": 16.53,
      "floor": "2층/3층",
      "contract_type": "월세",
      "address": "중랑구 중화동",
      "latitude": 37.6036059,
      "longitude": 127.0766452,
      "images": [
        {
          "id": 1,
          "image_url": "https://img.peterpanz.com/photo/...",
          "ordering": 0
        }
      ]
    }
  ]
  ```

### 2. 방 상세 조회
- **URL**: `GET /api/rooms/{id}/`
- **설명**: 특정 방 매물의 상세 정보를 조회합니다
- **인증**: 불필요
- **응답**: 방 목록과 동일한 구조

### 3. 방 검색
- **URL**: `GET /api/rooms/search/`
- **설명**: 피그마 디자인에 맞는 방 검색 기능
- **인증**: 불필요
- **쿼리 파라미터**:
  - `q`: 검색어 (지역명, 지하철역, 단지명)
  - `room_type`: 방 타입 (원룸, 투룸, 아파트, 빌라, 오피스텔)
  - `page`: 페이지 번호 (기본값: 1)
  - `page_size`: 페이지당 방 개수 (기본값: 20)
- **사용 예시**:
  ```
  GET /api/rooms/search/?q=중화동&room_type=원룸&page=1&page_size=10
  ```
- **응답**:
  ```json
  {
    "rooms": [...],
    "total_count": 150,
    "page": 1,
    "page_size": 20,
    "search_query": "중화동",
    "room_type": "원룸",
    "filters_applied": {
      "search_query": true,
      "room_type": true
    }
  }
  ```

### 4. 방 통계
- **URL**: `GET /api/rooms/stats/`
- **설명**: 방 타입별 통계 및 검색 옵션을 제공합니다
- **인증**: 불필요
- **응답**:
  ```json
  {
    "total_rooms": 150,
    "room_type_stats": [
      {
        "room_type": "원룸",
        "count": 80
      },
      {
        "room_type": "투룸",
        "count": 45
      }
    ],
    "region_stats": [
      {
        "region": "중랑구",
        "count": 120
      },
      {
        "region": "노원구",
        "count": 30
      }
    ],
    "search_options": {
      "room_types": ["원룸", "투룸", "아파트", "빌라", "오피스텔"],
      "regions": ["중랑구", "노원구"]
    }
  }
  ```

### 5. 방 생성
- **URL**: `POST /api/rooms/`
- **설명**: 새로운 방 매물을 생성합니다
- **인증**: 불필요
- **요청 데이터**:
  ```json
  {
    "title": "string",
    "room_type": "string",
    "deposit": 0,
    "monthly_fee": 0,
    "maintenance_cost": 0,
    "supply_area": 0.0,
    "real_area": 0.0,
    "floor": "string",
    "contract_type": "string",
    "address": "string",
    "latitude": 0.0,
    "longitude": 0.0
  }
  ```

### 6. 방 수정
- **URL**: `PATCH /api/rooms/{id}/`
- **설명**: 기존 방 매물의 정보를 수정합니다
- **인증**: 불필요
- **요청 데이터**: 수정할 필드만 포함

### 7. 방 삭제
- **URL**: `DELETE /api/rooms/{id}/`
- **설명**: 방 매물을 삭제합니다
- **인증**: 불필요

### 8. 방 데이터 일괄 등록
- **URL**: `POST /api/rooms/import/`
- **설명**: JSON 파일을 통해 방 데이터를 일괄 등록합니다
- **인증**: 불필요
- **요청 데이터**: JSON 파일 또는 JSON 데이터
- **응답**:
  ```json
  {
    "created": 100,
    "updated": 50,
    "rooms": [...]
  }
  ```

---

## 💬 방 리뷰 (Reviews)

### 1. 리뷰 목록 조회
- **URL**: `GET /api/rooms/{room_id}/reviews/`
- **설명**: 특정 방의 리뷰 목록을 조회합니다
- **인증**: 필요 (Authorization: Bearer {access_token})
- **응답**:
  ```json
  [
    {
      "id": 1,
      "rating_safety": 4,
      "rating_noise": 3,
      "rating_light": 5,
      "rating_traffic": 4,
      "rating_clean": 4,
      "content": "좋은 방이에요!",
      "created_at": "2025-08-10T20:25:17Z",
      "user": {
        "id": 1,
        "username": "string"
      },
      "room": {
        "id": 1,
        "title": "string"
      }
    }
  ]
  ```

### 2. 리뷰 작성
- **URL**: `POST /api/rooms/{room_id}/reviews/`
- **설명**: 특정 방에 대한 리뷰를 작성합니다
- **인증**: 필요 (Authorization: Bearer {access_token})
- **요청 데이터**:
  ```json
  {
    "rating_safety": 4,
    "rating_noise": 3,
    "rating_light": 5,
    "rating_traffic": 4,
    "rating_clean": 4,
    "content": "좋은 방이에요!"
  }
  ```

---

## 🔑 인증 헤더

JWT 토큰이 필요한 API 호출 시 다음 헤더를 포함해야 합니다:

```
Authorization: Bearer {access_token}
```

---

## 📝 에러 응답

### 400 Bad Request
```json
{
  "detail": "입력 파싱 오류: ..."
}
```

### 401 Unauthorized
```json
{
  "detail": "자격 증명이 제공되지 않았습니다."
}
```

### 404 Not Found
```json
{
  "detail": "찾을 수 없습니다."
}
```

---

## 🚀 사용 예시

### 1. 회원가입 → 로그인 → 방 검색
```bash
# 1. 회원가입
curl -X POST http://127.0.0.1:8000/api/users/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123","password_confirm":"password123"}'

# 2. 로그인
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 3. 방 검색 (토큰 사용)
curl -X GET "http://127.0.0.1:8000/api/rooms/search/?q=중화동&room_type=원룸" \
  -H "Authorization: Bearer {access_token}"
```

### 2. 방 통계 조회
```bash
curl -X GET http://127.0.0.1:8000/api/rooms/stats/
```

### 3. 내 정보 조회
```bash
curl -X GET http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer {access_token}"
```

---

## 📊 데이터 모델

### User 모델
- `id`: 사용자 ID (자동 생성)
- `username`: 사용자명 (고유)
- `email`: 이메일 (고유)
- `created_at`: 계정 생성 시간

### Room 모델
- `id`: 방 ID (자동 생성)
- `title`: 방 제목
- `room_type`: 방 타입 (원룸, 투룸, 아파트, 빌라, 오피스텔)
- `deposit`: 보증금
- `monthly_fee`: 월세
- `maintenance_cost`: 관리비
- `supply_area`: 공급면적
- `real_area`: 전용면적
- `floor`: 층수
- `contract_type`: 계약형태
- `address`: 주소
- `latitude`: 위도
- `longitude`: 경도
- `external_id`: 외부 매물 ID

### RoomImage 모델
- `id`: 이미지 ID (자동 생성)
- `room`: 방 (외래키)
- `image_url`: 이미지 URL
- `ordering`: 이미지 순서

### Review 모델
- `id`: 리뷰 ID (자동 생성)
- `user`: 사용자 (외래키)
- `room`: 방 (외래키)
- `rating_safety`: 안전성 평점 (1-5)
- `rating_noise`: 소음 평점 (1-5)
- `rating_light`: 채광 평점 (1-5)
- `rating_traffic`: 교통 편의성 평점 (1-5)
- `rating_clean`: 청결도 평점 (1-5)
- `content`: 리뷰 내용
- `created_at`: 리뷰 작성 시간
