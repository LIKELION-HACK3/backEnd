import json
import os
import openai
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AIComparisonReport
from .serializers import AIComparisonReportSerializer, AIComparisonRequestSerializer
from rooms.models import Room
# from bookmarks.models import Bookmark  # 임시로 주석 처리
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

@extend_schema(
    tags=['ai'],
    summary='AI 방 비교 분석',
    description='AI를 사용하여 두 방을 비교 분석하고 더 나은 선택을 추천합니다.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'room_a_id': {
                    'type': 'integer',
                    'description': '비교할 첫 번째 방 ID',
                    'example': 1
                },
                'room_b_id': {
                    'type': 'integer',
                    'description': '비교할 두 번째 방 ID',
                    'example': 2
                },
                'comparison_criteria': {
                    'type': 'object',
                    'description': '비교 기준 가중치 (0.0 ~ 1.0)',
                    'properties': {
                        'price_weight': {
                            'type': 'number',
                            'description': '가격 중요도 (0.0 ~ 1.0)',
                            'example': 0.4,
                            'minimum': 0.0,
                            'maximum': 1.0
                        },
                        'location_weight': {
                            'type': 'number',
                            'description': '위치 중요도 (0.0 ~ 1.0)',
                            'example': 0.3,
                            'minimum': 0.0,
                            'maximum': 1.0
                        },
                        'area_weight': {
                            'type': 'number',
                            'description': '면적 중요도 (0.0 ~ 1.0)',
                            'example': 0.3,
                            'minimum': 0.0,
                            'maximum': 1.0
                        },
                        'transport_weight': {
                            'type': 'number',
                            'description': '교통편 중요도 (0.0 ~ 1.0)',
                            'example': 0.2,
                            'minimum': 0.0,
                            'maximum': 1.0
                        }
                    },
                    'example': {
                        'price_weight': 0.4,
                        'location_weight': 0.3,
                        'area_weight': 0.3
                    }
                },
                'user_preferences': {
                    'type': 'string',
                    'description': '사용자 선호사항 (자유 텍스트)',
                    'example': '가격이 중요하고, 교통편이 좋았으면 좋겠어요. 원룸이면 더 좋고요.',
                    'maxLength': 500
                }
            },
            'required': ['room_a_id', 'room_b_id']
        }
    },
    responses={
        201: {
            'description': 'AI 비교 분석 완료',
            'examples': [
                {
                    'id': 1,
                    'room_a': {
                        'id': 1,
                        'title': '강남 원룸',
                        'room_type': '원룸',
                        'monthly_fee': 500000,
                        'address': '강남구 역삼동'
                    },
                    'room_b': {
                        'id': 2,
                        'title': '마포 투룸',
                        'room_type': '투룸',
                        'monthly_fee': 700000,
                        'address': '마포구 합정동'
                    },
                    'comparison_criteria': {
                        'price_weight': 0.4,
                        'location_weight': 0.3,
                        'area_weight': 0.3
                    },
                    'analysis_summary': '강남 원룸이 가격 대비 효율성이 높고, 마포 투룸은 면적이 넓지만 월세가 높습니다.',
                    'detailed_comparison': {
                        'price_analysis': '강남 원룸이 월세 50만원으로 더 저렴',
                        'location_analysis': '강남구가 교통편이 더 편리',
                        'area_analysis': '마포 투룸이 면적이 더 넓음'
                    },
                    'recommendation': 'room_a',
                    'reasoning': '사용자의 가격 중요도(40%)를 고려할 때, 강남 원룸이 월세가 낮고 교통편도 좋아 더 적합합니다.',
                    'created_at': '2025-08-15T10:30:00Z',
                    'updated_at': '2025-08-15T10:30:00Z'
                }
            ]
        },
        400: {
            'description': '잘못된 요청',
            'examples': [
                {
                    'room_a_id': ['이 필드는 필수입니다.'],
                    'room_b_id': ['이 필드는 필수입니다.'],
                    'non_field_errors': ['같은 방을 비교할 수 없습니다.']
                }
            ]
        },
        404: {
            'description': '방을 찾을 수 없습니다',
            'examples': [
                {
                    'error': '방을 찾을 수 없습니다.'
                }
            ]
        },
        500: {
            'description': 'AI 분석 중 오류가 발생했습니다',
            'examples': [
                {
                    'error': 'AI 분석 중 오류가 발생했습니다: OpenAI API 키가 설정되지 않았습니다.'
                }
            ]
        }
    },
    examples=[
        OpenApiExample(
            '기본 비교 분석',
            value={
                'room_a_id': 1,
                'room_b_id': 2,
                'comparison_criteria': {
                    'price_weight': 0.4,
                    'location_weight': 0.3,
                    'area_weight': 0.3
                },
                'user_preferences': '가격이 중요하고, 교통편이 좋았으면 좋겠어요'
            },
            request_only=True,
        ),
        OpenApiExample(
            '가격 중심 비교',
            value={
                'room_a_id': 3,
                'room_b_id': 4,
                'comparison_criteria': {
                    'price_weight': 0.7,
                    'location_weight': 0.2,
                    'area_weight': 0.1
                },
                'user_preferences': '가격이 가장 중요해요. 월세가 낮은 방을 원해요.'
            },
            request_only=True,
        ),
    ]
)
class AIComparisonView(APIView):
    """
    AI를 사용하여 두 방을 비교 분석하는 API
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AIComparisonRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        room_a_id = serializer.validated_data['room_a_id']
        room_b_id = serializer.validated_data['room_b_id']
        comparison_criteria = serializer.validated_data.get('comparison_criteria', {})
        user_preferences = serializer.validated_data.get('user_preferences', '')
        
        try:
            room_a = Room.objects.get(id=room_a_id)
            room_b = Room.objects.get(id=room_b_id)
        except Room.DoesNotExist:
            return Response(
                {"error": "방을 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # real-estate.json 데이터 로드 (AI 분석용 참고 데이터)
        real_estate_data = self._load_real_estate_data()
        
        # AI 분석 실행
        try:
            analysis_result = self._analyze_with_ai(
                room_a, room_b, comparison_criteria, user_preferences, real_estate_data
            )
        except Exception as e:
            return Response(
                {"error": f"AI 분석 중 오류가 발생했습니다: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 결과 저장
        with transaction.atomic():
            report = AIComparisonReport.objects.create(
                user=request.user,
                room_a=room_a,
                room_b=room_b,
                comparison_criteria=comparison_criteria,
                analysis_summary=analysis_result['summary'],
                detailed_comparison=analysis_result['detailed_comparison'],
                recommendation=analysis_result['recommendation'],
                reasoning=analysis_result['reasoning']
            )
        
        return Response(
            AIComparisonReportSerializer(report).data,
            status=status.HTTP_201_CREATED
        )
    
    def _load_real_estate_data(self):
        """real-estate.json 파일에서 참고 데이터 로드"""
        try:
            json_path = os.path.join(settings.BASE_DIR, 'real-estate.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception:
            return []
    
    def _analyze_with_ai(self, room_a, room_b, comparison_criteria, user_preferences, real_estate_data):
        """OpenAI GPT를 사용하여 방 비교 분석"""
        # OpenAI API 키 설정
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise Exception("OpenAI API 키가 설정되지 않았습니다.")
        
        # 프롬프트 구성
        prompt = self._build_comparison_prompt(
            room_a, room_b, comparison_criteria, user_preferences, real_estate_data
        )
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 부동산 전문가입니다. 두 개의 방을 객관적으로 비교 분석하고, 사용자의 선호사항을 고려하여 더 나은 선택을 추천해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # AI 응답을 구조화된 형태로 파싱
            return self._parse_ai_response(ai_response, room_a, room_b)
            
        except Exception as e:
            raise Exception(f"OpenAI API 호출 실패: {str(e)}")
    
    def _build_comparison_prompt(self, room_a, room_b, comparison_criteria, user_preferences, real_estate_data):
        """AI 분석을 위한 프롬프트 구성"""
        
        # 방 정보 요약
        room_a_info = f"""
방 A: {room_a.title}
- 타입: {room_a.room_type or 'N/A'}
- 보증금: {room_a.deposit:,}원 (있을 경우)
- 월세: {room_a.monthly_fee:,}원
- 관리비: {room_a.maintenance_cost:,}원
- 면적: 공급 {room_a.supply_area}㎡, 전용 {room_a.real_area}㎡
- 층수: {room_a.floor or 'N/A'}
- 주소: {room_a.address or 'N/A'}
- 위치: 위도 {room_a.latitude}, 경도 {room_a.longitude}
"""
        
        room_b_info = f"""
방 B: {room_b.title}
- 타입: {room_b.room_type or 'N/A'}
- 보증금: {room_b.deposit:,}원 (있을 경우)
- 월세: {room_b.monthly_fee:,}원
- 관리비: {room_b.maintenance_cost:,}원
- 면적: 공급 {room_b.supply_area}㎡, 전용 {room_b.real_area}㎡
- 층수: {room_b.floor or 'N/A'}
- 주소: {room_b.address or 'N/A'}
- 위치: 위도 {room_b.longitude}, 경도 {room_b.longitude}
"""
        
        # 비교 기준
        criteria_text = ""
        if comparison_criteria:
            criteria_text = f"\n비교 기준: {json.dumps(comparison_criteria, ensure_ascii=False)}"
        
        # 사용자 선호사항
        preferences_text = ""
        if user_preferences:
            preferences_text = f"\n사용자 선호사항: {user_preferences}"
        
        # 시장 참고 데이터 (샘플)
        market_context = ""
        if real_estate_data:
            sample_rooms = real_estate_data[:3]  # 처음 3개 방만 참고
            market_context = f"\n\n시장 참고 데이터 (샘플):\n"
            for room in sample_rooms:
                market_context += f"- {room.get('제목', 'N/A')}: {room.get('월세', 'N/A')}원, {room.get('주소', 'N/A')}\n"
        
        prompt = f"""
다음 두 방을 비교 분석해주세요:

{room_a_info}

{room_b_info}
{criteria_text}
{preferences_text}
{market_context}

다음 형식으로 응답해주세요:

요약: [두 방의 주요 차이점을 간단히 요약]
상세비교: [가격, 위치, 면적, 편의성 등을 구체적으로 비교]
추천: [room_a 또는 room_b 중 하나 선택]
이유: [추천 이유를 구체적으로 설명]
"""
        
        return prompt
    
    def _parse_ai_response(self, ai_response, room_a, room_b):
        """AI 응답을 구조화된 형태로 파싱"""
        try:
            # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
            lines = ai_response.split('\n')
            summary = ""
            detailed_comparison = {}
            recommendation = ""
            reasoning = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('요약:'):
                    summary = line.replace('요약:', '').strip()
                elif line.startswith('상세비교:'):
                    detailed_comparison['comparison'] = line.replace('상세비교:', '').strip()
                elif line.startswith('추천:'):
                    rec = line.replace('추천:', '').strip().lower()
                    if 'room_a' in rec or '방 a' in rec:
                        recommendation = 'room_a'
                    elif 'room_b' in rec or '방 b' in rec:
                        recommendation = 'room_b'
                    else:
                        recommendation = 'room_a'  # 기본값
                elif line.startswith('이유:'):
                    reasoning = line.replace('이유:', '').strip()
            
            return {
                'summary': summary or "AI 분석 완료",
                'detailed_comparison': detailed_comparison,
                'recommendation': recommendation or 'room_a',
                'reasoning': reasoning or "종합적인 분석 결과"
            }
            
        except Exception:
            # 파싱 실패 시 기본값 반환
            return {
                'summary': ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                'detailed_comparison': {'raw_response': ai_response},
                'recommendation': 'room_a',
                'reasoning': "AI 분석 결과"
            }

@extend_schema(
    tags=['ai'],
    summary='AI 비교 분석 히스토리',
    description='사용자의 AI 비교 분석 히스토리를 조회합니다.',
    responses={
        200: {
            'description': 'AI 비교 분석 히스토리',
            'examples': [
                [
                    {
                        'id': 1,
                        'room_a': {
                            'id': 1,
                            'title': '강남 원룸',
                            'room_type': '원룸',
                            'monthly_fee': 500000,
                            'address': '강남구 역삼동'
                        },
                        'room_b': {
                            'id': 2,
                            'title': '마포 투룸',
                            'room_type': '투룸',
                            'monthly_fee': 700000,
                            'address': '마포구 합정동'
                        },
                        'comparison_criteria': {
                            'price_weight': 0.4,
                            'location_weight': 0.3,
                            'area_weight': 0.3
                        },
                        'analysis_summary': '강남 원룸이 가격 대비 효율성이 높습니다.',
                        'recommendation': 'room_a',
                        'created_at': '2025-08-15T10:30:00Z'
                    },
                    {
                        'id': 2,
                        'room_a': {
                            'id': 3,
                            'title': '홍대 원룸',
                            'room_type': '원룸',
                            'monthly_fee': 450000,
                            'address': '마포구 홍대입구'
                        },
                        'room_b': {
                            'id': 4,
                            'title': '신촌 투룸',
                            'room_type': '투룸',
                            'monthly_fee': 650000,
                            'address': '서대문구 신촌동'
                        },
                        'comparison_criteria': {
                            'price_weight': 0.6,
                            'location_weight': 0.2,
                            'area_weight': 0.2
                        },
                        'analysis_summary': '홍대 원룸이 월세가 가장 낮습니다.',
                        'recommendation': 'room_a',
                        'created_at': '2025-08-15T09:15:00Z'
                    }
                ]
            ]
        },
        401: {
            'description': '인증되지 않은 사용자',
            'examples': [
                {
                    'detail': '인증 자격이 제공되지 않았습니다.'
                }
            ]
        }
    }
)
class AIComparisonHistoryView(APIView):
    """사용자의 AI 비교 분석 히스토리 조회"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        reports = AIComparisonReport.objects.filter(user=request.user)
        serializer = AIComparisonReportSerializer(reports, many=True)
        return Response(serializer.data)

@extend_schema(
    tags=['ai'],
    summary='AI 비교 분석 리포트 상세',
    description='특정 AI 비교 분석 리포트의 상세 정보를 조회합니다.',
    parameters=[
        OpenApiParameter(name='report_id', description='리포트 ID', required=True, type=int),
    ],
    responses={
        200: {
            'description': 'AI 비교 분석 리포트 상세',
            'examples': [
                {
                    'id': 1,
                    'room_a': {
                        'id': 1,
                        'title': '강남 원룸',
                        'room_type': '원룸',
                        'deposit': 1000000,
                        'monthly_fee': 500000,
                        'maintenance_cost': 50000,
                        'supply_area': 25.5,
                        'real_area': 20.3,
                        'floor': '3층',
                        'contract_type': '월세',
                        'address': '강남구 역삼동',
                        'latitude': 37.5665,
                        'longitude': 126.9780
                    },
                    'room_b': {
                        'id': 2,
                        'title': '마포 투룸',
                        'room_type': '투룸',
                        'deposit': 1500000,
                        'monthly_fee': 700000,
                        'maintenance_cost': 80000,
                        'supply_area': 35.2,
                        'real_area': 28.7,
                        'floor': '5층',
                        'contract_type': '월세',
                        'address': '마포구 합정동',
                        'latitude': 37.5519,
                        'longitude': 126.9250
                    },
                    'comparison_criteria': {
                        'price_weight': 0.4,
                        'location_weight': 0.3,
                        'area_weight': 0.3
                    },
                    'analysis_summary': '강남 원룸이 가격 대비 효율성이 높고, 마포 투룸은 면적이 넓지만 월세가 높습니다.',
                    'detailed_comparison': {
                        'price_analysis': '강남 원룸이 월세 50만원으로 더 저렴하고, 보증금도 100만원으로 낮음',
                        'location_analysis': '강남구가 교통편이 더 편리하고, 역삼역까지 도보 5분 거리',
                        'area_analysis': '마포 투룸이 공급면적 35.2㎡, 전용면적 28.7㎡로 더 넓음',
                        'cost_efficiency': '강남 원룸이 월세 대비 효율성이 1.2배 높음'
                    },
                    'recommendation': 'room_a',
                    'reasoning': '사용자의 가격 중요도(40%)를 고려할 때, 강남 원룸이 월세가 낮고 교통편도 좋아 더 적합합니다. 또한 보증금도 50만원 낮아 초기 비용도 절약할 수 있습니다.',
                    'created_at': '2025-08-15T10:30:00Z',
                    'updated_at': '2025-08-15T10:30:00Z'
                }
            ]
        },
        404: {
            'description': '리포트를 찾을 수 없습니다',
            'examples': [
                {
                    'error': '리포트를 찾을 수 없습니다.'
                }
            ]
        },
        401: {
            'description': '인증되지 않은 사용자',
            'examples': [
                {
                    'detail': '인증 자격이 제공되지 않았습니다.'
                }
            ]
        }
    }
)
class AIComparisonDetailView(APIView):
    """특정 AI 비교 분석 리포트 상세 조회"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        try:
            report = AIComparisonReport.objects.get(id=report_id, user=request.user)
            serializer = AIComparisonReportSerializer(report)
            return Response(serializer.data)
        except AIComparisonReport.DoesNotExist:
            return Response(
                {"error": "리포트를 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )

@extend_schema(
    tags=['ai'],
    summary='북마크된 방들 조회 (비교용)',
    description='AI 비교 분석을 위해 북마크된 방들을 조회합니다. (임시로 비활성화)',
    responses={
        200: {
            'description': '북마크된 방 목록',
            'examples': [
                {
                    'bookmarked_rooms': [],
                    'total_count': 0,
                    'message': '북마크 기능이 아직 구현되지 않았습니다.'
                }
            ]
        }
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookmarked_rooms_for_comparison(request):
    """북마크된 방들을 비교 분석용으로 조회 (임시로 비활성화)"""
    # Bookmark 모델이 없어서 임시로 빈 응답
    return Response({
        'bookmarked_rooms': [],
        'total_count': 0,
        'message': '북마크 기능이 아직 구현되지 않았습니다.'
    })
