from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import SignupSerializer, UserSerializer

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def signup(request):
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

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request):
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
