from rest_framework.throttling import UserRateThrottle


class SendFriendRequestRateThrottle(UserRateThrottle):
    rate = "3/minute"
