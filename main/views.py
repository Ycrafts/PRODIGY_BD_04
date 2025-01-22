from django.shortcuts import render
from .serializers import CustomUserSerializer
from .models import CustomUser
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .permissions import CustomUserPermission
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [CustomUserPermission]
    
    
    def get_permissions(self):
        if self.action in ['signup', 'login']:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Invalidate the specific cache for the object and the list view
        from django.core.cache import cache
        cache_key_list = 'cachApp:views.decorators.cache.cache_page.GET.users'
        cache_key_detail = f'cachApp:views.decorators.cache.cache_page.GET.users.{kwargs["pk"]}'
        cache.delete(cache_key_list)
        cache.delete(cache_key_detail)
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Invalidate the specific cache for the object and the list view
        from django.core.cache import cache
        cache_key_list = 'cachApp:views.decorators.cache.cache_page.GET.users'
        cache_key_detail = f'cachApp:views.decorators.cache.cache_page.GET.users.{kwargs["pk"]}'
        cache.delete(cache_key_list)
        cache.delete(cache_key_detail)
        return response

    
    # @method_decorator(cache_page(60 * 15))  #15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))  #15 minutes
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    #block the create logic in the viewset
    def create(self, request, *args, **kwargs):
        return Response(
            {"error": "This action is not allowed. Use the /api/users/signup/ endpoint to create a new user."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            from django.core.cache import cache
            cache_key_list = 'cachApp:views.decorators.cache.cache_page.GET.users'
            cache.delete(cache_key_list)
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({"error":"Username and Password are required"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)