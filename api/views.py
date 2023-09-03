import datetime
import logging
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.decorators import permission_classes

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (
    LoginSerializer,
    SignupSerializer,
    FriendRequestSerializer,
    UserSerializer,
    FriendsSerializer,
    AcceptRejectFriendRequestSerializer,
    SendFriendRequestSerializer,
)
from .models import FriendRequest
from .custom_throttle_rate import SendFriendRequestRateThrottle

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _ = Token.objects.get_or_create(user=user)
            response = {"token": token.key}
            if token.created < datetime.datetime.now() - datetime.timedelta(
                hours=getattr(settings, "REST_FRAMEWORK_TOKEN_EXPIRE_HOURS", 24)
            ):
                token.delete()
                token, _ = Token.objects.get_or_create(user=user)
                response = {"token": token.key}
            return Response(response)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "signup successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendFriendRequest(APIView):
    throttle_classes = [SendFriendRequestRateThrottle]

    def post(self, request):
        serializer = SendFriendRequestSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            instance = serializer.save()
            serializer = FriendRequestSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptRejectFriendRequest(APIView):
    def patch(self, request, request_id):
        instance = get_object_or_404(
            FriendRequest,
            to_user=request.user,
            pk=request_id,
            status="pending",
        )
        serializer = AcceptRejectFriendRequestSerializer(instance, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            serializer = FriendRequestSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPendingFriendRequests(ListAPIView):
    serializer_class = FriendsSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status="pending")


class ListFriends(APIView):
    def get(self, request):
        friends = FriendRequest.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user), status="accepted"
        ).distinct()
        friend_users = []
        for friend_request in friends:
            if friend_request.from_user == request.user:
                friend_users.append(friend_request.to_user)
            else:
                friend_users.append(friend_request.from_user)
        serializer = UserSerializer(friend_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if re.match(pattern, email):
        return True
    else:
        return False


class UserSearch(ListAPIView):
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        keyword = self.request.query_params.get("q", "")
        if is_valid_email(keyword):
            user = (
                User.objects.filter(email__iexact=keyword).exclude(id=self.request.user.id).first()
            )
            if user:
                return [user]
            else:
                return []
        else:
            return User.objects.filter(
                Q(first_name__icontains=keyword)
                | Q(last_name__icontains=keyword)
                | Q(email__icontains=keyword)
            ).exclude(id=self.request.user.id)
