from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.helpers import create_storage_filename


def get_file_path(instance, filename):
    return create_storage_filename("station", filename)


class Locations(models.Model):
    location_country = models.CharField(_("Country"), max_length=255)
    location_state = models.CharField(_("State"), max_length=255)
    location_city = models.CharField(_("City"), max_length=255)
    location_lat = models.DecimalField(_("Latitude"), max_digits=11, decimal_places=8)
    location_long = models.DecimalField(_("Longitude"), max_digits=11, decimal_places=8)

    # location_status = models.CharField(_('Status'), max_length=255)

    def __str__(self):
        return str(self.location_city)

    class Meta:
        app_label = "airadio"
        db_table = "locations"
        verbose_name = "Locations"
        verbose_name_plural = "Locations"


class Stations(models.Model):
    station_name = models.CharField(
        _("Station name"), max_length=255, blank=False, null=False
    )
    station_logo = models.FileField(
        _("Station logo"), upload_to=get_file_path, blank=True
    )
    station_preview = models.FileField(
        _("Station preview"), upload_to=get_file_path, blank=True
    )
    station_description = models.TextField(
        _("Station description"), max_length=200, blank=True, null=True
    )
    system_prompt = models.TextField(blank=True, null=True)
    order_id = models.IntegerField(_("Order"))
    location = models.ManyToManyField(Locations, blank=True)
    retail = models.BooleanField(_("Is Retail ?"), default=False)
    retailcode = models.CharField(
        _("Station Retail Code"), max_length=255, blank=True, null=True
    )
    streaming = models.BooleanField(_("Is Streaming ?"), default=False)
    stream_url = models.CharField(
        _("Station Stream URL"), max_length=255, blank=True, null=True
    )
    microsite = models.CharField(
        _("Microsite URL"), max_length=255, blank=True, null=True
    )
    published = models.BooleanField(_("Is Published ?"), default=True)

    def __str__(self):
        return self.station_name

    def has_playlist(self):
        return not self.station_playlist.all() == []

    @property
    def station_locations(self):
        return ", ".join([location.location_city for location in self.location.all()])

    class Meta:
        app_label = "airadio"
        db_table = "stations"
        ordering = [
            "order_id",
        ]
        verbose_name = "Stations"
        verbose_name_plural = "Stations"

    @classmethod
    def get_stations_with_playlist(self):
        from . import StationPlaylist

        stn_ids = StationPlaylist.objects.values_list("station__id", flat=True)
        return self.objects.filter(id__in=stn_ids)

    def delete(self, *args, **kwargs):
        try:
            self.clear_nullable_related()
        except:
            pass
        super(Stations, self).delete(*args, **kwargs)

    def clear_nullable_related(self):
        """
        Recursively clears any nullable foreign key fields on related objects.
        Django is hard-wired for cascading deletes, which is very dangerous for
        us. This simulates ON DELETE SET NULL behavior manually.
        """
        try:
            if self._meta and self._meta.get_fields():
                for field in self._meta.get_fields():
                    if (field.one_to_many or field.one_to_one) and field.auto_created:
                        accessor = field.get_accessor_name()
                        related_set = getattr(self, accessor)

                        if field.null:
                            related_set.clear()
                        else:
                            for related_object in related_set.all():
                                related_object.clear_nullable_related()
        except AttributeError:
            pass


class Genres(models.Model):
    name = models.CharField(_("Name"), max_length=255, blank=False, null=False)
    updated = models.DateTimeField(_("Updated"), auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "airadio"
        db_table = "genres"
        verbose_name = "Genre"
        verbose_name_plural = "Genres"


class PositionPrompts(models.Model):
    station = models.ForeignKey(Stations, on_delete=models.CASCADE)
    position = models.CharField(max_length=255, blank=False, null=False)
    prompt = models.TextField(blank=True, null=True)

    def __str__(self):
        str = ""
        if self.station:
            str = self.station.station_name + " - "
        return str + self.position

    class Meta:
        app_label = "airadio"
        ordering = ["station", "position"]
        db_table = "position_prompts"
        verbose_name = "Position Prompt"
        verbose_name_plural = "Position Prompts"


class TopicPrompts(models.Model):
    COLOR_GROUP = (
        (1, "Green"),
        (2, "Blue"),
        (3, "Red"),
        (4, "Yellow"),
    )
    station = models.ForeignKey(Stations, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255, blank=False, null=False)
    prompt = models.TextField(blank=True, null=True)
    color_group = models.PositiveSmallIntegerField(
        choices=COLOR_GROUP, blank=False, null=False
    )

    def __str__(self):
        str = ""
        if self.station:
            str = self.station.station_name + " - "
        return str + self.topic

    def get_color_group(self):
        if self.color_group == 1:
            return "teal"
        elif self.color_group == 2:
            return "sky"
        elif self.color_group == 3:
            return "red"
        elif self.color_group == 4:
            return "yellow"

    class Meta:
        app_label = "airadio"
        db_table = "topic_prompts"
        verbose_name = "Topic Prompt"
        verbose_name_plural = "Topic Prompts"


def get_file_path_banner(instance, filename):
    return create_storage_filename("stationbanner", filename)


class StationBanner(models.Model):
    station = models.ForeignKey(
        Stations, related_name="station_banners", on_delete=models.CASCADE
    )
    banner = models.FileField(
        _("Banner Image"), upload_to=get_file_path_banner, blank=True
    )
    type = models.CharField(_("Type"), max_length=255)

    def __str__(self):
        return self.station

    class Meta:
        app_label = "airadio"
        db_table = "stationbanner"
        verbose_name = "Station Banner"
        verbose_name_plural = "Station Banners"

    # def delete(self, *args, **kwargs):
    #     if not CLOUDSTORAGE is None:
    #         from utils.views import remove_from_cloud

    #         files = []
    #         if self.banner:
    #             files.append(self.banner.url)
    #             remove_from_cloud(files)
    #     super(StationBanner, self).delete(*args, **kwargs)


class MarketStations(models.Model):
    name = models.CharField(_("Market Name"), max_length=255, blank=False, null=False)
    key = models.CharField(
        _("Market Name Key"),
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        help_text="Avoid blank spaces if more than one word, instead use underscores.",
    )
    stations = models.ManyToManyField(Stations, related_name="station_markets")

    def __str__(self):
        return self.name

    class Meta:
        app_label = "airadio"
        db_table = "marketstations"
        verbose_name = "Market Station"
        verbose_name_plural = "Market Stations"


class StationPlaylistSocialCode(models.Model):
    TYPE_CHOICES = (
        ("instagram", "Instagram"),
        ("twitter", "Twitter"),
    )

    station = models.ForeignKey(Stations, on_delete=models.CASCADE)
    location = models.ForeignKey(
        Locations, null=True, blank=True, on_delete=models.SET_NULL
    )
    artist = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    twitter_code = models.TextField(null=True, blank=True)
    instagram_code = models.TextField(null=True, blank=True)
    img_link = models.CharField(max_length=255, null=True, blank=True)
    post_link = models.CharField(max_length=255, blank=True)
    post_text = models.TextField(blank=True)
    user_image_link = models.CharField(max_length=255, blank=True)
    related_link_twitter = models.CharField(max_length=255, blank=True)
    related_link_instagram = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default="instagram")

    def __str__(self):
        return self.artist

    class Meta:
        app_label = "airadio"
        verbose_name = "Station Playlist SocialCode"
        verbose_name_plural = "Station Playlist SocialCodes"
