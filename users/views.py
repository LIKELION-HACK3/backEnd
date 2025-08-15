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
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string',
                    'description': '사용자명 (고유해야 함)',
                    'example': 'tester1'
                },
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'description': '이메일 주소 (고유해야 함)',
                    'example': 'tester1@example.com'
                },
                'password': {
                    'type': 'string',
                    'description': '비밀번호',
                    'example': 'Passw0rd!123'
                },
                'password_confirm': {
                    'type': 'string',
                    'description': '비밀번호 확인',
                    'example': 'Passw0rd!123'
                }
            },
            'required': ['username', 'email', 'password', 'password_confirm']
        }
    },
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
        201: {
            'description': '회원가입 성공',
            'examples': [
                {
                    'message': '회원가입이 완료되었습니다.',
                    'user': {
                        'id': 1,
                        'username': 'tester1',
                        'email': 'tester1@example.com',
                        'created_at': '2025-08-15T07:56:19.785Z'
                    },
                    'tokens': {
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            ]
        },
        400: {
            'description': '유효성 검사 실패',
            'examples': [
                {
                    'username': ['이미 사용 중인 사용자명입니다.'],
                    'email': ['이미 사용 중인 이메일입니다.'],
                    'password_confirm': ['비밀번호가 일치하지 않습니다.']
                }
            ]
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def signup(request):
    """
    회원가입 API
    
    새로운 사용자 계정을 생성하고 JWT 토큰을 발급합니다.
    """
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
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string',
                    'description': '사용자명',
                    'example': 'tester1'
                },
                'password': {
                    'type': 'string',
                    'description': '비밀번호',
                    'example': 'Passw0rd!123'
                }
            },
            'required': ['username', 'password']
        }
    },
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
        200: {
            'description': '로그인 성공',
            'examples': [
                {
                    'message': '로그인 성공',
                    'user': {
                        'id': 1,
                        'username': 'tester1',
                        'email': 'tester1@example.com',
                        'created_at': '2025-08-15T07:56:19.785Z'
                    },
                    'tokens': {
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            ]
        },
        401: {
            'description': '인증 실패',
            'examples': [
                {
                    'error': '아이디 또는 비밀번호가 잘못되었습니다.'
                }
            ]
        },
        400: {
            'description': '잘못된 요청',
            'examples': [
                {
                    'error': '아이디와 비밀번호를 입력해주세요.'
                }
            ]
        }
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
