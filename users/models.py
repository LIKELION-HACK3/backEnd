from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 이메일로 로그인할 수 있도록 설정
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.username
