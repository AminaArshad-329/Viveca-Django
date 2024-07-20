import json
import urllib
from django.http import HttpResponse
from django.views.generic.base import View
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib.sites.models import Site
from airadio.models import Stations, Library
from airadio.views.api import calculate_seconds
from airadio.models import WidgetUserStatistics

# SITE_URL = 'http://162.209.102.208:8888'


class GetWidgetPlayList(object):
    def __init__(self, station):
        self.station = station

    def get_playlist(self):
        SITE = Site.objects.get(pk=1)
        SITE_URL = "http://" + SITE.domain

        playlist = self.station.station_playlist.all()
        playlists = []

        for item in playlist:
            content = item.content_type.model_class()
            object = content.objects.get(id=item.object_id)
            data = {}
            data["title"] = object.title
            data["artist"] = object.artistname
            data["media"] = SITE_URL + reverse(
                "widget_content_data", kwargs={"slug": "audio_" + str(object.id)}
            )
            data["cover"] = (
                SITE_URL
                + reverse("widget_content_data", kwargs={"slug": "img_" + str(object.id)})
                if object.cover_art
                else ""
            )
            data["aux"] = int(calculate_seconds(object.aux_point)) / 1000
            playlists.append(data)
        return playlists


class WidgetStationList(View):
    def get(self, request, *args, **kwargs):
        callback = request.GET.get("callback", "jsonpCallback")

        #        stations = Stations.get_stations_with_playlist().order_by('id')
        stations = Stations.objects.filter(retail=True).order_by("id")
        results = {}

        #        results['stations'] = list(stations.values_list('station_name',flat=True))
        # results['stationCodes'] = [{'code': station.retailcode, 'name': station.station_name, 'ref':station.id} for station in stations]
        results["albumImages"] = [
            station.station_logo.url if station.station_logo else ""
            for station in stations
        ]
        results["playlist"] = []
        #        if stations:
        #            playlists = GetWidgetPlayList(stations[0]).get_playlist()
        # results['playlist'] = playlists
        return HttpResponse(
            callback + "(" + json.dumps(results) + ");", content_type="application/json"
        )


class WidgetStationPlaylist(View):
    def get(self, request, *args, **kwargs):
        id = request.GET.get("ref")
        code = request.GET.get("code")
        callback = request.GET.get("callback", "jsonpCallbackPlaylist")
        results = {}
        results["status"] = False
        if id:
            stations = Stations.objects.filter(id=id)
        elif code:
            stations = Stations.objects.filter(retailcode=code)
        else:
            stations = []
        if stations:
            playlists = GetWidgetPlayList(stations[0]).get_playlist()
            if playlists and stations[0].published == True:
                stats, created = WidgetUserStatistics.objects.get_or_create(
                    station=stations[0]
                )
                stats.user_count = stats.user_count + 1
                stats.save()
                results["station"] = stations[0].station_name
                results["status"] = True
                results["playlist"] = playlists
        return HttpResponse(
            callback + "(" + json.dumps(results) + ");", content_type="application/json"
        )


class WidgetContentData(View):
    def get(self, request, *args, **kwargs):
        splitted = kwargs["slug"].split("_")
        error = self.get_error_response("401")
        if len(splitted) == 2:
            type = splitted[0]
            if type == "img":
                try:
                    library = Library.objects.get(id=splitted[1])
                except ObjectDoesNotExist:
                    response = self.get_error_response("403")
                else:
                    url = library.cover_art.url
                    response = self.get_response(url, type)

            if type == "audio":
                try:
                    library = Library.objects.get(id=splitted[1])
                except ObjectDoesNotExist:
                    response = self.get_error_response("403")
                else:
                    url = library.media
                    response = self.get_response(url, type)
        else:
            response = error

        return response

    def get_response(self, url, type):
        try:
            ext = url.split(".")[-1]
            response = HttpResponse(content=urllib.urlopen(url).read())
            response["Content-Type"] = "text/plain"
            response["Content-Disposition"] = "attachment; filename=%s.%s" % (type, ext)
        except:
            response = self.get_error_response("403")
        return response

    def get_error_response(self, code):
        return HttpResponse(
            json.dumps(
                {
                    "401": {
                        "code": "401",
                        "error": "You are not authorised to view this content.",
                    },
                    "403": {
                        "code": "403",
                        "error": "Unable to locate or the file may moved to another location.",
                    },
                }[code]
            ),
            content_type="application/json",
        )
