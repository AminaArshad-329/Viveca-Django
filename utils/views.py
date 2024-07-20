import json
import urllib
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.template import loader
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.template import Context

from airadio.models import (
    Stations,
    Sequence,
    Scheduling,
    BrandingTOH,
    StationLibrary,
    StationPlaylist,
    Wall,
    TSUPerStation,
    StationBanner,
    DJMusicBed,
)
from django.core.files.storage import default_storage


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(
            self.convert_context_to_json(context),
            content_type="application/json",
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)


def send_accout_activation_mail(user):
    if user.email and user.groups.filter(name__in=["DJ"]):
        t = loader.get_template("dashboard/common/dj_activation_mail.html")
        c = Context({"user": user})
        rendered = t.render(c)
        text_content = strip_tags(rendered)
        current_site = Site.objects.get_current()
        send_mail(
            "[%s] %s" % (current_site.name, "Account Activated"),
            text_content,
            settings.ADMIN_EMAIL,
            [user.email],
            fail_silently=False,
        )


def send_email_verification_mail(djuser):
    if djuser.user.email and djuser.confirmation_code:
        current_site = Site.objects.get_current()
        t = loader.get_template("registration/confirm_email.html")
        link = "http://%s%s" % (
            current_site.domain,
            reverse("user-verify-email", kwargs={"key": djuser.confirmation_code}),
        )
        c = Context({"user": djuser.user, "link": link})
        rendered = t.render(c)
        text_content = strip_tags(rendered)
        send_mail(
            "[%s] %s" % (current_site.name, "Confirm Email"),
            text_content,
            settings.ADMIN_EMAIL,
            [djuser.user.email],
            fail_silently=False,
        )


def get_image_file_url(url, id):
    try:
        content = urllib.urlopen(url).read()
        mediaURL = settings.MEDIA_ROOT + "/coverart" + str(id) + ".png"
        localFile = open(mediaURL, "w")
        localFile.write(content)
        localFile.close()
        return mediaURL
    except:
        return None


def remove_from_cloud(url_list):
    name_list = [url.split("/")[-1] for url in url_list]
    for name in name_list:
        if default_storage.exists(name):
            default_storage.delete(name)


def get_new_kwargs(old):
    new_kwargs = dict(
        [
            (fld.name, getattr(old, fld.name))
            for fld in old._meta.fields
            if fld.name != "id"
        ]
    )
    return new_kwargs


def clone_station(station):
    new_kwargs = get_new_kwargs(station)
    clone = Stations.objects.create(**new_kwargs)
    station_libraries = station.station_library.all()
    for lib in station_libraries:
        new_kwargs = get_new_kwargs(lib)
        library = StationLibrary.objects.create(**new_kwargs)
        library.station = clone
        library.save()

    try:
        station_playlist = station.station_playlist.all()
        for play in station_playlist:
            new_kwargs = get_new_kwargs(play)
            playlist = StationPlaylist.objects.create(**new_kwargs)
            playlist.station = clone
            playlist.save()
    except:
        pass

    try:
        station_sequences = station.station_sequences.all()
        for sequence in station_sequences:
            new_kwargs = get_new_kwargs(sequence)
            sequences = Sequence.objects.create(**new_kwargs)
            sequences.related_station = clone
            sequences.save()
    except:
        pass

    try:
        station_schedules = station.station_schedules
        new_kwargs = get_new_kwargs(station_schedules)
        new_kwargs["related_station"] = clone
        schedules = Scheduling.objects.create(**new_kwargs)
    except:
        pass

    try:
        station_branding_toh = station.station_branding_toh.all()
        for toh in station_branding_toh:
            new_kwargs = get_new_kwargs(toh)
            branding_toh = BrandingTOH.objects.create(**new_kwargs)
            branding_toh.station = clone
            branding_toh.save()
    except:
        pass

    try:
        station_tsu = station.station_tsu.all()
        for tsu in station_tsu:
            new_kwargs = get_new_kwargs(tsu)
            analytics = TSUPerStation.objects.create(**new_kwargs)
            analytics.station = clone
            analytics.save()
    except:
        pass

    try:
        station_wall_contents = station.station_wall_contents.all()
        for wall in station_wall_contents:
            new_kwargs = get_new_kwargs(wall)
            wall_content = Wall.objects.create(**new_kwargs)
            wall_content.related_station = clone
            wall_content.save()
    except:
        pass

    try:
        station_banners = station.station_banners.all()
        for banner in station_banners:
            new_kwargs = get_new_kwargs(banner)
            banner_content = StationBanner.objects.create(**new_kwargs)
            banner_content.station = clone
            banner_content.save()
    except:
        pass

    try:
        station_dj_musicbeds = station.station_dj_musicbeds.all()
        for musicbed in station_dj_musicbeds:
            new_kwargs = get_new_kwargs(musicbed)
            musicbed_content = DJMusicBed.objects.create(**new_kwargs)
            musicbed_content.station = clone
            musicbed_content.save()
    except:
        pass
