import base64
import time
import requests
import logging
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
from django.db.models import Q
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import base36_to_int
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.sites.models import Site
from .Response import GenericResponse
from .BaseView import APIBaseView
from django.contrib.auth import authenticate
from airadio.models import (
    Library,
    Stations,
    Locations,
    BrandingTOH,
    Adverts,
    DJUser,
    Analytics,
    TSUPerStation,
    Dashboard,
    MusicResearchLibrary,
    MusicResearchData,
    RealTimeSkipLibrary,
    RealTimeSkipData,
    DashboardTopSongs,
    DJTag,
    DJReputation,
    DJStationStatus,
    MarketStations,
    StationPlaylistSocialCode,
    UserActivity,
    Installation,
)
from airadio.forms import DJTracksForm, DJUserSignupForm, PasswordResetForm
from airadio.forms import DashboardLibraryForm, DashboardWallForm
from mailer.tasks import send_all
from utils.views import JSONResponseMixin


logger = logging.getLogger(__name__)


def milliseconds_to_seconds(ms):
    return int(ms) / 1000.00 if ms else 0


def calculate_seconds(time):
    time_array = time.split(":")
    ms = 0
    try:
        h_s = int(time_array[0]) * 60 * 60
        m_s = int(time_array[1]) * 60
        s_s = int(time_array[2])
        if time_array[3:]:
            ms = str(h_s + m_s + s_s) + "." + time_array[3]
        else:
            ms = str(h_s + m_s + s_s) + ".00"
    except:
        return 0
    return int(float(ms) * 1000.00)


class Index(APIBaseView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        """
        Simple GET request. Returns a JSON response API Index.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        data = {}
        data["-version"] = "1.0"
        data["-rev"] = (
            "$Rev: 9828 $ $Date: "
            + str(timezone.now().date())
            + " "
            + str(timezone.now().time())
            + " ("
            + str(timezone.now().strftime("%A, %d %B,%Y"))
            + ")$"
        )
        data["localization"] = {"country": {"-cn": "US"}}
        site = []
        site.append(
            {
                "apiName": "GetStationJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-station-list/",
                "requestMethod": "GET",
                "paremeters": "",
            }
        )
        site.append(
            {
                "apiName": "GetStationPlaylistSocialCodesJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-social-codes/",
                "requestMethod": "GET/POST",
                "paremeters": "station_id,longitude,latitude",
            }
        )
        site.append(
            {
                "apiName": "GetMusicJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-music/",
                "requestMethod": "POST",
                "paremeters": "station_id",
            }
        )
        site.append(
            {
                "apiName": "GetRetailMusicJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-retail-music/",
                "requestMethod": "POST",
                "paremeters": "retail_code",
            }
        )
        site.append(
            {
                "apiName": "GetBrandingJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-branding/",
                "requestMethod": "POST",
                "paremeters": "station_id,location",
            }
        )
        site.append(
            {
                "apiName": "GetAdvertJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-advert/",
                "requestMethod": "POST",
                "paremeters": "location",
            }
        )
        site.append(
            {
                "apiName": "MusicSearchJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/music-search/",
                "requestMethod": "POST",
                "paremeters": "q",
            }
        )
        site.append(
            {
                "apiName": "SoundWallJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-soundwall/",
                "requestMethod": "POST",
                "paremeters": "channel_id",
            }
        )
        site.append(
            {
                "apiName": "DjUserSignup",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/dj-signup/",
                "requestMethod": "POST",
                "paremeters": "username , email, password, first_name, last_name, station, photo",
            }
        )
        site.append(
            {
                "apiName": "DjUserLogin",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/dj-login/",
                "requestMethod": "POST",
                "paremeters": "username , password",
            }
        )
        site.append(
            {
                "apiName": "DjSetReputation",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/set-reputation/",
                "requestMethod": "POST",
                "paremeters": "djid , type",
            }
        )
        site.append(
            {
                "apiName": "DjSetSubscription",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/set-subscription/",
                "requestMethod": "POST",
                "paremeters": "token , djid, station_id",
            }
        )
        site.append(
            {
                "apiName": "DjGetSubscription",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-subscription/",
                "requestMethod": "POST",
                "paremeters": "token , djid, station_id",
            }
        )
        site.append(
            {
                "apiName": "DjUserPostTrack",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/dj-add-content/",
                "requestMethod": "POST",
                "paremeters": "token , media, recorded, cover_art, title, tags, in_point, aux_point",
            }
        )
        site.append(
            {
                "apiName": "GetDJTracksJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-dj-tracks/",
                "requestMethod": "POST",
                "paremeters": "djids,stationID,tags",
            }
        )
        site.append(
            {
                "apiName": "UpdateAnalyticsJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/update-analytics/",
                "requestMethod": "POST",
                "paremeters": "unique_users,current_users,cloud_files,db_load,male,female,iphone,android,web_palyer",
            }
        )
        site.append(
            {
                "apiName": "UpdateTSUperStationJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/update-tsu-per-station/",
                "requestMethod": "POST",
                "paremeters": "station_id,total_users,avg_per_head,avg_hour_per_user,total_hours",
            }
        )
        site.append(
            {
                "apiName": "UpdateMusicResearchJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/update-music-research/",
                "requestMethod": "POST",
                "paremeters": "library_id , value",
            }
        )
        site.append(
            {
                "apiName": "UpdateRealtimeSkipJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/update-realtime-skip/",
                "requestMethod": "POST",
                "paremeters": "library_id , value",
            }
        )
        site.append(
            {
                "apiName": "UpdateDashboardTopSongs",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/update-dashboard-topsongs/",
                "requestMethod": "POST",
                "paremeters": "library_id , instagram, rating",
            }
        )
        site.append(
            {
                "apiName": "StationBannersJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-station-banners/",
                "requestMethod": "POST",
                "paremeters": "station_id , bannerType",
            }
        )
        site.append(
            {
                "apiName": "UsersInfoJSON",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-user-info/",
                "requestMethod": "POST",
                "paremeters": "username",
            }
        )
        site.append(
            {
                "apiName": "GetDJList",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/station-dj-users/",
                "requestMethod": "POST",
                "paremeters": "station_id",
            }
        )
        site.append(
            {
                "apiName": "GetDJTags",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-tags/",
                "requestMethod": "GET",
                "paremeters": "",
            }
        )
        site.append(
            {
                "apiName": "GetDJMusicbeds",
                "requestUrl": "https://cms.radiostation.ai/api/v2.0/get-music-beds/",
                "requestMethod": "GET",
                "paremeters": "station_id",
            }
        )
        site.append(
            {
                "mediaRoot": {
                    "-src": getattr(settings, "RACKSPACE_CONTAINER_URL", ""),
                    "-extension": ".M4A.64.MP4",
                }
            }
        )
        data["site"] = site
        result["index"] = data

        response = GenericResponse(
            meta={"description": "Response for API Index."}, result=result, error=error
        )

        return response


class StationList(APIBaseView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        """
        Simple GET request. Returns a JSON response for all Stations List.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        market = request.GET.get("market-key")
        stations = []
        results = []
        if market:
            try:
                #                print market
                market_object = MarketStations.objects.get(key=market)
                #                print market_object
                market_stations_ids = market_object.stations.all().values_list(
                    "id", flat=True
                )
                #                print market_stations_ids
                stations = (
                    Stations.objects.filter(published=True)
                    .exclude(retail=True)
                    .filter(id__in=market_stations_ids)
                )
                for station in stations:
                    results.append(self.get_response_list(station))
            except Exception as e:
                #                print 'Error :',e
                pass
        else:
            stations = Stations.objects.filter(published=True).filter(
                station_markets__isnull=True
            )
            for station in stations:
                # if not station.station_markets.all():
                results.append(self.get_response_list(station))
        result["Stations"] = results
        response = GenericResponse(
            meta={"description": "Response for Station List JSON."},
            result=result,
            error=error,
        )
        return response

    def get_response_list(self, station):
        locations = station.location.all()
        location = []
        for loc in locations:
            location.append(
                {
                    "name": loc.location_city,
                    "longitude": str(loc.location_long),
                    "latitude": str(loc.location_lat),
                }
            )
        data = {
            "station_id": station.pk,
            "location": location,
            "name": station.station_name,
            "preview": station.station_preview.url if station.station_preview else "",
            "logo": station.station_logo.url if station.station_logo else "",
            "description": station.station_description,
            "retail": {
                "status": station.retail,
                "code": station.retailcode if station.retail else "",
            },
            "streaming": {
                "status": station.streaming,
                "url": station.stream_url if station.streaming else "",
            },
            "microsite": station.microsite if station.microsite else "",
        }
        return data


class StationSocialCode(APIBaseView):
    http_method_names = ["post", "get"]

    def get(self, request, *args, **kwargs):
        result = {}
        error = {"code": 200, "description": "Successful"}
        station_id = request.GET.get("station_id", None)
        lat = request.GET.get("latitude", None)
        longi = request.GET.get("longitude", None)
        if not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        if not lat:
            error = {"code": 1400, "description": "latitude: This field is required."}
        if not longi:
            error = {"code": 1400, "description": "longitude: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            location = None
            if stations:
                try:
                    if lat == "all" and longi == "all":
                        socials = StationPlaylistSocialCode.objects.filter(
                            station=stations[0], location__isnull=True
                        )
                        result["social"] = self.get_response(socials)
                    else:
                        locations = Locations.objects.filter(
                            location_lat=lat, location_long=longi
                        )
                        if locations:
                            location = locations[0]
                            socials = StationPlaylistSocialCode.objects.filter(
                                station=stations[0], location=location
                            )
                            result["social"] = self.get_response(socials)
                except:
                    pass

        response = GenericResponse(
            meta={"description": "Response for Social Codes JSON."},
            result=result,
            error=error,
        )
        return response

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all social codes for the
        station in given location.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        station_id = request.POST.get("station_id", None)
        lat = request.POST.get("latitude", None)
        longi = request.POST.get("longitude", None)
        if not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        if not lat:
            error = {"code": 1400, "description": "latitude: This field is required."}
        if not longi:
            error = {"code": 1400, "description": "longitude: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            location = None
            if stations:
                try:
                    if lat == "all" and longi == "all":
                        socials = StationPlaylistSocialCode.objects.filter(
                            station=stations[0], location__isnull=True
                        )
                        result["social"] = self.get_response(socials)
                    else:
                        locations = Locations.objects.filter(
                            location_lat=lat, location_long=longi
                        )
                        if locations:
                            location = locations[0]
                            socials = StationPlaylistSocialCode.objects.filter(
                                station=stations[0], location=location
                            )
                            result["social"] = self.get_response(socials)
                except:
                    pass

        response = GenericResponse(
            meta={"description": "Response for Social Codes JSON."},
            result=result,
            error=error,
        )
        return response

    def get_response(self, socials):
        data = []
        for social in socials:
            soc = {
                "artist": social.artist,
                "title": social.title,
                "type": social.type,
                "img_link": social.img_link if not social.img_link == None else "-",
                "post_link": (
                    social.post_link
                    if not social.post_link or not social.post_link == None
                    else "-"
                ),
                "post_text": (
                    social.post_text
                    if not social.post_link or not social.post_text == None
                    else "-"
                ),
                "user_img_link": (
                    social.user_image_link
                    if not social.user_image_link or not social.user_image_link == None
                    else "-"
                ),
            }
            # if social.type == 'instagram':
            #     soc.update({
            #         'code':social.instagram_code if social.instagram_code else '-',
            #         'related_link':social.related_link_instagram if social.related_link_instagram else '-',
            #     })
            # if social.type == 'twitter':
            #     soc.update({
            #         'code':social.twitter_code if social.twitter_code else '-',
            #         'related_link':social.related_link_twitter if social.related_link_twitter else '-',
            #     })
            data.append(soc)
        return data


class Music(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all Music Libraries for the
        station given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        station_id = request.POST.get("station_id", None)
        lat = request.POST.get("latitude", None)
        longi = request.POST.get("longitude", None)
        if not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        if not lat:
            error = {"code": 1400, "description": "latitude: This field is required."}
        if not longi:
            error = {"code": 1400, "description": "longitude: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            location = None
            exception = None
            if not lat == "all" and not longi == "all":
                try:
                    locations = Locations.objects.filter(
                        location_lat=lat, location_long=longi
                    )
                    location = locations[0] if locations else None
                except:
                    location = None
            if stations:
                try:
                    if lat == "all" and longi == "all":
                        socials = StationPlaylistSocialCode.objects.filter(
                            station=stations[0], location__isnull=True
                        )
                        result["social"] = self.get_response(socials)
                    else:
                        locations = Locations.objects.filter(
                            location_lat=lat, location_long=longi
                        )
                        if locations:
                            location = locations[0]
                            socials = StationPlaylistSocialCode.objects.filter(
                                station=stations[0], location=location
                            )
                            result["social"] = self.get_response(socials)
                except:
                    pass
                playlist = stations[0].station_playlist.all().filter(location=location)
                playlists = []
                i = 0
                for item in playlist:
                    try:
                        i = i + 1
                        content = item.content_type.model_class()
                        objects = content.objects.filter(id=item.object_id)
                        type = objects[0].__class__.__name__ if objects else None
                        data = {}
                        data["position"] = i

                        if type == "Library":
                            object = objects[0]
                            data.update(
                                {
                                    "title": object.title,
                                    "artist": object.artistname,
                                    "library_id": object.pk,
                                    "type": "MUSIC",
                                    "category": {
                                        "cat": object.get_rotation_category_display(),
                                        "skip_allowed": object.skip_allowed,
                                        "points": object.love_rating,
                                    },
                                    "cover": {
                                        "url": (
                                            object.cover_art.url
                                            if object.cover_art
                                            else ""
                                        )
                                    },
                                    "media": {"url": object.media},
                                    "artist_tour": {
                                        "twitter-url": object.twitter_name,
                                        "facebook-url": (
                                            object.facebook_name
                                            if object.facebook_name
                                            else ""
                                        ),
                                        "instagram-url": (
                                            object.instagram_name
                                            if object.instagram_name
                                            else ""
                                        ),
                                        "youtube-url": (
                                            object.youtube_name
                                            if object.youtube_name
                                            else ""
                                        ),
                                    },
                                    "duration": milliseconds_to_seconds(object.duration),
                                    "vox_point": milliseconds_to_seconds(object.vox_point),
                                    "in_point": milliseconds_to_seconds(object.in_point),
                                    "aux_point": milliseconds_to_seconds(
                                        object.aux_point
                                    ),
                                    "skipped": item.skipped,
                                }
                            )
                        if type == "BrandingTOH":
                            object = objects[0]
                            data.update(
                                {
                                    "branding_id": object.pk,
                                    "type": "BRANDING",
                                    "skip_allowed": object.skip_allowed,
                                    "title": object.title,
                                    "duration": milliseconds_to_seconds(object.duration),
                                    "in_point": milliseconds_to_seconds(object.in_point),
                                    "aux_point": milliseconds_to_seconds(
                                        object.aux_point
                                    ),
                                    "media": {"url": object.media},
                                }
                            )
                        if type == "Adverts":
                            object = objects[0]
                            data.update(
                                {
                                    "advert_id": object.pk,
                                    "type": "ADVERT",
                                    "advert-type": object.get_type_display(),
                                    "skip_allowed": object.skip_allowed,
                                    "title": object.title,
                                    "banner_text": object.banner_text,
                                    "radius": object.radius,
                                    "age_group": object.age_group,
                                    "micrositeURL": object.microsite,
                                    "duration": milliseconds_to_seconds(object.duration),
                                    "in_point": 0,
                                    "aux_point": milliseconds_to_seconds(
                                        object.aux_point
                                    ),
                                    "cover": {
                                        "url": (
                                            object.cover_art.url
                                            if object.cover_art
                                            else ""
                                        )
                                    },
                                    "media": {"url": object.media},
                                }
                            )

                        playlists.append(data)
                    except Exception as e:
                        logger.error(e)

                result["playlist"] = playlists
            else:
                error = {"code": 1400, "description": "Invalid station id."}
        response = GenericResponse(
            meta={"description": "Response for Music JSON."}, result=result, error=error
        )
        return response

    def get_response(self, socials):
        data = []
        for social in socials:
            soc = {
                "artist": social.artist,
                "title": social.title,
                "type": social.type,
            }
            if social.type == "instagram":
                soc.update(
                    {
                        "code": social.instagram_code if social.instagram_code else "-",
                        "related_link": (
                            social.related_link_instagram
                            if social.related_link_instagram
                            else "-"
                        ),
                    }
                )
            if social.type == "twitter":
                soc.update(
                    {
                        "code": social.twitter_code if social.twitter_code else "-",
                        "related_link": (
                            social.related_link_twitter
                            if social.related_link_twitter
                            else "-"
                        ),
                    }
                )
            data.append(soc)
        return data


class RetailMusic(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all Music Libraries for the
        retail station code given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        retail_code = request.POST.get("retail_code", None)
        if not retail_code:
            error = {"code": 1400, "description": "retail_code: This field is required."}
        else:
            stations = Stations.objects.filter(retailcode=retail_code)
            if stations:
                playlist = stations[0].station_playlist.all()
                playlists = []
                i = 0
                for item in playlist:
                    i = i + 1
                    content = item.content_type.model_class()
                    object = content.objects.get(id=item.object_id)
                    type = object.__class__.__name__
                    data = {}
                    data["position"] = str(i)

                    if type == "Library":
                        data["-type"] = ("MUSIC",)
                        data["category"] = {
                            "-cat": object.get_rotation_category_display(),
                            "-skip": "enabled" if object.skip_allowed else "disabled",
                            "-points": object.love_rating,
                        }
                        data["title"] = object.title
                        data["artist"] = object.artistname
                        data["library_id"] = object.pk
                        data["coverURL"] = {
                            "-url": object.cover_art.url if object.cover_art else ""
                        }
                        data["media"] = {"-url": object.media}
                        data["artist_tour"] = {
                            "twitter-url": object.twitter_name,
                            "facebook-url": (
                                object.facebook_name if object.facebook_name else ""
                            ),
                            "instagram-url": (
                                object.instagram_name if object.instagram_name else ""
                            ),
                            "youtube-url": (
                                object.youtube_name if object.youtube_name else ""
                            ),
                        }
                        data["duration"] = calculate_seconds(object.duration)
                        data["vox_point"] = calculate_seconds(object.vox_point)
                        data["in_point"] = calculate_seconds(object.in_point)
                        data["aux_point"] = calculate_seconds(object.aux_point)
                        data["skipped"] = "yes" if item.skipped else "no"
                    if type == "BrandingTOH":
                        data.update(
                            {
                                "-branding_id": object.pk,
                                "-type": "BRANDING",
                                "-skip": "enabled" if object.skip_allowed else "disabled",
                                "title": object.title,
                                "duration": calculate_seconds(object.duration),
                                "in_point": calculate_seconds(object.in_point),
                                "aux_point": calculate_seconds(object.aux_point),
                                "media": {"-url": object.media},
                            }
                        )
                    if type == "Adverts":
                        data.update(
                            {
                                "-advert_id": object.pk,
                                "-type": "ADVERT",
                                "advert-type": object.get_type_display(),
                                "-skip": "enabled" if object.skip_allowed else "disabled",
                                "title": object.title,
                                "banner_text": object.banner_text,
                                "radius": object.radius,
                                "age_group": object.age_group,
                                "duration": calculate_seconds(object.duration),
                                "micrositeURL": object.microsite,
                                "in_point": 0,
                                "aux_point": calculate_seconds(object.aux_point),
                                "coverURL": {
                                    "-url": (
                                        object.cover_art.url if object.cover_art else ""
                                    )
                                },
                                "media": {"-url": object.media},
                            }
                        )
                    playlists.append(data)

                result["playlist"] = playlists
            else:
                error = {"code": 1400, "description": "Invalid retail code."}
        response = GenericResponse(
            meta={"description": "Response for Retail Music JSON."},
            result=result,
            error=error,
        )
        return response


class Branding(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all Branding Libraries for the
        station and location given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        station_id = request.POST.get("station_id", None)
        location = request.POST.get("location", None)
        if not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        elif not location:
            error = {"code": 1400, "description": "location: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            brandings = []
            if not location == "All" and stations:
                locations = Locations.objects.filter(location_city=location)
                brandings = (
                    BrandingTOH.objects.filter(station=stations[0], location=locations[0])
                    if locations
                    else []
                )
            else:
                brandings = (
                    BrandingTOH.objects.filter(station=stations[0], location__isnull=True)
                    if stations
                    else []
                )
            results = []
            for branding in brandings:
                results.append(
                    {
                        "-branding_id": branding.pk,
                        "-type": "BRANDING",
                        "-skip": "enabled" if branding.skip_allowed else "disabled",
                        "title": branding.title,
                        "duration": calculate_seconds(branding.duration),
                        "in_point": calculate_seconds(branding.in_point),
                        "aux_point": calculate_seconds(branding.aux_point),
                        "media": {"-url": branding.media},
                    }
                )
            if stations:
                result["brandings"] = {
                    "playlist": "Content",
                    "location": {"-location": location},
                    "items": results,
                }
            else:
                error = {"code": 1400, "description": "Invalid station id."}

        response = GenericResponse(
            meta={"description": "Response for Brandings JSON."},
            result=result,
            error=error,
        )
        return response


class Advert(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all Adverts Libraries for the
        station and location given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        location = request.POST.get("location", None)
        if not location:
            error = {"code": 1400, "description": "location: This field is required."}
        else:
            adverts = []
            if not location == "All":
                locations = Locations.objects.filter(location_city=location)
                adverts = (
                    Adverts.objects.filter(location=locations[0]) if locations else []
                )
            else:
                adverts = Adverts.objects.filter(location__isnull=True)
            results = []
            for advert in adverts:
                results.append(
                    {
                        "-advert_id": advert.pk,
                        "-type": advert.get_type_display(),
                        "-skip": "enabled" if advert.skip_allowed else "disabled",
                        "title": advert.title,
                        "banner_text": advert.banner_text,
                        "radius": advert.radius,
                        "age_group": advert.age_group,
                        "duration": calculate_seconds(advert.duration),
                        "micrositeURL": advert.microsite,
                        "in_point": 0,
                        "aux_point": calculate_seconds(advert.aux_point),
                        "coverURL": {
                            "-url": advert.cover_art.url if advert.cover_art else ""
                        },
                        "media": {"-url": advert.media},
                    }
                )
            result = {
                "playlist": "Adverts",
                "location": {"-location": location},
                "items": results,
            }
        response = GenericResponse(
            meta={"description": "Response for Adverts JSON."}, result=result, error=error
        )
        return response


class MusicSearch(APIBaseView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        """
        Simple GET request. Returns a JSON response for all Music Libraries for the
        search query  given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        q = request.GET.get("q", None)

        songs = []
        if q:
            results = Library.objects.filter(
                Q(artistname__icontains=q) | Q(title__icontains=q)
            )
            i = 0
            for object in results:
                i = i + 1
                data = {}
                data["position"] = str(i)
                data["category"] = {
                    "-cat": object.get_rotation_category_display(),
                    "-skip": "enabled" if object.skip_allowed else "disabled",
                    "-points": object.love_rating,
                }
                data["title"] = object.title
                data["artist"] = object.artistname
                data["coverURL"] = {
                    "-url": object.cover_art.url if object.cover_art else ""
                }
                data["media"] = {"-url": object.media}
                data["artist_tour"] = {
                    "twitter-url": object.twitter_name,
                    "facebook-url": object.facebook_name if object.facebook_name else "",
                    "instagram-url": (
                        object.instagram_name if object.instagram_name else ""
                    ),
                    "youtube-url": object.youtube_name if object.youtube_name else "",
                }
                data["duration"] = calculate_seconds(object.duration)
                data["vox_point"] = (
                    calculate_seconds(object.vox_point) if object.vox_point else "",
                )
                data["in_point"] = calculate_seconds(object.in_point)
                data["aux_point"] = calculate_seconds(object.aux_point)
                songs.append(data)
        result["search-results"] = songs
        response = GenericResponse(
            meta={"description": "Response for Music Search JSON."},
            result=result,
            error=error,
        )
        return response


class SoundWall(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all SoundWall for the
        channelID given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        channel_id = request.POST.get("channel_id", None)
        if not channel_id:
            error = {"code": 1400, "description": "channel_id: This field is required."}
        else:
            stations = Stations.objects.filter(id=channel_id)
            items = []
            i = 0
            if stations:
                walls = stations[0].station_wall_contents.all().order_by("id")
                for wall in walls:
                    i += 1
                    items.append(
                        {
                            "channelID": channel_id,
                            "position": i,
                            "media_type": (
                                wall.get_media_type_display() if wall.media_type else ""
                            ),
                            "title": wall.title,
                            "artist": wall.artist,
                            "IN": wall.in_point,
                            "AUX": wall.aux_point,
                            "relativeLink": wall.relative_link,
                            "contentType": "Studio" if wall.studio_only else "Radio",
                            "foregroundColor": wall.ui_color_foreground,
                            "backgroundColor": wall.ui_color_background,
                            "shareURL": wall.social_media_handle,
                            "mediaURL": wall.media,
                            "coverimgURL": wall.cover_art.url if wall.cover_art else "",
                            "youtubeURL": wall.youtube,
                            "allowSkip": "YES" if wall.skip_allowed else "NO",
                            "scheduled": "YES" if wall.schedule_item else "NO",
                        }
                    )
            result["soundwall"] = items
        response = GenericResponse(
            meta={"description": "Response for SoundWall JSON."},
            result=result,
            error=error,
        )
        return response


class DJUserSignup(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        User can signup as DJ user and post contents after login.
        """
        result = {}
        error = {}
        form = DJUserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user=request.user)
            result = {"status": "DJ User Added."}
            site = Site.objects.get(pk=1)
            login_url = "http://" + site.domain + reverse("api_dj_login")
            username = request.POST.get("username")
            password = request.POST.get("password")
            resp = requests.post(
                login_url, data={"username": username, "password": password}
            )
            data = resp.json()
            result["token"] = data["result"].get("token", None)
        else:
            error = strip_tags(form.errors)
            error = (
                error.replace("This field", "")
                .replace("A", ": A")
                .replace("emailEnter", "Enter")
            )
            error = {"code": 1400, "description": error}
        response = GenericResponse(
            meta={"description": "Response for DJ User signup JSON."},
            result=result,
            error=error,
        )
        return response


class DJUserLogin(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        User can login from mobile directly. The request will contain user name,
        password. If succesful a token will be created. The token will be valid
        for one day. After that it will be expired.
        """
        result = {}
        error = {}
        login_success = False

        if not self.login_error:
            authentication_form = AuthenticationForm
            form = authentication_form(data=request.POST)
            if form.is_valid():
                profiles = DJUser.objects.filter(user=form.get_user())
                if profiles:
                    login(request, form.get_user())
                    username = form.get_user()
                    token = profiles[0].create_token(username)
                    login_success = True
                    result = {"token": base64.encodestring(token)}
                    error = {"code": 200, "description": "Successful"}

                else:
                    error = {"code": 1401, "description": "Unauthorized"}
            else:
                error = strip_tags(form.errors)
                error = error.replace("This field", "")
                error = {"code": 1400, "description": error}
        else:
            error = self.login_error
        result["login_success"] = login_success
        response = GenericResponse(
            meta={"description": "Response for login"}, result=result, error=error
        )
        return response


class DJPasswordReset(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Password reset process step-1. Mail a key for valid emails, to be used
        in step-2.
        """
        result = {}
        error = {}
        result["status"] = "failed"
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            opts = {
                "use_https": request.is_secure(),
                "token_generator": default_token_generator,
                "from_email": settings.ADMIN_EMAIL,
                #                'email_template_name': email_template_name,
                #                'subject_template_name': subject_template_name,
                "request": request,
            }
            key = form.save(**opts)
            #            send_all()
            result["status"] = "success"
            result["key"] = key
        else:
            error = strip_tags(form.errors)
            error = (
                error.replace("This field", "")
                .replace("Enter", ": Enter")
                .replace("That", ": That")
            )
            error = {"code": 1400, "description": error}
        response = GenericResponse(
            meta={"description": "Response for password reset."},
            result=result,
            error=error,
        )
        return response


class DJPasswordResetConfirm(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Password reset process step-2. Final step in password reset process.
        """
        result = {}
        error = {}
        uidb36 = kwargs["uidb36"]
        token = kwargs["token"]
        result["status"] = "failed"
        UserModel = get_user_model()
        email = request.POST.get("email")
        assert uidb36 is not None and token is not None  # checked by URLconf
        try:
            uid_int = base36_to_int(uidb36)
            user = UserModel._default_manager.get(pk=uid_int)
        except (ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(
            user, base64.b64decode(token)
        ):
            validlink = True
            if request.method == "POST":
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    result["status"] = "success"
                else:
                    error = strip_tags(form.errors)
                    error = (
                        error.replace("This field", "")
                        .replace("Enter", ": Enter")
                        .replace("T", ": T")
                    )
                    error = {"code": 1400, "description": error}
        else:
            error = {"code": 1400, "description": "Invalid Key"}
        response = GenericResponse(
            meta={"description": "Response for password reset."},
            result=result,
            error=error,
        )
        return response


class DJAddContent(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(DJAddContent, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Loggedin DJ Users can post sound records to MMI Studio.
        """
        self.start_time = time.time()
        result = {}
        error = {}
        form = DJTracksForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user=request.user)
            result = {"status": "DJ Track Added."}
        else:
            error = strip_tags(form.errors)
            error = error.replace("This field", "")
            error = {"code": 1400, "description": error}
        self.elapsed_time = time.time() - self.start_time
        response = GenericResponse(
            meta={
                "description": "Response for adding content to DJ media account.",
                "runtime": self.elapsed_time,
            },
            result=result,
            error=error,
        )
        return self.render_to_json_response(response, **kwargs)


class FollowUnfollowUser(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(FollowUnfollowUser, self).dispatch(*args, **kwargs)

    def post(self, request, type, *args, **kwargs):
        self.start_time = time.time()
        result = {}
        error = {}
        dj = request.POST.get("djid")
        splitted = dj.split("MU")
        if splitted:
            dj_id = splitted[0]
            try:
                djuser = DJUser.objects.get(id=dj_id)
                if type == "follow":
                    activity, created = UserActivity.objects.get_or_create(
                        to_user=djuser.user, from_user=request.user
                    )
                    result = {"status": "Followed successfully."}
                if type == "unfollow":
                    UserActivity.objects.filter(
                        to_user=djuser.user, from_user=request.user
                    ).delete()
                    result = {"status": "Unfollowed successfully."}
                if type == "check-follow":
                    activity = UserActivity.objects.filter(
                        to_user=djuser.user, from_user=request.user
                    )
                    result = (
                        {"is_following": True}
                        if activity.count() > 0
                        else {"is_following": False}
                    )
            except DJUser.DoesNotExist:
                error = {"code": 1400, "description": "DJ user doesn't exist."}

        self.elapsed_time = time.time() - self.start_time
        response = GenericResponse(
            meta={
                "description": "Response for user activity.",
                "runtime": self.elapsed_time,
            },
            result=result,
            error=error,
        )
        return self.render_to_json_response(response, **kwargs)


class AddMediaWall(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddMediaWall, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Loggedin admin user can add media wall contents.
        """
        self.start_time = time.time()
        result = {}
        error = {}
        form = DashboardWallForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            result = {"status": "Media Wall Added."}
        else:
            error = strip_tags(form.errors)
            error = error.replace("This field", "")
            error = {"code": 1400, "description": error}
        self.elapsed_time = time.time() - self.start_time
        response = GenericResponse(
            meta={
                "description": "Response for adding media wall content.",
                "runtime": self.elapsed_time,
            },
            result=result,
            error=error,
        )
        return self.render_to_json_response(response, **kwargs)


class StationDJContent(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all published DJ tracks for the
        DJ-id given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        djids = request.POST.get("djids", None)
        stationID = request.POST.get("stationID", None)
        tags = request.POST.get("tags", None)
        djids = djids.split(",") if djids else []
        if not djids:
            error = {"code": 1400, "description": "djids: This field is required."}
        elif not stationID:
            error = {"code": 1400, "description": "stationID: This field is required."}
        # elif not tags:
        #     error = {"code": 1400, "description": "tags: This field is required."}
        else:
            data = []
            # datatags = tags.split(',')
            datatags = tags
            hr_24_before = timezone.now() - timedelta(days=1)
            print(timezone.now())
            append_value = True
            print(djids, "all")
            for djid in djids:
                print(djid, "iter")
                values = djid.split("MU")
                try:
                    djs = DJUser.objects.filter(id=values[0])
                    if djs:
                        dj = djs[0]
                        # tracks = (
                        #     DJTracks.objects.filter(dj__station__id=stations[0].pk)
                        #     .filter(published=True)
                        #     .filter(created__gte=hr_24_before)
                        #     .order_by("-id")
                        #     if stations
                        #     else []
                        # )
                        tracks = (
                            dj.dj_user_tracks.filter(dj__station__id=stationID)
                            .filter(published=True)
                            .order_by("-id")
                        )
                        for track in tracks:
                            trackTags = track.get_tags()
                            if tags:
                                tagfound = [tag for tag in datatags if tag in trackTags]
                                append_value = True if tagfound else False
                            if append_value:
                                data.append(
                                    {
                                        "DJName": track.dj.user.username,
                                        "DJID": str(track.dj.pk)
                                        + "MU"
                                        + str(track.dj.user.pk),
                                        "stationID": (
                                            track.dj.station.pk
                                            if track.dj.station
                                            else ""
                                        ),
                                        "ProfileImage": (
                                            track.dj.photo.url if track.dj.photo else ""
                                        ),
                                        "Title": track.title,
                                        "Link": track.media.url if track.media else "",
                                        "CoverArt": (
                                            track.cover_art.url if track.cover_art else ""
                                        ),
                                        "recorded": track.recorded,
                                        "tags": track.tags,
                                        "in": track.in_point,
                                        "aux": track.aux_point,
                                        "created": str(track.created),
                                    }
                                )
                except:
                    pass
            result["tracks"] = data
        response = GenericResponse(
            meta={"description": "Response for published DJ tracks."},
            result=result,
            error=error,
        )
        return response


class DJSetReputation(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Set reputation for the DJ-id given.
        """
        result = {}
        result["status"] = False
        error = {"code": 200, "description": "Successful"}
        djid = request.POST.get("djid", None)
        type = request.POST.get("type", None)
        if not djid:
            error = {"code": 1400, "description": "djid: This field is required."}
        elif not type:
            error = {"code": 1400, "description": "type: This field is required."}
        else:
            try:
                values = djid.split("MU")
                djs = DJUser.objects.filter(id=values[0])
                if djs:
                    dj = djs[0]
                    rptn, created = DJReputation.objects.get_or_create(dj=dj)
                    if type == "follow":
                        current = rptn.num_followers
                        rptn.num_followers = current + 1
                        rptn.save()
                        result["status"] = True
                    if type == "unfollow":
                        current = rptn.num_followers
                        rptn.num_followers = current - 1 if current > 0 else 0
                        rptn.save()
                        result["status"] = True
            except:
                pass
        response = GenericResponse(
            meta={"description": "Response for set reputation."},
            result=result,
            error=error,
        )
        return response


class DJSetSubscription(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Set subscription for given station.
        """
        result = {}
        result["status"] = False
        error = {"code": 200, "description": "Successful"}
        djid = request.POST.get("djid", None)
        station_id = request.POST.get("station_id", None)
        if not djid:
            error = {"code": 1400, "description": "djid: This field is required."}
        elif not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            values = djid.split("MU")
            djs = DJUser.objects.filter(id=values[0])
            if stations and djs:
                station = stations[0]
                dj = djs[0]
                date = timezone.now().date()
                if request.user == dj.user:
                    subsc, created = DJStationStatus.objects.get_or_create(
                        dj=dj, station=station
                    )
                    result["status"] = True
                else:
                    error = {"code": 1400, "description": "Token and djid mismatch."}
            else:
                if not stations:
                    error = {"code": 1400, "description": "Station not found."}
                if not djs:
                    error = {"code": 1400, "description": "DJ not found."}

        response = GenericResponse(
            meta={"description": "Response for set subscription."},
            result=result,
            error=error,
        )
        return response


class DJGetSubscription(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Get subscription for given station.
        """
        print(request.POST, "POSTTTTTTTT")
        result = {}
        result["status"] = False
        error = {"code": 200, "description": "Successful"}
        djid = request.POST.get("djid", None)
        station_id = request.POST.get("station_id", None)
        if not djid:
            error = {"code": 1400, "description": "djid: This field is required."}
        elif not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            values = djid.split("MU")
            djs = DJUser.objects.filter(id=values[0])
            if stations and djs:
                dj = djs[0]
                subsc = dj.dj_station_status.all().filter(station__id=station_id)
                result["status"] = "Expired"
                if subsc:
                    result["status"] = subsc[0].check_expiry()
            else:
                if not stations:
                    error = {"code": 1400, "description": "Station not found."}
                if not djs:
                    error = {"code": 1400, "description": "DJ not found."}

        response = GenericResponse(
            meta={"description": "Response for get subscription."},
            result=result,
            error=error,
        )
        return response


class GetDJTags(APIBaseView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        """
        Simple GET request. Returns a JSON response of all tags.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        tags = DJTag.objects.all()
        data = []
        for tag in tags:
            data.append(tag.name)
        result["tags"] = data
        response = GenericResponse(
            meta={"description": "Response for tags JSON."}, result=result, error=error
        )
        return response


class GetDJMusicbeds(APIBaseView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        """
        Simple GET request. Returns a JSON response of all station music beds.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        station_id = request.GET.get("station_id", None)
        if not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        else:
            data = []
            stations = Stations.objects.filter(id=station_id)
            if stations:
                station = stations[0]
                for musicbed in station.station_dj_musicbeds.all():
                    data.append({"audioURL": musicbed.url})
            result["musicbeds"] = data

        response = GenericResponse(
            meta={"description": "Response for Musicbeds JSON."},
            result=result,
            error=error,
        )
        return response


class UserInfo(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple GET request. Returns a JSON response of all DJ users info.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        username = request.POST.get("username")

        users = DJUser.objects.filter(user__username__icontains=username)
        data = []
        if username:
            for dj in users:
                followers = dj.user.user_activity_to_user.all()
                data.append(
                    {
                        "id": str(dj.pk) + "MU" + str(dj.user.pk),
                        "username": dj.user.username,
                        "name": {
                            "first_name": dj.user.first_name,
                            "last_name": dj.user.last_name,
                        },
                        "email": dj.user.email,
                        "avatar": dj.photo.url,
                        "relatedStation": {
                            "station_id": dj.station.pk,
                            "name": dj.station.station_name,
                            "logo": (
                                dj.station.station_logo.url
                                if dj.station.station_logo
                                else ""
                            ),
                        },
                        "active": dj.user.is_active,
                        "reputaion": {"followers": dj.get_follower_count},
                    }
                )
        else:
            error = {"code": 1400, "description": "username required."}
        result["user-data"] = data
        response = GenericResponse(
            meta={"description": "Response for users info."}, result=result, error=error
        )
        return response


class StationDJUsers(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all DJ users tracks for the
        station given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        station_id = request.POST.get("station_id", None)
        if not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            if stations:
                station = stations[0]
                users = station.station_dj_user.all()
                data = []
                for dj in users:
                    data.append(
                        {
                            "id": str(dj.pk) + "MU" + str(dj.user.pk),
                            "username": dj.user.username,
                            "name": {
                                "first_name": dj.user.first_name,
                                "last_name": dj.user.last_name,
                            },
                            "email": dj.user.email,
                            "avatar": dj.photo.url,
                            "relatedStation": {
                                "station_id": dj.station.pk,
                                "name": dj.station.station_name,
                                "logo": (
                                    dj.station.station_logo.url
                                    if dj.station.station_logo
                                    else ""
                                ),
                            },
                            "active": dj.user.is_active,
                        }
                    )
                result["users-data"] = data
            else:
                error = {"code": 1400, "description": "Station doesnot exists."}

        response = GenericResponse(
            meta={"description": "Response for dj station users info."},
            result=result,
            error=error,
        )
        return response


class UpdateAnalytics(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Saves the current analytics data from iOS/Android.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        NOW = timezone.now().date()
        try:
            analytics = Analytics.objects.get(date=NOW)
        except ObjectDoesNotExist:
            analytics = Analytics.objects.create(
                date=NOW, unique_users=0, current_users=0
            )

        posts = request.POST.copy()
        posts["s3_data_usage"] = posts.pop("cloud_files")
        datas = dict((k, v) for k, v in posts.iteritems() if v)
        Analytics.objects.filter(id=analytics.pk).update(**datas)
        result = {"status": "Analytics updated successfully."}
        response = GenericResponse(
            meta={"description": "Response for update analytics."},
            result=result,
            error=error,
        )
        return response


class UpdateTSUPerStation(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Saves the current TSU data from iOS/Android.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        NOW = timezone.now().date()
        station_id = request.POST.get("station_id")
        posts = {
            "total_users": request.POST.get("total_users", None),
            "avg_per_head": request.POST.get("avg_per_head", None),
            "avg_hour_per_user": request.POST.get("avg_hour_per_user", None),
            "total_hours": request.POST.get("total_hours", None),
        }
        if not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            if stations:
                station = stations[0]
                try:
                    analytics = Analytics.objects.get(date=NOW)
                except ObjectDoesNotExist:
                    analytics = Analytics.objects.create(
                        date=NOW, unique_users=0, current_users=0
                    )
                try:
                    tsu = TSUPerStation.objects.get(analytics=analytics, station=station)
                except ObjectDoesNotExist:
                    tsu = TSUPerStation.objects.create(
                        analytics=analytics, station=station
                    )

                datas = dict((k, v) for k, v in posts.iteritems() if v)
                TSUPerStation.objects.filter(id=tsu.pk).update(**datas)
                result = {"status": "TSU per station updated successfully."}
            else:
                error = {"code": 1400, "description": "Station doesnot exists."}

        response = GenericResponse(
            meta={"description": "Response for update tsu per station."},
            result=result,
            error=error,
        )
        return response


class UpdateMusicResearch(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Saves the current Music Research Plots.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        NOW = timezone.now().date()
        library_id = request.POST.get("library_id")
        value = request.POST.get("value")

        if not library_id:
            error = {"code": 1400, "description": "library_id: This field is required."}
        elif not value:
            error = {"code": 1400, "description": "value: This field is required."}
        else:
            try:
                dashboard = Dashboard.objects.get(date=NOW)
            except ObjectDoesNotExist:
                dashboard = Dashboard.objects.create(date=NOW)
            libraries = Library.objects.filter(id=library_id)
            if libraries:
                library = libraries[0]
                try:
                    research = MusicResearchLibrary.objects.get(
                        dashboard=dashboard, library=library
                    )
                except ObjectDoesNotExist:
                    research = MusicResearchLibrary.objects.create(
                        dashboard=dashboard, library=library
                    )
                data = MusicResearchData.objects.create(research=research)
                data.value = value
                data.save()
                result = {"status": "Music research updated successfully."}
            else:
                error = {"code": 1400, "description": "Library doesnot exists."}

        response = GenericResponse(
            meta={"description": "Response for update Music Research Plots."},
            result=result,
            error=error,
        )
        return response


class UpdateRealTimeSkip(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Saves the current Real Time Skip.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        NOW = timezone.now().date()
        library_id = request.POST.get("library_id")
        value = request.POST.get("value")

        if not library_id:
            error = {"code": 1400, "description": "library_id: This field is required."}
        elif not value:
            error = {"code": 1400, "description": "value: This field is required."}
        else:
            try:
                dashboard = Dashboard.objects.get(date=NOW)
            except ObjectDoesNotExist:
                dashboard = Dashboard.objects.create(date=NOW)
            libraries = Library.objects.filter(id=library_id)
            if libraries:
                library = libraries[0]
                try:
                    realtime = RealTimeSkipLibrary.objects.get(
                        dashboard=dashboard, library=library
                    )
                except ObjectDoesNotExist:
                    realtime = RealTimeSkipLibrary.objects.create(
                        dashboard=dashboard, library=library
                    )
                data = RealTimeSkipData.objects.create(realtime=realtime)
                data.value = value
                data.save()
                result = {"status": "RealTime Skip Data updated successfully."}
            else:
                error = {"code": 1400, "description": "Library doesnot exists."}

        response = GenericResponse(
            meta={"description": "Response for update RealTime Skip Data."},
            result=result,
            error=error,
        )
        return response


class UpdateDashboardTopSongs(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Saves the current top song data for dashboard.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        NOW = timezone.now().date()
        library_id = request.POST.get("library_id")
        instagram = request.POST.get("instagram")
        rating = request.POST.get("rating")
        if not library_id:
            error = {"code": 1400, "description": "library_id: This field is required."}
        elif not instagram:
            error = {"code": 1400, "description": "instagram: This field is required."}
        else:
            libraries = Library.objects.filter(id=library_id)
            if libraries:
                library = libraries[0]
                try:
                    dashboard = Dashboard.objects.get(date=NOW)
                except ObjectDoesNotExist:
                    dashboard = Dashboard.objects.create(date=NOW)

                try:
                    top = DashboardTopSongs.objects.get(
                        dashboard=dashboard, library=library
                    )
                except ObjectDoesNotExist:
                    top = DashboardTopSongs.objects.create(
                        dashboard=dashboard, library=library, instagram="@"
                    )
                if instagram:
                    top.instagram = instagram
                    top.save()
                if rating:
                    top.rating = rating
                    top.save()
                result = {"status": "Dashboard Top Songs updated successfully."}
            else:
                error = {"code": 1400, "description": "Library does not exist."}
        response = GenericResponse(
            meta={"description": "Response for update RealTime Skip Data."},
            result=result,
            error=error,
        )
        return response


class StationBanners(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Returns a JSON response for all banners for the
        station and type given.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        station_id = request.POST.get("station_id", None)
        type = request.POST.get("bannerType", None)
        if not station_id:
            error = {"code": 1400, "description": "station_id: This field is required."}
        elif not type:
            error = {"code": 1400, "description": "bannerType: This field is required."}
        else:
            stations = Stations.objects.filter(id=station_id)
            if stations:
                station = stations[0]
                banners = station.station_banners.all().filter(type=type)
                data = []
                for banner in banners:
                    data.append(
                        {
                            "bannerUrl": banner.banner.url if banner.banner else "",
                            "bannerType": banner.type,
                        }
                    )
                result[station.station_name] = data
        response = GenericResponse(
            meta={"description": "Response for station banners."},
            result=result,
            error=error,
        )
        return response


class AddLibrary(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Adds a track to library.
        """
        result = {}
        error = {"code": 200, "description": "Successful"}
        form = DashboardLibraryForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not username:
            error = {"code": 1400, "description": "username: This field is required."}
        elif not password:
            error = {"code": 1400, "description": "password: This field is required."}
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active and user.is_superuser:
                    if form.is_valid():
                        form.save()
                        result["status"] = True
                    else:
                        error = {
                            "code": 1400,
                            "description": form.errors.as_text()
                            .replace("*", "")
                            .replace("\n", ":"),
                        }
                else:
                    error = {"code": 1400, "description": "Invalid User"}
            else:
                error = {"code": 1400, "description": "Invalid User"}

        response = GenericResponse(
            meta={"description": "Response for add library."}, result=result, error=error
        )
        return response


class AddInstallation(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Adds a device token to backend.
        """
        token = request.POST.get("device_token")
        result = {}
        error = {"code": 200, "description": "Successful"}
        if token:
            ins, created = Installation.objects.get_or_create(device_token=token)
        else:
            error = {"code": 1400, "description": "Invalid device token"}
        response = GenericResponse(
            meta={"description": "Response for add device token."},
            result=result,
            error=error,
        )
        return response


class CheckUserEmailVerified(APIBaseView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """
        Simple POST request. Check if requested user has verified his/her email.
        """

        self.start_time = time.time()
        result = {}
        error = {}
        user = request.user
        result = {"email_verified": user.dj_user.email_verified}
        self.elapsed_time = time.time() - self.start_time
        response = GenericResponse(
            meta={
                "description": "Response for checking if user has a verified email.",
                "runtime": self.elapsed_time,
            },
            result=result,
            error=error,
        )
        return response
