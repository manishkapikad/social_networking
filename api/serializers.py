from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRequest

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "username"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
                raise serializers.ValidationError("unable to log in with the provided credentials.")
            else:
                if user.check_password(password):
                    if not user.is_active:
                        raise serializers.ValidationError("user account is not active.")
                else:
                    raise serializers.ValidationError(
                        "unable to log in with the provided credentials."
                    )
        else:
            raise serializers.ValidationError("both email and password are required.")
        data["user"] = user
        return data


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("email address already in use")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = "__all__"


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = "__all__"


class AcceptRejectFriendRequestSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=(("accepted", "Accepted"), ("rejected", "Rejected")),
        required=True,
    )

    class Meta:
        model = FriendRequest
        fields = ["status"]
        extra_kwargs = {"status": {"required": True}}


class SendFriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    to_user_id = serializers.IntegerField(required=True)

    class Meta:
        model = FriendRequest
        fields = ["to_user_id", "from_user"]

    def validate_to_user_id(self, value):
        authenticated_user_id = self.context["request"].user.id
        if value == authenticated_user_id:
            raise serializers.ValidationError("you cannot send a friend request to yourself.")
        existing_request_from_to = FriendRequest.objects.filter(
            from_user_id=authenticated_user_id, to_user_id=value
        ).exists()

        existing_request_to_from = FriendRequest.objects.filter(
            from_user_id=value, to_user_id=authenticated_user_id
        ).exists()
        if existing_request_from_to or existing_request_to_from:
            raise serializers.ValidationError("A friend request to this user already exists.")
        try:
            user = User.objects.get(id=value)
        except Exception:
            raise serializers.ValidationError("invalid user ID provided.")
        return value
