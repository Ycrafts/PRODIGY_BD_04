from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['username',"id", 'name', "password",'email', 'age']
        model = CustomUser
        