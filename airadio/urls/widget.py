from django.urls import include, path, re_path
from django.views.decorators.cache import cache_page
from airadio.views.widget import *
from airadio.views.decorators import check_authorized

urlpatterns = [
    re_path(
        r"^get-station-list/", WidgetStationList.as_view(), name="widget_station_list"
    ),
    re_path(
        r"^get-station-playlist/",
        WidgetStationPlaylist.as_view(),
        name="widget_station_playlist",
    ),
    re_path(
        r"^get-content-data/(?P<slug>[\w-]*)/",
        cache_page(60 * 60)(check_authorized(WidgetContentData.as_view())),
        name="widget_content_data",
    ),
]
