from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django_extensions.db.fields import CreationDateTimeField

from airadio.models.settings import Stations, Locations
from airadio.models.users import DJUser
from utils.helpers import create_storage_filename


def get_file_path_for_library_cover(instance, filename):
    return create_storage_filename("library", filename)


class Library(models.Model):
    GENRES = (
        (1, "Pop"),
        (2, "Dance"),
        (3, "Rock"),
        (4, "Ballad"),
        (5, "Urban"),
    )
    ROTATION = (
        (1, "G"),
        (2, "R"),
        (3, "N"),
        (4, "C"),
        (5, "B"),
        (6, "A"),
    )
    artistname = models.CharField(_("Artist"), max_length=255, blank=False, null=False)
    title = models.CharField(_("Title"), max_length=255, blank=False, null=False)
    love_rating = models.IntegerField(_("Love rating"), blank=False, null=False)
    # media = models.FileField(_('Media'), upload_to='media', blank=True)
    media = models.URLField(_("Media URL"))
    cover_art = models.FileField(
        _("Cover art"), upload_to=get_file_path_for_library_cover, blank=True
    )
    release_year = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9999)]
    )
    skip_allowed = models.BooleanField(_("Skip allowed"), default=True)
    mark_clean = models.BooleanField(_("Clean"), default=True)
    duration = models.CharField(_("Duration"), max_length=25)
    genre = models.IntegerField(_("Genre"), choices=GENRES, default=1)
    rotation_category = models.IntegerField(_("Rotation"), choices=ROTATION, default=3)
    twitter_name = models.URLField(_("Twitter"), blank=True)
    facebook_name = models.URLField(_("Facebook"), blank=True, null=True)
    instagram_name = models.URLField(_("Instagram"), blank=True, null=True)
    youtube_name = models.URLField(_("YouTube"), blank=True, null=True)
    in_point = models.CharField(_("Mark In"), max_length=25, blank=False, null=False)
    aux_point = models.CharField(_("Mark Aux"), max_length=25, blank=False, null=False)
    vox_point = models.CharField(_("Mark Vox"), max_length=25, blank=True, null=True)
    relative_link = models.URLField(_("Relative Link"), blank=True)

    def __str__(self):
        return "%s - %s" % (self.artistname, self.title)

    class Meta:
        ordering = ["-id"]
        app_label = "airadio"
        db_table = "library"
        verbose_name = "Library"
        verbose_name_plural = "Library"

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "title__icontains", "artistname__icontains")

    def delete(self, *args, **kwargs):
        self.clear_nullable_related()
        # if not CLOUDSTORAGE is None:
        #     from utils.views import remove_from_cloud
        #     files = [self.media]
        #     if self.cover_art:
        #         files.append( self.cover_art.url )
        #     remove_from_cloud(files)
        super(Library, self).delete(*args, **kwargs)

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


def get_file_path_for_wall_cover(instance, filename):
    return create_storage_filename("wall", filename)


class Wall(models.Model):
    CONTENT_TYPE = (
        (1, "latest"),
        (2, "funny"),
        (3, "entertainment news"),
        (4, "traffic"),
        (5, "interview"),
    )
    TYPE_CHOICE = (
        ("audio", "Audio"),
        ("video", "Video"),
    )
    # content_type = models.BooleanField(_('Content type'), choices=CONTENT_TYPE, default=1)
    related_station = models.ForeignKey(
        Stations, related_name="station_wall_contents", on_delete=models.CASCADE
    )
    cover_art = models.FileField(_("Cover art"), upload_to=get_file_path_for_wall_cover)
    media = models.URLField(_("Media URL"))
    media_type = models.CharField(
        _("Media Type"), choices=TYPE_CHOICE, max_length=200, blank=True, null=True
    )
    title = models.CharField(_("Title"), max_length=25, blank=False, null=False)
    artist = models.CharField(_("Artist"), max_length=25, blank=False, null=False)
    social_media_handle = models.URLField(_("Share link"), null=True, blank=True)
    youtube = models.URLField(_("Youtube URL"), null=True, blank=True)
    in_point = models.CharField(_("Mark In"), max_length=200, blank=False, null=False)
    aux_point = models.CharField(_("Mark Aux"), max_length=200, blank=False, null=False)
    rating = models.IntegerField(_("Rating"), blank=False, null=False)
    relative_link = models.URLField(_("Relative Link"), null=True, blank=True)
    schedule_item = models.BooleanField(_("Schedule item"), default=False)
    skip_allowed = models.BooleanField(_("Skip allowed"), default=True)
    studio_only = models.BooleanField(_("Studio Only"), default=False)
    ui_color_foreground = models.CharField(_("UIColorForeground"), max_length=25)
    ui_color_background = models.CharField(_("UIColorBackground"), max_length=25)

    def __str__(self):
        return str(self.related_station)

    class Meta:
        app_label = "airadio"
        db_table = "wall"
        verbose_name = "Wall"
        verbose_name_plural = "Wall"
        ordering = ["-id"]

    # def delete(self, *args, **kwargs):
    #     if not CLOUDSTORAGE is None:
    #         from utils.views import remove_from_cloud

    #         files = [self.media]
    #         if self.cover_art:
    #             files.append(self.cover_art.url)
    #             remove_from_cloud(files)
    #     super(Wall, self).delete(*args, **kwargs)


class Links(models.Model):
    CONTENT_TYPE = (
        (1, "latest"),
        (2, "funny"),
        (3, "entertainment news"),
        (4, "traffic"),
        (5, "interview"),
    )
    LINK_TYPE = (
        (1, "Content"),
        (2, "Branding"),
    )
    content_type = models.PositiveSmallIntegerField(
        _("Content type"), choices=CONTENT_TYPE, default=1
    )
    link_type = models.PositiveSmallIntegerField(
        _("Link type"), choices=LINK_TYPE, default=1
    )
    related_station = models.ForeignKey(Stations, on_delete=models.CASCADE)
    related_market = models.URLField(_("Related Market"), blank=True)
    relative_link = models.URLField(_("Relative Link"), blank=True)
    in_point = models.IntegerField(_("Mark In"), blank=False, null=False)
    aux_point = models.IntegerField(_("Mark Aux"), blank=False, null=False)

    def __str__(self):
        return str(self.related_station)

    class Meta:
        app_label = "airadio"
        db_table = "links"
        verbose_name = "Links"
        verbose_name_plural = "Links"


def get_file_path(instance, filename):
    return create_storage_filename(instance.type, filename)


class MediaUpload(models.Model):
    media = models.FileField(_("Media"), upload_to=get_file_path)
    type = models.CharField(_("Service Type"), max_length=255)
    name_id_val = models.PositiveIntegerField(_("Filename Value"))

    def __str__(self):
        return str(self.pk)

    class Meta:
        app_label = "airadio"
        verbose_name = "Media Upload"
        verbose_name_plural = "Media Uploads"


class GlobalPlaylist(models.Model):
    TYPES = (
        (1, "News"),
        (2, "Weather"),
        (4, "Entertainment"),
        (5, "Sports"),
    )
    type = models.IntegerField(_("Type"), choices=TYPES, default=1)
    title = models.CharField(_("Title"), max_length=255)
    media = models.URLField(_("Media URL"))
    updated = models.DateTimeField(_("Updated"), auto_now_add=True)

    def __str__(self):
        return self.title + " (" + str(self.get_type_display()) + ")"

    class Meta:
        app_label = "airadio"
        verbose_name = "Global Playlist"
        verbose_name_plural = "Global Playlists"
        ordering = ["-id"]


class StationLibrary(models.Model):
    station = models.ForeignKey(
        Stations, related_name="station_library", on_delete=models.CASCADE
    )
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    points = models.IntegerField(_("Points"), blank=True, null=True)

    def __str__(self):
        return str(self.station)

    class Meta:
        app_label = "airadio"
        ordering = ["-library__id"]
        verbose_name = "Station Library"
        verbose_name_plural = "Station Libraries"


class StationPlaylist(models.Model):
    station = models.ForeignKey(
        Stations, related_name="station_playlist", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Locations,
        related_name="location_playlist",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey("content_type", "object_id")
    updated = models.DateTimeField(_("Updated"), auto_now_add=True)
    skipped = models.BooleanField(_("Skip ?"), default=False)
    position = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.station)

    class Meta:
        app_label = "airadio"
        verbose_name = "Station Playlist"
        verbose_name_plural = "Station Playlists"
        ordering = ["position"]


def get_file_path_for_dj_media(instance, filename):
    return create_storage_filename("mmistudio", filename)


def get_file_path_for_djtrack_cover(instance, filename):
    return create_storage_filename("djtrack", filename)


class DJTracks(models.Model):
    dj = models.ForeignKey(
        DJUser, related_name="dj_user_tracks", on_delete=models.CASCADE
    )
    cover_art = models.FileField(
        _("Cover art"), upload_to=get_file_path_for_djtrack_cover, blank=True, null=True
    )
    title = models.CharField(_("Title"), max_length=255)
    tags = models.CharField(_("Tags"), max_length=255)
    media = models.FileField(_("Media"), upload_to=get_file_path_for_dj_media)
    recorded = models.CharField(_("Recorded"), max_length=200, blank=True, editable=False)
    in_point = models.CharField(_("Mark In"), max_length=200)
    aux_point = models.CharField(_("Mark Aux"), max_length=200)
    published = models.BooleanField(_("Publish ?"), default=True)
    created = CreationDateTimeField(_("Created at"))

    def __str__(self):
        return str(self.dj)

    class Meta:
        app_label = "airadio"
        verbose_name = "DJTracks"
        verbose_name_plural = "DJTracks"

    def get_tags(self):
        return self.tags.split(",")

    # def delete(self, *args, **kwargs):
    #     if not CLOUDSTORAGE is None:
    #         from utils.views import remove_from_cloud

    #         files = [self.media.url]
    #         if self.cover_art:
    #             files.append(self.cover_art.url)
    #             remove_from_cloud(files)
    #     super(DJTracks, self).delete(*args, **kwargs)


class ExportPlaylist(models.Model):
    HOURS = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "10"),
        (11, "11"),
        (12, "12"),
        (13, "13"),
        (14, "14"),
        (15, "15"),
        (16, "16"),
        (17, "17"),
        (18, "18"),
        (19, "19"),
        (20, "20"),
        (21, "21"),
        (22, "22"),
        (23, "23"),
        (24, "24"),
    )
    station = models.ForeignKey(
        Stations, related_name="export_station", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Locations,
        related_name="export_location",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    hour = models.PositiveIntegerField(choices=HOURS)

    def __str__(self):
        return str(self.hour)

    class Meta:
        ordering = [
            "hour",
        ]
        app_label = "airadio"
        verbose_name = "ExportPlaylist"
        verbose_name_plural = "ExportPlaylists"


class ExportPlaylistItem(models.Model):
    export = models.ForeignKey(
        ExportPlaylist, related_name="exports", on_delete=models.CASCADE
    )
    item = models.TextField()

    def __str__(self):
        return str(self.export)

    @property
    def get_item(self):
        import ast

        return ast.literal_eval(self.item)

    @property
    def get_item_position(self):
        import ast

        return ast.literal_eval(self.item)["-position"]

    @property
    def get_item_type(self):
        import ast

        return ast.literal_eval(self.item)["-type"]

    @property
    def get_item_media(self):
        import ast

        return ast.literal_eval(self.item)["media"]["-url"]

    class Meta:
        ordering = [
            "id",
        ]
        app_label = "airadio"
        verbose_name = "ExportPlaylistItem"
        verbose_name_plural = "ExportPlaylistItems"
