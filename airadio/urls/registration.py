from django.urls import re_path
from airadio.views.registration import *

urlpatterns = [
    re_path(
        r"^(?P<key>.+)/verify-email/$",
        EmailVerfiyView.as_view(),
        name="user-verify-email",
    ),
]
