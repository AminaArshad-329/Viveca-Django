import json
import os
import random
import string
import subprocess
import tempfile
import urllib
import requests
import logging
import uuid
import boto3

from datetime import timedelta
from io import BytesIO
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.core.files import File
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, Sum, Case, When
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, CreateView
from django.views.generic.base import View
from utils.helpers import create_storage_filename
from utils.views import JSONResponseMixin, clone_station

import twitter
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from urllib.parse import urlencode

from airadio.forms import (
    DashboardLibraryForm,
    DashboardSequenceForm,
    DashboardWallForm,
    DashboardSchedulingForm,
    DashboardStationLocationForm,
    DashboardBrandingTOHForm,
    DashboardAdvertForm,
    DashboardUserForm,
    DashboardUserEditForm,
    DashboardLocationForm,
    DashboardGenresForm,
    DashboardStationPlaylistSocialCode,
    DashboardDJMusicBedForm,
    NewsGenerateForm,
    SettingStationForm,
)
from airadio.models import (
    Analytics,
    Library,
    RealTimeSkipLibrary,
    Stations,
    Locations,
    PositionPrompts,
    TopicPrompts,
    MediaUpload,
    StationLibrary,
    GlobalPlaylist,
    Wall,
    BrandingTOH,
    Scheduling,
    Adverts,
    DJTracks,
    StationPlaylist,
    ExportPlaylist,
    Sequence,
    Genres,
    StationPlaylistSocialCode,
    DJMusicBed,
)
from airadio.playlist import Playlist
from airadio.tasks import get_image_file_url, export_palylist
from airadio.templatetags.radio_tags import TIME_CHART
from airadio.views.generate_news_scripts import (
    get_news_script,
    generate_bulletin,
    generate_voicetrack_from_prompts,
)
from airadio.views.helpers import speak_elevenlabs

logger = logging.getLogger(__name__)


def is_ajax(request):
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


def get_days_before(days):
    return timezone.now() - timedelta(days=days)


def get_page_paginator(results, items_per_page=5, page_number=1):
    paginator = Paginator(results, items_per_page)

    try:
        results = paginator.page(page_number)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.object_list.none()

    return results


def get_dashboard_stats(queryset=None, start=None, end=None):
    if not queryset:
        queryset = Analytics.objects.filter(date__gte=start, date__lte=end)
    result = {}
    result["unique_users"] = (
        queryset.aggregate(Sum("unique_users"))["unique_users__sum"] if queryset else 0
    )
    result["current_users"] = (
        queryset.aggregate(Sum("current_users"))["current_users__sum"] if queryset else 0
    )
    result["s3_data_usage"] = (
        queryset.aggregate(Sum("s3_data_usage"))["s3_data_usage__sum"] / queryset.count()
        if queryset
        else 0
    )
    result["db_load"] = (
        queryset.aggregate(Sum("db_load"))["db_load__sum"] / queryset.count()
        if queryset
        else 0
    )
    return result


def delete_linode_object(media_url):
    try:
        file_name = media_url.split("/" + settings.AWS_STORAGE_BUCKET_NAME + "/")[-1]

        linode_obj_config = {
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "endpoint_url": settings.AWS_S3_ENDPOINT_URL,
        }
        client = boto3.client("s3", **linode_obj_config)
        client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name)
    except Exception as e:
        logger.error("Error deleting object from linode:", e)


class PlaylistExportJson(View):
    def get(self, request, *args, **kwargs):
        station = self.request.GET.get("station")
        location = self.request.GET.get("location")
        type = self.request.GET.get("type")
        context = {}
        datas = []
        if location == "all":
            datas = ExportPlaylist.objects.filter(
                station__id=station, location__isnull=True
            )
        else:
            datas = ExportPlaylist.objects.filter(
                station__id=station, location__id=location
            )
        if type == "json":
            results = []
            for data in datas:
                results.append(
                    {TIME_CHART[data.hour]: [item.item for item in data.exports.all()]}
                )
                context["results"] = results
        return HttpResponse(json.dumps(context), content_type="application/json")


class LoginView(View):
    template_name = "viveca_dashboard/login.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context["form"] = AuthenticationForm()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = AuthenticationForm(data=request.POST)
        next = request.POST.get("next")
        if form.is_valid():
            user = form.get_user()
            if user.is_active and user.is_superuser:
                auth_login(request, user)
                if next:
                    return redirect(next)
                return redirect("viveca_dashboard")
            else:
                context["error_msg"] = "Access denied for this user."
        context["form"] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        return kwargs


class DashboardView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/dashboard.html"

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            start = request.GET.get("start")
            end = request.GET.get("end")
            context = {}
            context["status"] = False
            stats = get_dashboard_stats(None, start, end)
            context["status"] = True
            context["stats"] = render_to_string(
                "viveca_dashboard/partials/dashboard_top_bar_stats.html", {"stats": stats}
            )
            context["music_research"] = self.get_music_research(start, end)
            context["top_songs"] = render_to_string(
                "viveca_dashboard/partials/dashboard_topsongs_table.html",
                {"topsongs": self.get_top_songs(start, end, context["music_research"])},
            )
            return self.render_to_json_response(context, **kwargs)
        return render(request, self.template_name, self.get_context_data())

    def get_random_colourcodes(self):
        def r():
            return random.randint(0, 255)

        return "#%02X%02X%02X" % (r(), r(), r())

    def get_music_research(self, start, end):
        result = []
        libraries = Library.objects.filter(
            dashboard_music_library__dashboard__date__gte=start,
            dashboard_music_library__dashboard__date__lte=end,
        )[:5]
        for library in libraries:
            researches = library.dashboard_music_library.all().filter(
                dashboard__date__gte=start, dashboard__date__lte=end
            )
            data = []
            for research in researches:
                musicresearch_data = research.dashboard_musicresearch_data.all()
                if musicresearch_data:
                    values = research.dashboard_musicresearch_data.all().values_list(
                        "value", flat=True
                    )
                    data += values
            if data:
                all_data = []
                i = 1
                for dat in data:
                    all_data.append([i, dat])
                    i += 1
                result.append(
                    {
                        "data": all_data,
                        "label": library.title,
                        "library_id": library.pk,
                        "color": self.get_random_colourcodes(),
                    }
                )
            if len(result) == 5:
                break
        return json.dumps(result[:5])

    def get_realtime_skips(self):
        realtimes = RealTimeSkipLibrary.objects.filter(
            dashboard__date=timezone.now().date()
        )
        result = []
        for realtime in realtimes:
            values = realtime.realtime_data.all().values_list("value", flat=True)
            if values:
                all_data = []
                i = 1
                for dat in values:
                    all_data.append([i, dat])
                    i += 1
                result.append(all_data)
        return json.dumps(result[:5])

    def get_top_songs(self, start, end, music_research):
        ids = []
        for data in json.loads(music_research):
            ids.append(data["library_id"])
        result = Library.objects.filter(id__in=ids)
        return result

    def get_context_data(self, **kwargs):
        start = get_days_before(29).date()
        end = timezone.now().date()
        # kwargs['realtime'] = self.get_realtime_skips()
        kwargs["stats"] = get_dashboard_stats(None, start, end)
        return kwargs


class AnalyticsView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/analytics.html"

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            start = request.GET.get("start")
            end = request.GET.get("end")
            context = {}
            context["status"] = False
            analytics = self.calculate_analytics(start, end)
            if analytics:
                context["analytics"] = analytics
                context["status"] = True
                context["html"] = render_to_string(
                    "viveca_dashboard/partials/analytics_tsu_table.html",
                    {"analytics": analytics},
                )
                context["stats"] = render_to_string(
                    "viveca_dashboard/partials/dashboard_top_bar_stats.html",
                    {"stats": analytics["stats"]},
                )
            return self.render_to_json_response(context, **kwargs)

        return render(request, self.template_name, self.get_context_data())

    def calculate_analytics(self, start, end):
        result = {}
        analytics = Analytics.objects.filter(date__gte=start, date__lte=end)
        if analytics:
            result["stats"] = get_dashboard_stats(analytics)
            result["male"] = (
                analytics.aggregate(Sum("male"))["male__sum"] / analytics.count()
            )
            result["female"] = (
                analytics.aggregate(Sum("female"))["female__sum"] / analytics.count()
            )
            result["iphone"] = (
                analytics.aggregate(Sum("iphone"))["iphone__sum"] / analytics.count()
            )
            result["android"] = (
                analytics.aggregate(Sum("android"))["android__sum"] / analytics.count()
            )
            result["web_palyer"] = (
                analytics.aggregate(Sum("web_palyer"))["web_palyer__sum"]
                / analytics.count()
            )

            stations = Stations.objects.all()
            tsu_results = []
            for station in stations:
                tsu_data = station.station_tsu.all().filter(
                    analytics__date__gte=start, analytics__date__lte=end
                )
                if tsu_data:
                    tsu_results.append(
                        {
                            "station": station.station_name,
                            "total_users": tsu_data.aggregate(Sum("total_users"))[
                                "total_users__sum"
                            ],
                            "avg_per_head": str(
                                tsu_data.aggregate(Sum("avg_per_head"))[
                                    "avg_per_head__sum"
                                ]
                            ),
                            "avg_hour_per_user": str(
                                tsu_data.aggregate(Sum("avg_hour_per_user"))[
                                    "avg_hour_per_user__sum"
                                ]
                            ),
                            "total_hours": tsu_data.aggregate(Sum("total_hours"))[
                                "total_hours__sum"
                            ],
                        }
                    )
                    result["tsu"] = tsu_results

        return result

    def get_context_data(self, **kwargs):
        start = get_days_before(29).date()
        end = timezone.now().date()
        kwargs["analytics"] = self.calculate_analytics(start, end)
        return kwargs


class LibraryView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/library.html"

    def get(self, request, *args, **kwargs):

        page_number = self.request.GET.get("page", 1)
        libraries = Library.objects.all()
        libraries = get_page_paginator(libraries, 5, int(page_number))

        if is_ajax(request):

            query = request.GET.get("q")
            sort = request.GET.get("order_by")
            station_id = request.GET.get("station")
            context = {}

            context["status"] = True

            if page_number:
                context = self.get_context_data()
                context["libraries"] = libraries
                return render(request, self.template_name, context)

            if station_id:
                station = Stations.objects.get(id=station_id)
                results = (
                    station.station_library.filter(
                        Q(library__title__icontains=query)
                        | Q(library__artistname__icontains=query)
                    )
                    if query
                    else station.station_library.all()[:10]
                )
                context["html"] = render_to_string(
                    "viveca_dashboard/partials/station_library_ajax_search.html",
                    {"station_libraries": results},
                )
            elif sort:
                if sort in ["title", "artistname"]:
                    results = Library.objects.all().order_by(sort)
                else:
                    results = Library.objects.all()

                libraries = get_page_paginator(results, 5, int(page_number))

                context["html"] = render_to_string(
                    "viveca_dashboard/partials/library_ajax_search.html",
                    {"results": libraries},
                )
            else:
                results = (
                    Library.objects.filter(
                        Q(title__icontains=query) | Q(artistname__icontains=query)
                    )
                    if query
                    else Library.objects.all()[:10]
                )
                context["html"] = render_to_string(
                    "viveca_dashboard/partials/library_ajax_search.html",
                    {"results": results},
                )
            return self.render_to_json_response(context, **kwargs)

        context = self.get_context_data()
        context["libraries"] = libraries
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        ids = request.POST.getlist("library")
        if action == "delete":
            datas = Library.objects.filter(id__in=ids)
            for data in datas:
                delete_linode_object(data.media)
                data.delete()
        elif action == "add-to-station":
            datas = StationLibrary.objects.filter(id__in=ids)
            datas.delete()
        return redirect("viveca_dashboard_library")

    def get_context_data(self, **kwargs):
        stations = Stations.objects.all()
        ref = self.request.GET.get("station_ref")

        if ref:
            stations = stations.filter(id=ref)

        kwargs["library_form"] = DashboardLibraryForm()
        kwargs["locations"] = Locations.objects.all()
        if stations:
            kwargs["station_form"] = DashboardSequenceForm(
                initial={"related_station": stations[0]}
            )
            kwargs["station_libraries"] = stations[0].station_library.all()
        else:
            kwargs["station_form"] = DashboardSequenceForm()
            kwargs["station_libraries"] = ""
        return kwargs


class AddToLibraryView(CreateView, JSONResponseMixin):
    model = Library
    form_class = DashboardLibraryForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddToLibraryView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_json_response({"error": "Method not allowed."}, **kwargs)

    def form_valid(self, form, **kwargs):
        context = {}
        context["status"] = True
        object = form.save()
        img_url = self.request.POST.get("image_url")
        if img_url:
            self.upload_cover_from_url(img_url, object)

        context["html"] = render_to_string(
            "viveca_dashboard/partials/library_add_edit_form.html", {"form": form}
        )
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/library_add_edit_form.html", {"form": form}
        )
        return self.render_to_json_response(context, **kwargs)

    def upload_cover_from_url(self, url, object):
        try:
            media_directory = os.path.join(settings.MEDIA_ROOT, "tmp")
            if not os.path.exists(media_directory):
                os.makedirs(media_directory)
            image_path = os.path.join(media_directory, "coverart.png")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                with open(image_path, "wb") as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            out_file.write(chunk)
                object_name = create_storage_filename("library", str(object.id) + ".png")
                with open(image_path, "rb") as img_file:
                    object.cover_art.save(object_name, File(img_file))
                os.remove(image_path)
        except Exception as e:
            logger.error("Error while saving image from URL:", e)


class MediaUploadView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(MediaUploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = True
        data = request.FILES.get("image")
        type = request.POST.get("type")
        if data and type:
            # name_value = 1
            # prev = MediaUpload.objects.filter(type=type).order_by("-id")
            # if prev:
            #     name_value = prev[0].name_id_val + 1
            # media = MediaUpload.objects.create(
            #     media=data, type=type, name_id_val=name_value
            # )

            content_type_parts = data.content_type.split("/")
            file_extension = content_type_parts[1] if len(content_type_parts) == 2 else ""

            if not file_extension:
                raise ValueError("Unable to determine file extension")

            # Generate a unique filename for the uploaded image
            img_name = str(uuid.uuid4()) + f".{file_extension}"

            # Save the uploaded file to a temporary location
            # Assuming MEDIA_ROOT is the directory where you want to save the temporary file
            temp_file_path = os.path.join(settings.MEDIA_ROOT, img_name)
            with open(temp_file_path, "wb") as temp_file:
                for chunk in data.chunks():
                    temp_file.write(chunk)

            linode_obj_config = {
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                "endpoint_url": settings.AWS_S3_ENDPOINT_URL,
            }

            client = boto3.client("s3", **linode_obj_config)
            client.upload_file(
                Filename=temp_file_path,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=img_name,
                ExtraArgs={"ACL": "public-read"},
            )

            url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{img_name}"
            # Clean up: remove the temporary file
            os.remove(temp_file_path)

            # context["media"] = "%s" % (media.media.url)
            context["media"] = url
            context["audio"] = render_to_string(
                "viveca_dashboard/partials/audio_player_ajax.html",
                {"media_url": context["media"]},
            )
        else:
            context["status"] = False
            context["media"] = ""
            context["audio"] = render_to_string(
                "viveca_dashboard/partials/audio_player_ajax.html",
            )
        return self.render_to_json_response(context, **kwargs)


class EditLibraryPopupView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditLibraryPopupView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        id = request.POST.get("library")
        library = Library.objects.get(id=id)
        if library:
            form = DashboardLibraryForm(instance=library)
            context["html"] = render_to_string(
                "viveca_dashboard/partials/library_add_edit_form.html",
                {"form": form, "library": library},
            )
            context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class EditLibraryView(UpdateView, JSONResponseMixin):
    model = Library
    form_class = DashboardLibraryForm
    template_name = "viveca_dashboard/partials/library_add_edit_form.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditLibraryView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        context = {}
        context["status"] = True
        object = form.save()
        img_url = self.request.POST.get("image_url")
        if img_url:
            self.upload_cover_from_url(img_url, object)

        updated_form = DashboardLibraryForm(instance=object)

        context["html"] = render_to_string(
            self.template_name, {"form": updated_form, "library": object}
        )
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            self.template_name, {"form": form, "library": self.object}
        )
        return self.render_to_json_response(context, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(self.get_form_class())
        form = DashboardLibraryForm(request.POST, request.FILES, instance=self.object)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def upload_cover_from_url(self, url, object):
        try:
            media_directory = os.path.join(settings.MEDIA_ROOT, "tmp")
            if not os.path.exists(media_directory):
                os.makedirs(media_directory)
            image_path = os.path.join(media_directory, "coverart.png")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                with open(image_path, "wb") as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            out_file.write(chunk)
                object_name = create_storage_filename("library", str(object.id) + ".png")
                with open(image_path, "rb") as img_file:
                    object.cover_art.save(object_name, File(img_file))
                os.remove(image_path)
        except Exception as e:
            logger.error("Error while saving image from URL:", e)


class UpdateStationPointsView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdateStationPointsView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        id = request.POST.get("st_library")
        points = request.POST.get("points")
        if id:
            library = StationLibrary.objects.get(id=id)
            library.points = points
            library.save()
            context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class AddToStationView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddToStationView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = DashboardSequenceForm(request.POST)
        if form.is_valid():
            station = form.get_station()
            ids = request.POST.getlist("library")
            datas = Library.objects.filter(id__in=ids)
            for data in datas:
                added, created = StationLibrary.objects.get_or_create(
                    station=station, library=data
                )
                if created:
                    added.points = data.love_rating
                    added.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class LibraryGeneratePlaylist(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LibraryGeneratePlaylist, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        form = DashboardSequenceForm(request.POST)
        location = request.POST.get("location")
        if form.is_valid() and location:
            station = form.get_station()
            if location == "all":
                playlist = Playlist(station)
            else:
                loc = Locations.objects.get(id=location)
                playlist = Playlist(station, loc)
            playlists = playlist.generate_playlist()
            context["status"] = True
            results = []
            for play in playlists:
                content = play.content_type.model_class()
                object = content.objects.get(id=play.object_id)
                data = {
                    "title": object.title,
                    "type": object.__class__.__name__,
                    "media": object.media,
                    "id": play.object_id,
                }
                results.append(data)
            context["html"] = render_to_string(
                "viveca_dashboard/partials/show_playlist_modal.html", {"results": results}
            )
        return self.render_to_json_response(context, **kwargs)


class PodcastsView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/podcasts.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PodcastsView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        edit = request.GET.get("edit")
        object = Wall.objects.filter(id=edit)
        if object:
            context["form"] = DashboardWallForm(instance=object[0])
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        station_ref = request.GET.get("station_ref", "")
        redirect_url = (
            reverse("viveca_dashboard_podcasts") + f"?station_ref={station_ref}"
        )
        if is_ajax(request):
            if "delete" in request.POST.keys():
                Wall.objects.filter(id=request.POST.get("delete")).delete()
                return self.render_to_json_response({"status": True})
        form = DashboardWallForm(request.POST, request.FILES)
        edit = request.GET.get("edit")
        object = Wall.objects.filter(id=edit)
        if object:
            form = DashboardWallForm(request.POST, request.FILES, instance=object[0])
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
        context = self.get_context_data()
        context["form"] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        stations = Stations.objects.all()
        kwargs["form"] = DashboardWallForm()
        station_ref = self.request.GET.get("station_ref")
        if station_ref:
            stations = stations.filter(id=station_ref)
        kwargs["contents"] = stations[0].station_wall_contents.all() if stations else []
        kwargs["form"] = (
            DashboardWallForm(initial={"related_station": stations[0]})
            if stations
            else DashboardWallForm()
        )

        return kwargs


class ScheduleView(View):
    template_name = "viveca_dashboard/schedule.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        ids = request.POST.getlist("tohs")
        if action == "delete-tohs":
            datas = BrandingTOH.objects.filter(id__in=ids)
            for data in datas:
                delete_linode_object(data.media)
                data.delete()
        return redirect("viveca_dashboard_schedule")

    def get_context_data(self, **kwargs):
        stations = Stations.objects.all()
        station_ref = self.request.GET.get("station_ref")
        location_ref = self.request.GET.get("location_ref")
        if station_ref:
            stations = stations.filter(id=station_ref)
        locations = None
        if location_ref:
            locations = Locations.objects.filter(id=location_ref)

        kwargs["schedule_form"] = DashboardSchedulingForm()
        kwargs["station_location_form"] = DashboardStationLocationForm()

        kwargs["brandingtoh_form"] = DashboardBrandingTOHForm()
        brandingtohs = []
        if stations:
            objects = stations[0].station_branding_toh.all()
            brandingtohs = (
                objects.filter(location=locations[0])
                if locations
                else objects.filter(location__isnull=True)
            )
        kwargs["brandingtohs"] = brandingtohs
        return kwargs


class ScheduleAjaxView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ScheduleAjaxView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        station_form = DashboardSequenceForm(request.POST)
        if station_form.is_valid():
            station = station_form.get_station()
            try:
                schedule = station.station_schedules
            except:
                form = DashboardSchedulingForm(initial={"related_station": station})
                context["html"] = render_to_string(
                    "viveca_dashboard/partials/schedule_add_edit_form.html",
                    {"form": form},
                )
            else:
                form = DashboardSchedulingForm(instance=schedule)
                context["html"] = render_to_string(
                    "viveca_dashboard/partials/schedule_add_edit_form.html",
                    {"form": form, "schedule": schedule},
                )
            context["status"] = True

        return self.render_to_json_response(context, **kwargs)


class AddScheduleView(CreateView, JSONResponseMixin):
    model = Scheduling
    form_class = DashboardSchedulingForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddScheduleView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        obj = form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/schedule_add_edit_form.html", {"form": form}
        )
        return self.render_to_json_response(context, **kwargs)


class EditScheduleView(UpdateView, JSONResponseMixin):
    model = Scheduling
    form_class = DashboardSchedulingForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditScheduleView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/schedule_add_edit_form.html",
            {"form": form, "schedule": self.get_object()},
        )
        return self.render_to_json_response(context, **kwargs)


class AddBrandingTOHView(CreateView, JSONResponseMixin):
    model = BrandingTOH
    form_class = DashboardBrandingTOHForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddBrandingTOHView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        obj = form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/brandingtoh_add_edit_form.html", {"form": form}
        )
        return self.render_to_json_response(context, **kwargs)


class EditBrandingTOHPopupView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditBrandingTOHPopupView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        id = request.POST.get("tohs")
        toh = BrandingTOH.objects.get(id=id)
        if toh:
            form = DashboardBrandingTOHForm(instance=toh)
            context["html"] = render_to_string(
                "viveca_dashboard/partials/brandingtoh_add_edit_form.html",
                {"form": form, "toh": toh},
            )
            context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class EditBrandingTOHView(UpdateView, JSONResponseMixin):
    model = BrandingTOH
    form_class = DashboardBrandingTOHForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditBrandingTOHView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/brandingtoh_add_edit_form.html",
            {"form": form, "toh": self.get_object()},
        )
        return self.render_to_json_response(context, **kwargs)


class AdvertView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/adverts.html"

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            query = request.GET.get("q")
            if query == "":
                results = Adverts.objects.all()[:10]
            else:
                results = Adverts.objects.filter(
                    Q(title__icontains=query) | Q(type__icontains=query)
                )
            context = {}
            context["status"] = True
            context["html"] = render_to_string(
                "viveca_dashboard/partials/advert_ajax_search.html", {"adverts": results}
            )
            return self.render_to_json_response(context, **kwargs)
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        ids = request.POST.getlist("advert")
        datas = Adverts.objects.filter(id__in=ids)
        if action == "delete":
            for data in datas:
                delete_linode_object(data.media)
                data.delete()
        elif action == "type":
            datas.update(type="")
        return redirect("viveca_dashboard_advert")

    def get_context_data(self, **kwargs):
        kwargs["advert_form"] = DashboardAdvertForm()
        kwargs["adverts"] = Adverts.objects.all()
        kwargs["adverts_banner"] = Adverts.objects.filter(type="banner")
        return kwargs


class AdvertAjaxView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AdvertAjaxView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        type = request.POST.get("type")
        query = request.POST.get("q")
        if type:
            result = Adverts.objects.filter(type=type)
            if query:
                result = result.filter(
                    Q(title__icontains=query) | Q(type__icontains=query)
                )
            context["status"] = True
            context["html"] = render_to_string(
                "viveca_dashboard/partials/advert_type_ajax_list.html",
                {"adverts_banner": result},
            )

        return self.render_to_json_response(context, **kwargs)


class AddAdvertView(CreateView, JSONResponseMixin):
    model = Adverts
    form_class = DashboardAdvertForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddAdvertView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        if is_ajax(self.request):
            context = {}
            context["status"] = True
            return self.render_to_json_response(context, **kwargs)
        else:
            object = form.save()
        return redirect("viveca_dashboard_advert")

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/advert_add_edit_form.html",
            {
                "form": form,
            },
        )
        return self.render_to_json_response(context, **kwargs)


class EditAdvertPopupView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditAdvertPopupView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        id = request.POST.get("advert")
        advert = Adverts.objects.get(id=id)
        if advert:
            form = DashboardAdvertForm(instance=advert)
            context["html"] = render_to_string(
                "viveca_dashboard/partials/advert_add_edit_form.html",
                {"form": form, "advert": advert},
            )
            context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class EditAdvertView(UpdateView, JSONResponseMixin):
    model = Adverts
    form_class = DashboardAdvertForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditAdvertView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        if is_ajax(self.request):
            context = {}
            context["status"] = True
            return self.render_to_json_response(context, **kwargs)
        else:
            object = form.save()
        return redirect("viveca_dashboard_advert")

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/advert_add_edit_form.html",
            {"form": form, "advert": self.get_object()},
        )
        return self.render_to_json_response(context, **kwargs)


class PlaylistView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/playlist.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PlaylistView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if "reorder" in request.POST:
            ids = request.POST.getlist("reordered")
            list_preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
            data_list = StationPlaylist.objects.filter(id__in=ids).order_by(
                list_preserved
            )
            self.reorder_items(data_list) if data_list and data_list.count() >= 2 else 0

        if "delete" in request.POST:
            ids = request.POST.getlist("id")
            datas = StationPlaylist.objects.filter(id__in=ids)
            if datas:
                datas.delete()

        if "save" in request.POST:
            ids = request.POST.getlist("skipped")
            all_ids = request.POST.getlist("reordered")
            skipped = StationPlaylist.objects.filter(id__in=ids)
            not_skipped = StationPlaylist.objects.filter(id__in=all_ids).exclude(
                id__in=ids
            )
            if skipped:
                skipped.update(skipped=True)
            if not_skipped:
                not_skipped.update(skipped=False)

        if "export" in request.POST:
            context = {}
            context["redirect"] = reverse("viveca_dashboard_reports_playlist")
            station = request.POST.get("station")
            location = request.POST.get("location")
            # obj_station = Stations.objects.get(id = station)
            lat = "all"
            longi = "all"
            loc = None
            if not location == "all":
                loc = Locations.objects.get(id=location)
                lat = loc.location_lat
                longi = loc.location_long

            export = export_palylist(loc, station, lat, longi)
            context["redirect"] = reverse(
                "viveca_dashboard_reports_playlist_export"
            ) + "?station=%s&location=%s" % (station, location)
            return self.render_to_json_response(context, **kwargs)

        return redirect("viveca_dashboard_reports_playlist")

    def reorder_items(self, data_list):
        for index, item in enumerate(data_list):
            item.position = index + 1
            item.save()

    def get_context_data(self, **kwargs):
        location = self.request.GET.get("location_ref", "all")
        station_id = self.request.GET.get("station_ref")
        loc = None
        stations = []
        try:
            if not location == "all":
                loc = Locations.objects.filter(id=location)
            if station_id:
                stations = Stations.objects.filter(id=station_id)
            else:
                stations = Stations.objects.all().order_by("id")

            if loc:
                kwargs["playlist"] = (
                    stations[0].station_playlist.all().filter(location=loc[0])
                    if stations
                    else []
                )
            else:
                kwargs["playlist"] = (
                    stations[0].station_playlist.all().filter(location=None)
                    if stations
                    else []
                )
        except:
            kwargs["playlist"] = []
        kwargs["global_playlist"] = GlobalPlaylist.objects.all().order_by("-id")
        kwargs["stations"] = Stations.objects.all().order_by("id")
        kwargs["position"] = (
            [i + 1 for i in range(kwargs["playlist"].count())] if stations else []
        )
        kwargs["locations"] = Locations.objects.all()
        return kwargs


class PlaylistSearch(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PlaylistSearch, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        type = request.POST.get("type")
        q = request.POST.get("q")
        context = {}
        results = []
        if type == "music" and q:
            datas = Library.objects.filter(title__icontains=q)
            for result in datas:
                results.append(
                    {
                        "title": result.title,
                        "artist": result.artistname,
                        "id": result.pk,
                    }
                )

        if type == "branding" and q:
            datas = BrandingTOH.objects.filter(title__icontains=q)
            for result in datas:
                results.append({"title": result.title, "artist": "-", "id": result.pk})

        if type == "advert" and q:
            datas = Adverts.objects.filter(title__icontains=q)
            for result in datas:
                results.append({"title": result.title, "artist": "-", "id": result.pk})

        context["html"] = render_to_string(
            "viveca_dashboard/partials/playlist_search_table.html", {"results": results}
        )
        return self.render_to_json_response(context, **kwargs)


class PlaylistInsertToPlaylist(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PlaylistInsertToPlaylist, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return redirect("viveca_dashboard_reports_playlist")

    def post(self, request, *args, **kwargs):
        loc = None
        type = request.POST.get("type")
        ids = request.POST.getlist("item")
        stationid = request.POST.get("station")
        station = Stations.objects.get(id=stationid)
        location = request.POST.get("location", "all")
        if not location == "all":
            loc = Locations.objects.get(id=location)
        playlist = station.station_playlist.all().filter(location=loc).reverse()

        if type == "music":
            datas = Library.objects.filter(id__in=ids)
            max = playlist[0].position if playlist else 0
            for data in datas:
                max = max + 1
                library = StationPlaylist.objects.create(
                    station=station, content_object=data, position=max, location=loc
                )
        if type == "branding":
            datas = BrandingTOH.objects.filter(id__in=ids)
            max = playlist[0].position if playlist else 0
            for data in datas:
                max = max + 1
                library = StationPlaylist.objects.create(
                    station=station, content_object=data, position=max, location=loc
                )
        if type == "advert":
            datas = Adverts.objects.filter(id__in=ids)
            max = playlist[0].position if playlist else 0
            for data in datas:
                max = max + 1
                library = StationPlaylist.objects.create(
                    station=station, content_object=data, position=max, location=loc
                )
        return redirect("viveca_dashboard_reports_playlist")


class PlaylistExportView(View):
    template_name = "viveca_dashboard/partials/playlist_export.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        station = self.request.GET.get("station")
        location = self.request.GET.get("location")
        if location == "all":
            kwargs["datas"] = ExportPlaylist.objects.filter(
                station__id=station, location__isnull=True
            )
        else:
            kwargs["datas"] = ExportPlaylist.objects.filter(
                station__id=station, location__id=location
            )
        kwargs["json_url"] = reverse(
            "playlist_export_json"
        ) + "?station=%s&location=%s&type=json" % (station, location)
        return kwargs


class PlaylistSocialPostData(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PlaylistSocialPostData, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        url = request.POST.get("post_url")
        type = request.POST.get("post_type")
        if type == "twitter":
            api = request.session.get("TWITTER_API_OBJECT")
            api = twitter.Api(
                consumer_key=settings.TWITTER_CONSUMER_KEY,
                consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                access_token_key=settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            )
            tw_id = url.split("/")[-1]
            status = api.GetStatus(tw_id)
            context["status"] = True
            context["text"] = status.text
            context["media"] = status.media[0]["media_url"]
        if type == "instagram":
            stage_1_url = "http://api.instagram.com/publicapi/oembed/?url=%s" % (url)
            content_1 = urllib.urlopen(stage_1_url).read()
            content_1_data = json.loads(content_1)
            if "media_id" in content_1_data.keys():
                context["status"] = True
                context["text"] = content_1_data["title"]
                if "thumbnail_url" in content_1_data:
                    context["media"] = content_1_data["thumbnail_url"]
                else:
                    stage_2_url = "https://api.instagram.com/v1/media/%s?client_id=%s" % (
                        content_1_data["media_id"],
                        settings.INSTAGRAM_CLIENT_ID,
                    )
                    content_2 = urllib.urlopen(stage_2_url).read()
                    content_2_data = json.loads(content_2)
                    context["media"] = content_2_data["data"]["images"][
                        "standard_resolution"
                    ]["url"]
        return self.render_to_json_response(context, **kwargs)


class AiVoicetracksView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/ai_voicetracks.html"

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            query = request.GET.get("q")
            station = request.GET.get("related_station")
            tracks = DJTracks.objects.filter(dj__station__id=station).filter(
                Q(title__icontains=query) | Q(dj__user__username__icontains=query)
            )
            context = {}
            context["status"] = True
            context["html"] = render_to_string(
                "viveca_dashboard/partials/dj_tracks_search.html", {"tracks": tracks}
            )
            return self.render_to_json_response(context, **kwargs)
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            ids = request.POST.getlist("tracks")
            datas = DJTracks.objects.filter(id__in=ids)
            if datas:
                datas.delete()

        if "save" in request.POST:
            ids = request.POST.getlist("published")
            all_ids = request.POST.getlist("id")
            published = DJTracks.objects.filter(id__in=ids)
            notpublished = DJTracks.objects.filter(id__in=all_ids).exclude(id__in=ids)
            if published:
                published.update(published=True)
            if notpublished:
                notpublished.update(published=False)

        return redirect("viveca_dashboard_ai_voicetracks")

    def get_context_data(self, **kwargs):
        location = self.request.GET.get("location_ref", "all")
        station_id = self.request.GET.get("station_ref")
        try:
            current_station = Stations.objects.get(id=station_id)
            kwargs["topic_prompts"] = TopicPrompts.objects.filter(station=current_station)
            kwargs["position_prompts"] = PositionPrompts.objects.filter(
                station=current_station
            )
        except:
            pass
        loc = None
        stations = []
        kwargs["stations"] = Stations.objects.all().order_by("id")
        kwargs["locations"] = Locations.objects.all()

        try:
            if not location == "all":
                loc = Locations.objects.filter(id=location)
            if station_id:
                stations = Stations.objects.filter(id=station_id)
            else:
                stations = Stations.objects.all().order_by("id")

            if loc:
                kwargs["playlist"] = (
                    stations[0].station_playlist.all().filter(location=loc[0])
                    if stations
                    else []
                )
            else:
                kwargs["playlist"] = (
                    stations[0].station_playlist.all().filter(location=None)
                    if stations
                    else []
                )
        except:
            kwargs["playlist"] = []

        kwargs["position"] = (
            [i + 1 for i in range(kwargs["playlist"].count())] if stations else []
        )

        return kwargs


class AiVoicetracksGenerateVoicetrackView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AiVoicetracksGenerateVoicetrackView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        status = True
        words_limit_placeholder = "- words_limit_prompt_placeholder"
        previous_artist_placeholder = "- previous_artist_prompt_placeholder"
        next_song_placeholder = "- next_song_prompt_placeholder"

        previous_artist = None
        next_song = None

        prev_song_id = request.POST.get("prev_song_id", None)
        next_song_id = request.POST.get("next_song_id", None)
        station_id = request.POST.get("station_id")
        words_limit = request.POST.get("words_limit")
        position_prompt_id = request.POST.get("position_prompt_id")

        try:
            system_prompt = Stations.objects.get(id=station_id).system_prompt
            user_prompt = PositionPrompts.objects.get(id=position_prompt_id).prompt

            if prev_song_id:
                previous_track = Library.objects.get(id=prev_song_id)
                previous_artist = previous_track.artistname

            if next_song_id:
                next_track = Library.objects.get(id=next_song_id)
                next_song = next_track.artistname + " - " + next_track.title

            if user_prompt and words_limit_placeholder in user_prompt:
                words_limit_prompt = f"- use no more than {words_limit} words"
                user_prompt = user_prompt.replace(
                    words_limit_placeholder, words_limit_prompt
                )

            if user_prompt and previous_artist_placeholder in user_prompt:
                previous_artist_prompt = (
                    f'- previous artist = "{previous_artist}"' if previous_artist else ""
                )
                user_prompt = user_prompt.replace(
                    previous_artist_placeholder, previous_artist_prompt
                )

            if user_prompt and next_song_placeholder in user_prompt:
                next_song_prompt = f'- next song = "{next_song}"' if next_song else ""
                user_prompt = user_prompt.replace(next_song_placeholder, next_song_prompt)

            if system_prompt and user_prompt:
                response = generate_voicetrack_from_prompts(system_prompt, user_prompt)
                if response.message and response.message.content:
                    context = response.message.content
            else:
                context = "Failed to generate a voicetrack with the current prompts!"
                status = False

        except:
            context = "Error while getting prompts!"
            status = False

        response = HttpResponse(context, content_type="application/json")
        if not status:
            response.status_code = 400
        return response


class AiVoicetracksEditInAux(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AiVoicetracksEditInAux, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        id = request.POST.get("object")
        in_val = request.POST.get("in_point")
        aux_val = request.POST.get("aux_point")
        if in_val and aux_val:
            track = DJTracks.objects.filter(id=id)
            if track:
                if not in_val == "" and not aux_val == "":
                    track[0].in_point = in_val
                    track[0].aux_point = aux_val
                    track[0].save()

        if is_ajax(request):
            context = {}
            context["status"] = False
            tracks = request.POST.getlist("tracks")
            if tracks:
                id = tracks[0]
                track = DJTracks.objects.filter(id=id)
                if track:
                    context["status"] = True
                    context["html"] = render_to_string(
                        "viveca_dashboard/partials/ai_voicetracks_dj_inaux.html",
                        {"object": track[0]},
                    )
            return self.render_to_json_response(context, **kwargs)
        return redirect("viveca_dashboard_ai_voicetracks")


class AiVoicetracksAddMusicBed(View, JSONResponseMixin):
    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            context = {}
            type = request.GET.get("type")
            id = request.GET.get("id")
            if type and id:
                if type == "delete":
                    DJMusicBed.objects.filter(id=id).delete()
                    context["status"] = True
            return self.render_to_json_response(context, **kwargs)
        return redirect("viveca_dashboard_ai_voicetracks")

    def post(self, request, *args, **kwargs):
        form = DashboardDJMusicBedForm(request.POST)
        next = request.POST.get("next")
        if form.is_valid():
            form.save()
        if next:
            return redirect(next)
        return redirect("viveca_dashboard_ai_voicetracks")


class NewsView(View, JSONResponseMixin):
    form_class = NewsGenerateForm
    template_name = "viveca_dashboard/news.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(NewsView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            context = {}
            context["status"] = True
            return self.render_to_json_response(context, **kwargs)
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        context = {}
        if form.is_valid():
            context["status"] = True
            params = {
                "voice_code": form.cleaned_data["voice_code"],
                "location_code": form.cleaned_data["location_code"],
                "no_of_stories": form.cleaned_data["no_of_stories"],
            }
            newsgenerator_endpoint = "https://newsgenerator.radiostation.ai/generate/news"
            newsgenerator_endpoint += "?" + urlencode(params)
            headers = {"accept": "application/json"}

            response = requests.get(newsgenerator_endpoint, headers=headers)
            context["form"] = render_to_string(
                "viveca_dashboard/partials/news_generate_form.html", {"form": form}
            )
            if response.status_code == 200:
                context["status"] = True
                context["response"] = response.json()
            else:
                context["status"] = False
                context["error"] = response.text
            return self.render_to_json_response(context, **kwargs)
        else:
            context["status"] = False
            context["form"] = render_to_string(
                "viveca_dashboard/partials/news_generate_form.html", {"form": form}
            )
            return self.render_to_json_response(context, **kwargs)

    def get_context_data(self, **kwargs):
        form = NewsGenerateForm()
        kwargs["form"] = form
        kwargs["voice_codes"] = form.get_voices()
        return kwargs


class GenerateNewsAudio(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GenerateNewsAudio, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_json_response({"error": "Method not allowed."}, **kwargs)

    def post(self, request, *args, **kwargs):
        text = request.POST.get("text")
        voice_code = request.POST.get("voice_code")
        elevenlabs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        generated_audio = elevenlabs_client.generate(
            text=text,
            voice=voice_code,
            model="eleven_multilingual_v2",
        )
        generated_audio_bytes = b"".join(generated_audio)

        # Create main audio from bytes directly
        main_audio = AudioSegment.from_file(BytesIO(generated_audio_bytes), format="mp3")
        main_audio = main_audio.speedup(playback_speed=1.1)

        static_file_path = os.path.join(
            "static/audio/tmp/", self.generate_random_string(length=6) + ".mp3"
        )

        # Export the main audio to a temporary MP3 file
        main_audio.export(static_file_path, format="mp3")

        # Convert the MP3 file to WAV format
        wav_path = self.convert_to_wav(filepath=static_file_path)

        # Enhance the WAV file
        enhanced_path = self.enhance(wav_path, self.generate_random_string(6))

        # Prepare the output directory path
        media_directory = os.path.join(settings.MEDIA_ROOT, "tmp")
        if not os.path.exists(media_directory):
            os.makedirs(media_directory)
        file_path = os.path.join(
            media_directory, self.generate_random_string(length=10) + ".mp3"
        )

        # Load the enhanced audio
        main_audio = AudioSegment.from_wav(enhanced_path)

        # Export the enhanced audio to the original file path
        main_audio.export(file_path, format="mp3")

        # Normalize the audio
        normalized_file_path = self.normalize_audio(
            input_file=file_path, output_file=file_path
        )

        os.remove(wav_path)
        os.remove(enhanced_path)
        os.remove(static_file_path)
        context = {
            "status": True,
            "audio_url": normalized_file_path,
        }

        return self.render_to_json_response(context, **kwargs)

    def generate_random_string(self, length):
        return "".join(random.choices(string.ascii_letters, k=length))

    def convert_to_wav(self, filepath: str):
        tmp_path = filepath.replace(".mp3", ".wav")
        command = [
            "ffmpeg",
            "-y",
            "-i",
            filepath,
            "-af",
            "highpass=f=100",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "2",
            "-ar",
            "44100",
            tmp_path,
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to convert audio to WAV format")
            raise e
        return tmp_path

    def enhance(self, filepath: str, new_filename: str):
        output_path = filepath.replace(os.path.basename(filepath), f"{new_filename}.wav")
        command = [
            "static/audio/stereotool",
            "-q",
            "-k",
            "<3f1ca7de5f8577384785b979b98bc571414141712197e3e40a78ac5ab85a>",
            "-s",
            "static/audio/micProcessing.sts",
            filepath,
            output_path,
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to enhance audio")
            raise e
        return output_path

    def normalize_audio(self, input_file: str, output_file: str, target_db: int = -5):
        command = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-af",
            f"loudnorm=I={target_db}:LRA=11:TP=-1.5",
            output_file,
        ]
        try:
            subprocess.run(command)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to normalize audio:", e)
            raise e
        return output_file


class ExportNewsAudio(View, JSONResponseMixin):
    def get(self, request, *args, **kwargs):
        return self.render_to_json_response({"error": "Method not allowed."}, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        intro_url = request.POST.get("intro", None)
        news_url = request.POST.get("news", None)
        news_2_url = request.POST.get("news_2", None)
        news_3_url = request.POST.get("news_3", None)
        news_4_url = request.POST.get("news_4", None)
        news_5_url = request.POST.get("news_5", None)
        entertainment_url = request.POST.get("entertainment", None)
        sports_url = request.POST.get("sports", None)
        weather_url = request.POST.get("weather", None)
        outro_url = request.POST.get("outro", None)
        newsbed_str = request.POST.get("newsbed", "false")
        newsbed = newsbed_str.lower() == "true"
        seperator_str = request.POST.get("seperator", "false")
        seperator = seperator_str.lower() == "true"
        weatherbed_str = request.POST.get("weatherbed", "false")
        weatherbed = weatherbed_str.lower() == "true"
        bulletin_duration = request.POST.get("bulletin_duration", 0)

        intro_audio = None
        news_audio = None
        news_2_audio = None
        news_3_audio = None
        news_4_audio = None
        news_5_audio = None
        entertainment_audio = None
        sports_audio = None
        weather_audio = None
        outro_audio = None

        if intro_url:
            intro_audio = AudioSegment.from_mp3(intro_url)
        if news_url:
            news_audio = AudioSegment.from_mp3(news_url)
        if news_2_url:
            news_2_audio = AudioSegment.from_mp3(news_2_url)
        if news_3_url:
            news_3_audio = AudioSegment.from_mp3(news_3_url)
        if news_4_url:
            news_4_audio = AudioSegment.from_mp3(news_4_url)
        if news_5_url:
            news_5_audio = AudioSegment.from_mp3(news_5_url)
        if entertainment_url:
            entertainment_audio = AudioSegment.from_mp3(entertainment_url)
        if sports_url:
            sports_audio = AudioSegment.from_mp3(sports_url)
        if weather_url:
            weather_audio = AudioSegment.from_mp3(weather_url)
        if outro_url:
            outro_audio = AudioSegment.from_mp3(outro_url)

        # join news audio having in mind missing audio and separator
        separator_audio = AudioSegment.from_mp3("static/audio/beep.mp3")
        silent_1sec_audio = AudioSegment.silent(duration=1 * 1000)
        news_audios_to_join = [
            audio
            for audio in [
                news_audio,
                news_2_audio,
                news_3_audio,
                news_4_audio,
                news_5_audio,
                entertainment_audio,
                sports_audio,
            ]
            if audio is not None
        ]
        if len(news_audios_to_join) == 1:
            news_mix_audio = news_audios_to_join[0]
        elif len(news_audios_to_join) > 1:
            news_mix_audio = news_audios_to_join[0]
            for audio in news_audios_to_join[1:]:
                if seperator:
                    news_mix_audio = news_mix_audio + separator_audio + audio
                else:
                    news_mix_audio = news_mix_audio + silent_1sec_audio + audio
        else:
            news_mix_audio = None

        # try to join intro and the created newsmix audio if they exist
        if intro_audio and news_mix_audio:
            silent_half_second_audio = AudioSegment.silent(duration=1000 / 2)
            intro_and_news_audio = intro_audio + silent_half_second_audio + news_mix_audio
        elif intro_audio:
            intro_and_news_audio = intro_audio
        elif news_mix_audio:
            intro_and_news_audio = news_mix_audio
        else:
            intro_and_news_audio = None

        # add 1 empty second to the intro and news audio and overlay newsbed if selected
        if intro_and_news_audio:
            current_length = len(intro_and_news_audio)
            intro_and_news_audio += silent_1sec_audio
            if newsbed:
                newsbed_audio = AudioSegment.from_mp3("static/audio/newsbed.mp3") + 5
                newsbed_audio = newsbed_audio[: len(intro_and_news_audio)]
                newsbed_audio.fade_out(current_length)
                intro_and_news_audio = intro_and_news_audio.overlay(newsbed_audio)

        # join weather audio and outro if they exist
        if weather_audio and outro_audio:
            weather_and_outro_audio = weather_audio + outro_audio
        elif weather_audio:
            weather_and_outro_audio = weather_audio
        elif outro_audio:
            weather_and_outro_audio = outro_audio
        else:
            weather_and_outro_audio = None

        # add weatherbed overlay if selected only to the weather and outro
        if weather_and_outro_audio and weatherbed:
            weatherbed_audio = AudioSegment.from_mp3("static/audio/weatherbed.mp3")
            delay = 1 * 1000
            tmp_weather_audio = weatherbed_audio[:delay]
            tmp_weather_audio += weatherbed_audio[
                delay : (2 * delay) + len(weather_and_outro_audio)
            ].overlay(weather_and_outro_audio)
            weather_and_outro_audio = tmp_weather_audio

        if intro_and_news_audio and weather_and_outro_audio:
            main_audio = intro_and_news_audio + weather_and_outro_audio
        elif intro_and_news_audio:
            main_audio = intro_and_news_audio
        elif weather_and_outro_audio:
            main_audio = weather_and_outro_audio

        news_directory = os.path.join(settings.MEDIA_ROOT, "generated")
        if not os.path.exists(news_directory):
            os.makedirs(news_directory)
        file_path = os.path.join(news_directory, "news.wav")
        main_audio.export(file_path, format="wav")

        context = {}
        context["status"] = True
        context["audio_url"] = file_path

        return self.render_to_json_response(context, **kwargs)


class AddNewsToPlaylist(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddNewsToPlaylist, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_json_response({"error": "Method not allowed."}, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        context = {}
        audio_url = request.POST.get("audio_url")
        audio_name = "news.wav"
        if audio_url:
            linode_obj_config = {
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                "endpoint_url": settings.AWS_S3_ENDPOINT_URL,
            }
            client = boto3.client("s3", **linode_obj_config)
            client.upload_file(
                Filename=audio_url,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=audio_name,
                ExtraArgs={"ACL": "public-read"},
            )
            url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{audio_name}"
            context["status"] = True
            context["media"] = url

            try:
                global_playlist, _ = GlobalPlaylist.objects.get_or_create(type=1)
                global_playlist.media = url
                global_playlist.updated = timezone.now()
                global_playlist.save()
            except Exception as e:
                context["status"] = False
                context["media"] = ""
                context["issue"] = "Failed to create/update Global Playlist item!"

        else:
            context["status"] = False
            context["media"] = ""
            context["issue"] = "No audio file provided!"

        return self.render_to_json_response(context, **kwargs)


class SettingUserView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/setting_users.html"

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            users = self.get_context_data()["users"]
            query = request.GET.get("q")
            if query == "":
                results = users[:10]
            results = users.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
            context = {}
            context["status"] = True
            context["html"] = render_to_string(
                "viveca_dashboard/partials/setting_user_search.html", {"users": results}
            )
            return self.render_to_json_response(context, **kwargs)
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist("users")
        datas = User.objects.filter(id__in=ids)
        for data in datas:
            if data.dj_user:
                data.dj_user.delete()
                data.dj_user.dj_user_tracks.all().delete()
            data.delete()
        return redirect("viveca_dashboard_setting_user")

    def get_context_data(self, **kwargs):
        show = self.request.GET.get("show")
        if show == "dj":
            group = Group.objects.filter(name="DJ")
            users = User.objects.filter(groups__in=[group[0].pk]) if group else []
            kwargs["users"] = users
        else:
            kwargs["users"] = User.objects.all()
        kwargs["user_form"] = DashboardUserForm()

        return kwargs


class EditSettingUserPopupView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditSettingUserPopupView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        id = request.POST.get("users")
        user = User.objects.get(id=id)
        if user:
            form = DashboardUserEditForm(
                instance=user,
                initial={
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                },
            )
            context["html"] = render_to_string(
                "viveca_dashboard/partials/user_creation_form.html",
                {"form": form, "user_obj": user},
            )
            context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class AddSettingUserView(CreateView, JSONResponseMixin):
    model = User
    form_class = DashboardUserForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddSettingUserView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        obj = form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/user_creation_form.html",
            {
                "form": form,
            },
        )
        return self.render_to_json_response(context, **kwargs)


class UpdateSettingUserView(UpdateView, JSONResponseMixin):
    model = User
    form_class = DashboardUserEditForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSettingUserView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        obj = form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/user_creation_form.html",
            {"form": form, "user_obj": self.get_object()},
        )
        return self.render_to_json_response(context, **kwargs)


class SettingStationView(View, JSONResponseMixin):
    template_name = "viveca_dashboard/setting_station.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SettingStationView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            stations = self.get_context_data()["stations"]
            query = request.GET.get("q")
            stations = stations.filter(Q(station_name__icontains=query))
            context = {}
            context["status"] = True
            context["html"] = render_to_string(
                "viveca_dashboard/partials/setting_station_search.html",
                {"stations": stations},
            )
            return self.render_to_json_response(context, **kwargs)
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist("station")
        action = request.POST.get("action")
        datas = Stations.objects.filter(id__in=ids)
        if action == "delete":
            for data in datas:
                data.delete()
        if action == "clone":
            for data in datas:
                clone_station(data)
        if action == "save":
            retail_ids = request.POST.getlist("retail_id")
            stream_ids = request.POST.getlist("stream_id")

            # update retail code and stream url fields
            for data in datas:
                data.retailcode = request.POST.get("ret_code_%s" % data.pk)
                data.stream_url = request.POST.get("stream_url_%s" % data.pk)
                data.save()

            # set retail True tags
            datas = Stations.objects.filter(id__in=retail_ids)
            datas.update(retail=True)

            # set retail False tags
            non_retails = Stations.objects.filter(id__in=ids).exclude(id__in=retail_ids)
            non_retails.update(retail=False)

            # set streaming True tags
            datas = Stations.objects.filter(id__in=stream_ids)
            datas.update(streaming=True)

            # set streaming False tags
            non_stream = Stations.objects.filter(id__in=ids).exclude(id__in=stream_ids)
            non_stream.update(streaming=False)

        return redirect("viveca_dashboard_setting_station")

    def get_context_data(self, **kwargs):
        kwargs["station_form"] = SettingStationForm()
        kwargs["stations"] = Stations.objects.all()
        return kwargs


class AddSettingStationView(CreateView, JSONResponseMixin):
    model = Stations
    form_class = SettingStationForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddSettingStationView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        if is_ajax(self.request):
            context = {}
            context["status"] = True
            return self.render_to_json_response(context, **kwargs)
        else:
            object = form.save()
        return redirect("viveca_dashboard_setting_station")

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/station_add_edit_form.html",
            {
                "form": form,
            },
        )
        return self.render_to_json_response(context, **kwargs)


class EditSettingStationPopupView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditSettingStationPopupView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        id = request.POST.get("station")
        station = Stations.objects.get(id=id)
        if station:
            form = SettingStationForm(instance=station)
            context["html"] = render_to_string(
                "viveca_dashboard/partials/station_add_edit_form.html",
                {"form": form, "station": station},
            )
            context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class UpdateSettingStationView(UpdateView, JSONResponseMixin):
    model = Stations
    form_class = SettingStationForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSettingStationView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        if is_ajax(self.request):
            context = {}
            context["status"] = True
            return self.render_to_json_response(context, **kwargs)
        else:
            object = form.save()
        return redirect("viveca_dashboard_setting_station")

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/station_add_edit_form.html",
            {"form": form, "station": self.get_object()},
        )
        return self.render_to_json_response(context, **kwargs)


class SettingLocationView(View):
    template_name = "viveca_dashboard/setting_location.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist("location")
        datas = Locations.objects.filter(id__in=ids)
        datas.delete()
        return redirect("viveca_dashboard_setting_location")

    def get_context_data(self, **kwargs):
        kwargs["location_form"] = DashboardLocationForm()
        kwargs["locations"] = Locations.objects.all()
        return kwargs


class AddSettingLocationView(CreateView, JSONResponseMixin):
    model = Locations
    form_class = DashboardLocationForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddSettingLocationView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/location_add_edit_form.html",
            {
                "form": form,
            },
        )
        return self.render_to_json_response(context, **kwargs)


class EditSettingLocationPopupView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditSettingLocationPopupView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        id = request.POST.get("location")
        location = Locations.objects.get(id=id)
        if location:
            form = DashboardLocationForm(instance=location)
            context["html"] = render_to_string(
                "viveca_dashboard/partials/location_add_edit_form.html",
                {"form": form, "location": location},
            )
            context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class UpdateSettingLocationView(UpdateView, JSONResponseMixin):
    model = Locations
    form_class = DashboardLocationForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSettingLocationView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        obj = form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/location_add_edit_form.html",
            {"form": form, "location": self.get_object()},
        )
        return self.render_to_json_response(context, **kwargs)


class SettingSequenceView(View):
    template_name = "viveca_dashboard/setting_sequence.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        values = request.POST.getlist("sequence")
        delete = request.POST.getlist("delete")
        form = DashboardSequenceForm(request.POST)
        context = self.get_context_data()
        if form.is_valid():
            station = form.get_station()
            context["sequence_station"] = station
            if delete:
                datas = Sequence.objects.filter(id__in=delete)
                datas.delete()
            elif values:
                for value in values:
                    try:
                        data = value.split("_")
                        exists = Sequence.objects.filter(
                            related_station=station, order=data[0]
                        )
                        if exists:
                            exists.update(rating=data[1])
                        else:
                            sequence, created = Sequence.objects.get_or_create(
                                related_station=station, order=data[0], rating=data[1]
                            )
                    except Exception as e:
                        pass
        context["sequence_form"] = form
        # return render(request, self.template_name,context)
        return redirect("viveca_dashboard_setting_sequence")

    def get_context_data(self, **kwargs):
        kwargs["sequences"] = Sequence.objects.all()
        kwargs["sequence_form"] = DashboardSequenceForm()
        return kwargs


class SettingSequenceAjaxView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SettingSequenceAjaxView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        form = DashboardSequenceForm(request.POST)
        if form.is_valid():
            station = form.get_station()
            context["status"] = True
        else:
            station = None
        context["html"] = render_to_string(
            "viveca_dashboard/partials/setting_sequence_rating.html", {"station": station}
        )
        return self.render_to_json_response(context, **kwargs)


class SettingGenresView(View):
    template_name = "viveca_dashboard/setting_genres.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist("genre")
        datas = Genres.objects.filter(id__in=ids)
        datas.delete()
        return redirect("viveca_dashboard_setting_genres")

    def get_context_data(self, **kwargs):
        kwargs["genre_form"] = DashboardGenresForm()
        kwargs["genres"] = Genres.objects.all()
        return kwargs


class AddSettingGenresView(CreateView, JSONResponseMixin):
    model = Genres
    form_class = DashboardGenresForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddSettingGenresView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/genre_add_edit_form.html",
            {"form": form},
        )
        return self.render_to_json_response(context, **kwargs)


class EditSettingGenresPopupView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EditSettingGenresPopupView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        id = request.POST.get("genre")
        genre = Genres.objects.get(id=id)
        if genre:
            form = DashboardGenresForm(instance=genre)
            context["html"] = render_to_string(
                "viveca_dashboard/partials/genre_add_edit_form.html",
                {"form": form, "genre": genre},
            )
            context["status"] = True
        return self.render_to_json_response(context, **kwargs)


class UpdateSettingGenresView(UpdateView, JSONResponseMixin):
    model = Genres
    form_class = DashboardGenresForm

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSettingGenresView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        obj = form.save()
        context = {}
        context["status"] = True
        return self.render_to_json_response(context, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = {}
        context["status"] = False
        context["html"] = render_to_string(
            "viveca_dashboard/partials/genre_add_edit_form.html",
            {"form": form, "genre": self.get_object()},
        )
        return self.render_to_json_response(context, **kwargs)


class PopupSocialPopupView(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PopupSocialPopupView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        context["status"] = False
        station = request.POST.get("station")
        location = request.POST.get("location")
        artist = request.POST.get("artist")
        twitter = self.request.POST.get("twitter")
        instagram = self.request.POST.get("instagram")
        if location == "all":
            social = StationPlaylistSocialCode.objects.filter(
                station__id=station, location__isnull=True, artist=artist
            )
        else:
            social = StationPlaylistSocialCode.objects.filter(
                station__id=station, location__id=location, artist=artist
            )
        if social:
            form = DashboardStationPlaylistSocialCode(instance=social[0])
            context["html"] = render_to_string(
                "viveca_dashboard/partials/playlist_social_form.html",
                {
                    "form": form,
                    "social": social[0],
                    "station": station,
                    "location": location,
                    "artist": artist,
                    "twitter": twitter,
                    "instagram": instagram,
                },
            )
            context["status"] = True
        else:
            form = DashboardStationPlaylistSocialCode()
            context["html"] = render_to_string(
                "viveca_dashboard/partials/playlist_social_form.html",
                {
                    "form": form,
                    "station": station,
                    "location": location,
                    "artist": artist,
                    "twitter": twitter,
                    "instagram": instagram,
                },
            )
            context["status"] = True

        return self.render_to_json_response(context, **kwargs)


class AddSocialPopupView(CreateView, JSONResponseMixin):
    model = StationPlaylistSocialCode
    form_class = DashboardStationPlaylistSocialCode

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddSocialPopupView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        form.save()
        redirect_url = self.request.POST.get("next")
        if redirect_url:
            return redirect(redirect_url)
        return redirect("viveca_dashboard_reports_playlist")


class UpdateSocialPopupView(UpdateView, JSONResponseMixin):
    model = StationPlaylistSocialCode
    form_class = DashboardStationPlaylistSocialCode

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSocialPopupView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, **kwargs):
        obj = form.save()
        redirect_url = self.request.POST.get("next")
        if redirect_url:
            return redirect(redirect_url)
        return redirect("viveca_dashboard_reports_playlist")


class MediaContentData(View):
    def get(self, request, *args, **kwargs):
        url = request.GET.get("url")
        title = request.GET.get("song")
        artist = request.GET.get("artist")
        error = self.get_error_response("401")
        download_name = "viveca_audio"
        if title:
            download_name = title
        if artist:
            download_name += "-" + artist

        if url:
            try:
                response = self.get_response(url, download_name)
            except:
                response = error
        else:
            response = error

        return response

    def get_response(self, url, type):
        try:
            ext = url.split(".")[-1]
            req = urllib.Request(url)

            req.add_header("Content-type", "application/x-www-form-urlencoded")
            content = urllib.urlopen(url).read()
            response = HttpResponse(content=content)
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


class SearchDiscogs(View, JSONResponseMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SearchDiscogs, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        DISCOGS_API_KEY = getattr(settings, "DISCOGS_API_KEY", "")
        DISCOGS_API_SECRET = getattr(settings, "DISCOGS_API_SECRET", "")
        DISCOGS_API_URL = "https://api.discogs.com/database/search"
        context = {}

        artist = request.POST.get("artist")
        title = request.POST.get("title")
        params = {
            "artist": artist,
            "release_title": title,
            "key": DISCOGS_API_KEY,
            "secret": DISCOGS_API_SECRET,
        }
        img_url = None

        try:
            response = requests.get(DISCOGS_API_URL, params=params)
            response.raise_for_status()

            data = response.json()

            if "results" in data and len(data["results"]) > 0:
                img_url = data["results"][0]["cover_image"]
                context["status"] = True
            else:
                img_url = None
                context["status"] = False

        except (requests.exceptions.HTTPError, Exception) as http_err:
            logger.error("Error making the Discogs request:", http_err)
            img_url = None
            context["status"] = False

        context["html"] = render_to_string(
            "viveca_dashboard/partials/discogs_search_result.html",
            {"img_url": img_url},
        )

        return self.render_to_json_response(context, **kwargs)


class GenerateAIStoryView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GenerateAIStoryView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        stories = int(request.POST.get("stories", 5)) + 1
        voice = request.POST.get("voice", "Patrick")
        newsbed = bool(request.POST.get("newsbed", 0))
        separator = bool(request.POST.get("separator", 0))

        news = int(request.POST.get("news", 0))
        entertainment = int(request.POST.get("entertainment", 0))
        sports = int(request.POST.get("sports", 0))
        weather = int(request.POST.get("weather", 0))

        concatenated_audio = AudioSegment.empty()

        prompts = [
            "Get World News" "Get Entertainment News",
            "Get Sports News",
            "Get Health News",
            "What is the weather like in Paris in Farenheit?",
        ]
        news = []

        for i in range(stories):
            news.append(get_news_script(prompts[i]))

        bulletin = generate_bulletin(",".join(news))

        if not separator:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpFile:
                speak_elevenlabs(bulletin, tmpFile.name, voice)
                audio = AudioSegment.from_file(tmpFile.name)
                concatenated_audio += audio

        else:
            beep_sound = AudioSegment.from_mp3("static/audio/beep.mp3")

            for n in news:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpFile:
                    speak_elevenlabs(n, tmpFile.name, voice)
                    audio = AudioSegment.from_file(tmpFile.name)
                    concatenated_audio += beep_sound
                    concatenated_audio += audio

        if newsbed:
            backgroundMusic = AudioSegment.from_mp3("static/audio/newsbed.mp3")
            # Reduce the volume by 30dB
            backgroundMusic = backgroundMusic - 30

            # Loop and extend the background music to match the duration of the concatenated audio
            backgroundMusic = backgroundMusic * (
                len(concatenated_audio) // len(backgroundMusic) + 1
            )
            backgroundMusic = backgroundMusic[: len(concatenated_audio)]

            backgroundMusic = backgroundMusic.fade_out(2000)
            finalAudio = concatenated_audio.overlay(backgroundMusic)
        else:
            finalAudio = concatenated_audio

        audios_directory = os.path.join(settings.MEDIA_ROOT, "audios")
        if not os.path.exists(audios_directory):
            os.makedirs(audios_directory)
        final_audio_path = os.path.join(audios_directory, "generated_audio.wav")
        finalAudio.export(final_audio_path, format="wav")

        with open(final_audio_path, "rb") as audio_file:
            response = HttpResponse(File(audio_file), content_type="audio/wav")

        response["Content-Disposition"] = 'attachment; filename="generated_audio.wav"'
        return response
