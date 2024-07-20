from django.urls import re_path
from airadio.views.api_v2 import *
from airadio.views.decorators import token_required

urlpatterns = [
    re_path(r"^$", Index.as_view(), name="api_index"),
    re_path(r"^get-station-list/", StationList.as_view(), name="api_station_list"),
    re_path(r"^get-music/", Music.as_view(), name="api_music"),
    re_path(r"^add-library/", AddLibrary.as_view(), name="api_add_library"),
    re_path(r"^get-retail-music/", RetailMusic.as_view(), name="api_retail_music"),
    re_path(r"^get-branding/", Branding.as_view(), name="api_branding"),
    re_path(r"^get-advert/", Advert.as_view(), name="api_advert"),
    re_path(r"^music-search/", MusicSearch.as_view(), name="api_music_search"),
    re_path(r"^get-soundwall/", SoundWall.as_view(), name="api_soundwall"),
    re_path(
        r"^get-station-banners/", StationBanners.as_view(), name="api_stationbanners"
    ),
    re_path(r"^get-user-info/", UserInfo.as_view(), name="api_user_info"),
    re_path(r"^get-social-codes/", StationSocialCode.as_view(), name="api_get_codes"),
    # Analytics
    re_path(
        r"^update-analytics/", UpdateAnalytics.as_view(), name="api_update_analytics"
    ),
    re_path(
        r"^update-tsu-per-station/", UpdateTSUPerStation.as_view(), name="api_update_tsu"
    ),
    re_path(
        r"^update-music-research/",
        UpdateMusicResearch.as_view(),
        name="api_update_musicresearch",
    ),
    re_path(
        r"^update-realtime-skip/",
        UpdateRealTimeSkip.as_view(),
        name="api_update_realtime",
    ),
    re_path(
        r"^update-dashboard-topsongs/",
        UpdateDashboardTopSongs.as_view(),
        name="api_update_dashboard_topsongs",
    ),
    re_path(
        r"^add-device-token/", AddInstallation.as_view(), name="api_add_device_token"
    ),
    # DJ
    re_path(r"^dj-signup/", DJUserSignup.as_view(), name="api_dj_signup"),
    re_path(r"^dj-login/", DJUserLogin.as_view(), name="api_dj_login"),
    re_path(
        r"^dj-check-emailverified/",
        token_required(CheckUserEmailVerified.as_view()),
        name="api_dj_check_email_verified",
    ),
    re_path(r"^reset-password/", DJPasswordReset.as_view(), name="api_password_reset"),
    re_path(
        r"^dj-add-content/",
        token_required(DJAddContent.as_view()),
        name="api_dj_add_content",
    ),
    re_path(
        r"^user-activity/(?P<type>.+)/",
        token_required(FollowUnfollowUser.as_view()),
        name="api_user_activity",
    ),
    re_path(r"^get-dj-tracks/", StationDJContent.as_view(), name="api_dj_tracks"),
    re_path(r"^station-dj-users/", StationDJUsers.as_view(), name="api_station_dj_users"),
    re_path(r"^get-tags/", GetDJTags.as_view(), name="api_get_tags"),
    re_path(r"^get-music-beds/", GetDJMusicbeds.as_view(), name="api_get_musicbeds"),
    re_path(r"^set-reputation/", DJSetReputation.as_view(), name="api_set_reputation"),
    re_path(
        r"^set-subscription/", DJSetSubscription.as_view(), name="api_set_subscription"
    ),
    re_path(
        r"^get-subscription/",
        token_required(DJGetSubscription.as_view()),
        name="api_get_subscription",
    ),
    re_path(
        r"^confirm-password/(?P<uidb36>[0-9a-zA-Z]{1,13})-(?P<token>.+)$",
        DJPasswordResetConfirm.as_view(),
        name="api_password_reset_confirm",
    ),
    re_path(r"^add-media-wall/", AddMediaWall.as_view(), name="api_add_media_wall"),
]
