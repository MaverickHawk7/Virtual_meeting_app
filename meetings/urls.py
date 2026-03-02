from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Auth
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Meetings
    path("meetings/", views.MeetingListCreateView.as_view(), name="meeting-list-create"),
    path("meetings/<uuid:meeting_id>/join/", views.MeetingJoinView.as_view(), name="meeting-join"),
    path("meetings/<uuid:meeting_id>/leave/", views.MeetingLeaveView.as_view(), name="meeting-leave"),
    path("meetings/<uuid:meeting_id>/end/", views.MeetingEndView.as_view(), name="meeting-end"),
    path("meetings/<uuid:meeting_id>/participants/", views.MeetingParticipantsView.as_view(), name="meeting-participants"),
]
