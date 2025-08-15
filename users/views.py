from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import SignupSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

@extend_schema(
    tags=['users'],
    summary='회원가입',
    description='새로운 사용자 계정을 생성합니다.',
    examples=[
        OpenApiExample(
            '회원가입 예시',
            value={
                'username': 'tester1',
                'email': 'tester1@example.com',
                'password': 'Passw0rd!123',
                'password_confirm': 'Passw0rd!123'
            },
            request_only=True,
        ),
    ],
    responses={
        201: UserSerializer,
        400: '유효성 검사 실패'
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def signup(request):
    """
    회원가입 API
    
    - GET: 회원가입 폼 정보 제공
    - POST: 새로운 사용자 계정 생성
    """
    if request.method == 'GET':
        return Response({
            'message': '회원가입 API',
            'method': 'POST',
            'fields': ['username', 'email', 'password', 'password_confirm']
        })
    
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': '회원가입이 완료되었습니다.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['users'],
    summary='로그인',
    description='사용자 인증 후 JWT 토큰을 발급합니다.',
    examples=[
        OpenApiExample(
            '로그인 예시',
            value={
                'username': 'tester1',
                'password': 'Passw0rd!123'
            },
            request_only=True,
        ),
    ],
    responses={
        200: UserSerializer,
        401: '인증 실패',
        400: '잘못된 요청'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request):
    """
    로그인 API
    
    사용자명과 비밀번호로 인증 후 JWT 토큰을 발급합니다.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': '로그인 성공',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        else:
            return Response({
                'error': '아이디 또는 비밀번호가 잘못되었습니다.'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        'error': '아이디와 비밀번호를 입력해주세요.'
    }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['users'],
    summary='내 정보 조회',
    description='현재 로그인한 사용자의 정보를 조회합니다.',
    responses={
        200: UserSerializer,
        401: '인증되지 않은 사용자'
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    내 정보 조회 API
    
    JWT 토큰을 통해 인증된 사용자의 정보를 반환합니다.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
