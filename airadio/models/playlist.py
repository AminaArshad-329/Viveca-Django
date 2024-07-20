from django.db import models
from django.utils.translation import gettext_lazy as _

from airadio.models.settings import Stations, Locations
from utils.helpers import create_storage_filename


def get_file_path_for_advert(instance, filename):
    return create_storage_filename("adverts", filename)


class Sequence(models.Model):
    related_station = models.ForeignKey(
        Stations, related_name="station_sequences", on_delete=models.CASCADE
    )
    rating = models.IntegerField(_("Rating"))
    order = models.IntegerField(_("Order"))

    def __str__(self):
        return str(self.related_station)

    class Meta:
        app_label = "airadio"
        ordering = ["order"]
        db_table = "sequence"
        verbose_name = "Sequence"
        verbose_name_plural = "Sequence"


class Scheduling(models.Model):
    related_station = models.OneToOneField(
        Stations,
        verbose_name=_("Station"),
        related_name="station_schedules",
        on_delete=models.CASCADE,
    )
    branding = models.PositiveIntegerField(_("Insert Branding Every"), default=0)
    advert = models.PositiveIntegerField(_("Insert Advert Every"), default=0)
    link = models.PositiveIntegerField(_("Insert Link Every"), default=0)
    wall = models.PositiveIntegerField(_("Insert Wall Every"), default=0)
    rate_5 = models.PositiveIntegerField(_("Music Rotation Rating-5"), default=0)
    rate_4 = models.PositiveIntegerField(_("Music Rotation Rating-4"), default=0)
    rate_3 = models.PositiveIntegerField(_("Music Rotation Rating-3"), default=0)
    rate_2 = models.PositiveIntegerField(_("Music Rotation Rating-2"), default=0)
    rate_1 = models.PositiveIntegerField(_("Music Rotation Rating-1"), default=0)
    seperate_genres = models.BooleanField(_("Seperate same genres ?"), default=False)
    seperate_genres_songs = models.IntegerField(
        _("Seperate same genres songs"), null=True, blank=True
    )

    def __str__(self):
        return str(self.related_station)

    class Meta:
        app_label = "airadio"
        db_table = "scheduling"
        verbose_name = "Scheduling"
        verbose_name_plural = "Scheduling"


class BrandingTOH(models.Model):
    station = models.ForeignKey(
        Stations, related_name="station_branding_toh", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Locations,
        related_name="location_branding_toh",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    media = models.URLField(_("Media URL"))
    title = models.CharField(_("Title"), max_length=255)
    points = models.IntegerField(_("Points"))
    skip_allowed = models.BooleanField(_("Skip allowed"), default=True)
    relative_link = models.URLField(_("Relative Link"), blank=True)
    duration = models.CharField(_("Duration"), max_length=25)
    in_point = models.CharField(_("Mark In"), max_length=25)
    aux_point = models.CharField(_("Mark Aux"), max_length=25)

    def __str__(self):
        return self.title

    class Meta:
        app_label = "airadio"
        db_table = "brandingtoh"
        verbose_name = "BrandingTOH/IDS"
        verbose_name_plural = "BrandingTOH/IDS"


class Adverts(models.Model):
    ADVERT_TYPES = (
        ("audio", "Audio"),
        ("video", "Video"),
    )
    AGE_GROUPS = (
        (1, "Teens"),
        (2, "P18-34"),
        (3, "P25-34"),
        (4, "P34-45"),
        (5, "P45+"),
    )
    title = models.CharField(_("Title"), max_length=255)
    type = models.CharField(
        _("Type"), max_length=255, choices=ADVERT_TYPES, null=True, blank=True
    )
    media = models.URLField(_("Media URL"))
    cover_art = models.FileField(
        _("Cover Image"), upload_to=get_file_path_for_advert, blank=True
    )
    banner_text = models.CharField(
        _("Banner Body Text"), max_length=255, null=True, blank=True
    )
    age_group = models.PositiveSmallIntegerField(
        _("Age group"), choices=AGE_GROUPS, blank=False, null=False
    )
    location = models.ForeignKey(
        Locations,
        related_name="location_adverts",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    radius = models.IntegerField(_("Radius"))
    duration = models.CharField(_("Duration"), max_length=25)
    aux_point = models.CharField(_("Pos Chain"), max_length=255)
    points = models.IntegerField(_("Points"))
    microsite = models.URLField(_("Microsite URL"), null=True, blank=True)
    skip_allowed = models.BooleanField(_("Skip allowed"), default=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ["-id"]
        app_label = "airadio"
        db_table = "adverts"
        verbose_name = "Advert"
        verbose_name_plural = "Adverts"

    # def delete(self, *args, **kwargs):
    #     if not CLOUDSTORAGE is None:
    #         from utils.views import remove_from_cloud

    #         files = [self.media]
    #         if self.cover_art:
    #             files.append(self.cover_art.url)
    #             remove_from_cloud(files)
    #     super(Adverts, self).delete(*args, **kwargs)
