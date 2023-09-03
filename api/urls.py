"""txagentconsole URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.urls import path

from .views import (
    LoginView,
    SignupView,
    SendFriendRequest,
    AcceptRejectFriendRequest,
    ListPendingFriendRequests,
    ListFriends,
    UserSearch,
)

app_name = "api"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("search/", UserSearch.as_view(), name="user-search"),
    path("send-friend-request/", SendFriendRequest.as_view(), name="send_friend_request"),
    path(
        "handle-friend-request/<int:request_id>/",
        AcceptRejectFriendRequest.as_view(),
        name="handle_friend_request",
    ),
    path(
        "pending-friends-list/",
        ListPendingFriendRequests.as_view(),
        name="list-pending-friends-list",
    ),
    path("list-friends/", ListFriends.as_view(), name="list-friends"),
]
