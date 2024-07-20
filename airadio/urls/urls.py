from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import re_path

from airadio.views.viveca_dashboard import *

urlpatterns = [
    re_path(
        r"^$",
        login_required(DashboardView.as_view(), login_url="/login/"),
        name="viveca_dashboard",
    ),
    re_path(r"^login/$", LoginView.as_view(), name="viveca_dashboard_login"),
    re_path(
        r"^user-logout/$",
        LogoutView.as_view(next_page="/login/"),
        name="viveca_dashboard_logout",
    ),
    re_path(
        r"^analytics/$",
        login_required(AnalyticsView.as_view(), login_url="/login/"),
        name="viveca_dashboard_analytics",
    ),
    re_path(
        r"^library/$",
        login_required(LibraryView.as_view(), login_url="/login/"),
        name="viveca_dashboard_library",
    ),
    re_path(
        r"^add-to-library/$",
        login_required(AddToLibraryView.as_view(), login_url="/login/"),
        name="viveca_dashboard_library_add",
    ),
    re_path(
        r"^library-upload-media/$",
        login_required(MediaUploadView.as_view(), login_url="/login/"),
        name="viveca_dashboard_upload_media",
    ),
    re_path(
        r"^edit-library/$",
        login_required(EditLibraryPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_edit_library_popup",
    ),
    re_path(
        r"^library/edit/(?P<pk>\d+)/$",
        login_required(EditLibraryView.as_view(), login_url="/login/"),
        name="viveca_dashboard_edit_library",
    ),
    re_path(
        r"^library/update-station-points/$",
        login_required(UpdateStationPointsView.as_view(), login_url="/login/"),
        name="viveca_dashboard_library_update_station_points",
    ),
    re_path(
        r"^library/add-to-station/$",
        login_required(AddToStationView.as_view(), login_url="/login/"),
        name="viveca_dashboard_library_add_to_station",
    ),
    re_path(
        r"^library/generate-playlist/$",
        login_required(LibraryGeneratePlaylist.as_view(), login_url="/login/"),
        name="viveca_dashboard_library_generate_playlist",
    ),
    re_path(
        r"^library/search/discogs/$",
        login_required(SearchDiscogs.as_view(), login_url="/login/"),
        name="viveca_dashboard_library_search_discogs",
    ),
    re_path(
        r"^podcasts/$",
        login_required(PodcastsView.as_view(), login_url="/login/"),
        name="viveca_dashboard_podcasts",
    ),
    re_path(
        r"^schedule/$",
        login_required(ScheduleView.as_view(), login_url="/login/"),
        name="viveca_dashboard_schedule",
    ),
    re_path(
        r"^add-schedule/$",
        login_required(AddScheduleView.as_view(), login_url="/login/"),
        name="viveca_dashboard_schedule_add",
    ),
    re_path(
        r"^ajax-schedule/$",
        login_required(ScheduleAjaxView.as_view(), login_url="/login/"),
        name="viveca_dashboard_schedule_ajax",
    ),
    re_path(
        r"^edit-schedule/(?P<pk>\d+)/$",
        login_required(EditScheduleView.as_view(), login_url="/login/"),
        name="viveca_dashboard_schedule_edit",
    ),
    re_path(
        r"^schedule/branding/toh/add/$",
        login_required(AddBrandingTOHView.as_view(), login_url="/login/"),
        name="viveca_dashboard_add_schedule_branding_toh",
    ),
    re_path(
        r"^schedule/branding/toh/edit/popup/$",
        login_required(EditBrandingTOHPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_edit_schedule_branding_toh_popup",
    ),
    re_path(
        r"^schedule/branding/toh/edit/(?P<pk>\d+)/$",
        login_required(EditBrandingTOHView.as_view(), login_url="/login/"),
        name="viveca_dashboard_edit_schedule_branding_toh",
    ),
    re_path(
        r"^advert/$",
        login_required(AdvertView.as_view(), login_url="/login/"),
        name="viveca_dashboard_advert",
    ),
    re_path(
        r"^advert/add/$",
        login_required(AddAdvertView.as_view(), login_url="/login/"),
        name="viveca_dashboard_advert_add",
    ),
    re_path(
        r"^advert/edit/popup/$",
        login_required(EditAdvertPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_advert_edit_popup",
    ),
    re_path(
        r"^advert/edit/(?P<pk>\d+)/$",
        login_required(EditAdvertView.as_view(), login_url="/login/"),
        name="viveca_dashboard_advert_edit",
    ),
    re_path(
        r"^advert/ajax/$",
        login_required(AdvertAjaxView.as_view(), login_url="/login/"),
        name="viveca_dashboard_ajax_advert",
    ),
    re_path(
        r"^playlist/$",
        login_required(PlaylistView.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_playlist",
    ),
    re_path(
        r"^playlist/search$",
        login_required(PlaylistSearch.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_playlist_search",
    ),
    re_path(
        r"^playlist/insert$",
        login_required(PlaylistInsertToPlaylist.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_playlist_insert",
    ),
    re_path(
        r"^playlist-export/$",
        login_required(PlaylistExportView.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_playlist_export",
    ),
    re_path(
        r"^playlist/social/popup/$",
        login_required(PopupSocialPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_playlist_social_popup",
    ),
    re_path(
        r"^playlist/social/add/$",
        login_required(AddSocialPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_playlist_social_add",
    ),
    re_path(
        r"^playlist/social/fetch-post-data/$",
        login_required(PlaylistSocialPostData.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_playlist_social_fetch_post_data",
    ),
    re_path(
        r"^playlist/update/(?P<pk>\d+)/$",
        login_required(UpdateSocialPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_playlist_social_update",
    ),
    re_path(
        r"^ai-voicetracks/$",
        login_required(AiVoicetracksView.as_view(), login_url="/login/"),
        name="viveca_dashboard_ai_voicetracks",
    ),
    re_path(
        r"^ai-voicetracks/generate-voicetrack/$",
        login_required(
            AiVoicetracksGenerateVoicetrackView.as_view(), login_url="/login/"
        ),
        name="viveca_dashboard_ai_voicetracks_generate_voicetrack",
    ),
    re_path(
        r"^ai-voicetracks/in-aux/$",
        login_required(AiVoicetracksEditInAux.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_dj_inaux",
    ),
    re_path(
        r"^ai-voicetracks/music-beds/$",
        login_required(AiVoicetracksAddMusicBed.as_view(), login_url="/login/"),
        name="viveca_dashboard_reports_dj_musicbeds",
    ),
    re_path(
        r"^news/$",
        login_required(NewsView.as_view(), login_url="/login/"),
        name="viveca_dashboard_news",
    ),
    re_path(
        r"^news/generate-news-audio/$",
        login_required(GenerateNewsAudio.as_view(), login_url="/login/"),
        name="news_generate_news_audio",
    ),
    re_path(
        r"^news/export-news-audio/$",
        login_required(ExportNewsAudio.as_view(), login_url="/login/"),
        name="news_export_news_audio",
    ),
    re_path(
        r"^news/add-news-to-playlist/$",
        login_required(AddNewsToPlaylist.as_view(), login_url="/login/"),
        name="news_add_news_to_playlist",
    ),
    re_path(
        r"^setting/user/$",
        login_required(SettingUserView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_user",
    ),
    re_path(
        r"^setting/user/add/$",
        login_required(AddSettingUserView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_user_add",
    ),
    re_path(
        r"^setting/user/edit/popup/$",
        login_required(EditSettingUserPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_user_edit_popup",
    ),
    re_path(
        r"^setting/user/edit/(?P<pk>\d+)/$",
        login_required(UpdateSettingUserView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_user_edit",
    ),
    re_path(
        r"^setting/station/$",
        login_required(SettingStationView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_station",
    ),
    re_path(
        r"^setting/station/add/$",
        login_required(AddSettingStationView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_station_add",
    ),
    re_path(
        r"^setting/station/edit/popup/$",
        login_required(EditSettingStationPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_station_edit_popup",
    ),
    re_path(
        r"^setting/station/edit/(?P<pk>\d+)/$",
        login_required(UpdateSettingStationView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_station_edit",
    ),
    re_path(
        r"^setting/location/$",
        login_required(SettingLocationView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_location",
    ),
    re_path(
        r"^setting/location/add/$",
        login_required(AddSettingLocationView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_location_add",
    ),
    re_path(
        r"^setting/location/edit/popup/$",
        login_required(EditSettingLocationPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_edit_location_popup",
    ),
    re_path(
        r"^setting/location/edit/(?P<pk>\d+)/$",
        login_required(UpdateSettingLocationView.as_view(), login_url="/login/"),
        name="viveca_dashboard_location_edit",
    ),
    re_path(
        r"^setting/sequence/$",
        login_required(SettingSequenceView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_sequence",
    ),
    re_path(
        r"^setting/sequence/ajax/$",
        login_required(SettingSequenceAjaxView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_sequence_ajax",
    ),
    re_path(
        r"^setting/genres/$",
        login_required(SettingGenresView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_genres",
    ),
    re_path(
        r"^setting/genres/add/$",
        login_required(AddSettingGenresView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_genres_add",
    ),
    re_path(
        r"^setting/genres/edit/popup/$",
        login_required(EditSettingGenresPopupView.as_view(), login_url="/login/"),
        name="viveca_dashboard_setting_genre_edit_popup",
    ),
    re_path(
        r"^setting/genres/edit/(?P<pk>\d+)/$",
        login_required(UpdateSettingGenresView.as_view(), login_url="/login/"),
        name="viveca_dashboard_genre_edit",
    ),
    # Get Data
    re_path(
        r"^get-player-content-data/",
        staff_member_required(MediaContentData.as_view()),
        name="viveca_dashboard_player_content_data",
    ),
    re_path(
        r"^generate-news/", GenerateAIStoryView.as_view(), name="viveca_generate_news"
    ),
]
