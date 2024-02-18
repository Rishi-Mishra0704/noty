from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from .serializers import UserSerializer

@api_view(['POST'])
def login(request):
    """
    Authenticate user and generate token for login.

    Args:
        request: HTTP request object containing username and password.

    Returns:
        HTTP response with authentication token and user data if login successful,
        else returns error response with status code 400.
    """
    try:
        user = get_object_or_404(User, username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response({'detail': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(instance=user)
        return Response({'token': token.key, 'user': serializer.data})
    except:
        return Response({'detail': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def signup(request):
    """
    Register a new user.

    Args:
        request: HTTP request object containing user data for registration.

    Returns:
        HTTP response with authentication token if signup successful,
        else returns error response with status code 400.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
