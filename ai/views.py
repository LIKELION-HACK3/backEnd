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

class AIComparisonHistoryView(APIView):
    """사용자의 AI 비교 분석 히스토리 조회"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        reports = AIComparisonReport.objects.filter(user=request.user)
        serializer = AIComparisonReportSerializer(reports, many=True)
        return Response(serializer.data)

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
