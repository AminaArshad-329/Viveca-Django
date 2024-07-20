from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal as D

from airadio.models.settings import Stations
from airadio.models.library import Library


class Analytics(models.Model):
    date = models.DateField(_("Date"))
    unique_users = models.PositiveIntegerField(_("Unique Users"))
    current_users = models.PositiveIntegerField(_("Current Users"))
    s3_data_usage = models.IntegerField(
        _("Cloud Files"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    db_load = models.IntegerField(
        _("Database Load"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    male = models.IntegerField(
        _("Male"), validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )
    female = models.IntegerField(
        _("Female"), validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )
    iphone = models.IntegerField(
        _("iPhone"), validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )
    android = models.IntegerField(
        _("Android"), validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )
    web_palyer = models.IntegerField(
        _("WebPlayer"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )

    def __str__(self):
        return str(self.date)

    class Meta:
        app_label = "airadio"
        db_table = "analytics"
        verbose_name = "Analytics"
        verbose_name_plural = "Analytics"


class TSUPerStation(models.Model):
    analytics = models.ForeignKey(
        Analytics, related_name="analytics_tsu", on_delete=models.CASCADE
    )
    station = models.ForeignKey(
        Stations, related_name="station_tsu", on_delete=models.CASCADE
    )
    total_users = models.PositiveIntegerField(_("Total Users"), default=0)
    avg_per_head = models.DecimalField(
        _("Average Per Head"), max_digits=10, decimal_places=2, default=D("0.00")
    )
    avg_hour_per_user = models.DecimalField(
        _("Average Hour Per User"), max_digits=10, decimal_places=2, default=D("0.00")
    )
    total_hours = models.PositiveIntegerField(_("Total Hours"), default=0)

    def __str__(self):
        return str(self.analytics)

    class Meta:
        app_label = "airadio"
        db_table = "tsuperstation"
        verbose_name = "TSU Per Station"
        verbose_name_plural = "TSU Per Station"


class Dashboard(models.Model):
    date = models.DateField(_("Date"))

    def __str__(self):
        return str(self.date)

    class Meta:
        app_label = "airadio"
        db_table = "dashboard"
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboard"


class MusicResearchLibrary(models.Model):
    dashboard = models.ForeignKey(
        Dashboard, related_name="dashboard_musicresearch", on_delete=models.CASCADE
    )
    library = models.ForeignKey(
        Library, related_name="dashboard_music_library", on_delete=models.CASCADE
    )

    def __str__(self):
        return "%s %s" % (self.dashboard.date, self.library.title)

    class Meta:
        app_label = "airadio"
        db_table = "musicresearchlibrary"
        verbose_name = "Music Research Library"
        verbose_name_plural = "Music Research Library"


class MusicResearchData(models.Model):
    research = models.ForeignKey(
        MusicResearchLibrary,
        related_name="dashboard_musicresearch_data",
        on_delete=models.CASCADE,
    )
    value = models.PositiveIntegerField(_("Value"), default=0)

    def __str__(self):
        return str(self.value)

    class Meta:
        app_label = "airadio"
        db_table = "musicresearchdata"
        verbose_name = "Music Research Data"
        verbose_name_plural = "Music Research Data"


class RealTimeSkipLibrary(models.Model):
    dashboard = models.ForeignKey(
        Dashboard, related_name="dashboard_realtime_skips", on_delete=models.CASCADE
    )
    library = models.ForeignKey(
        Library, related_name="dashboard_realtime_skips_library", on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.dashboard)

    class Meta:
        app_label = "airadio"
        db_table = "realtimeskiplibrary"
        verbose_name = "RealTime Skip Library"
        verbose_name_plural = "RealTime Skip Library"


class RealTimeSkipData(models.Model):
    realtime = models.ForeignKey(
        RealTimeSkipLibrary, related_name="realtime_data", on_delete=models.CASCADE
    )
    value = models.PositiveIntegerField(_("Value"), default=0)

    def __str__(self):
        return str(self.value)

    class Meta:
        app_label = "airadio"
        db_table = "realtimeskipdata"
        verbose_name = "RealTime Skip Data"
        verbose_name_plural = "RealTime Skip Data"


class DashboardTopSongs(models.Model):
    dashboard = models.ForeignKey(
        Dashboard, related_name="dashboard_topsongs", on_delete=models.CASCADE
    )
    library = models.ForeignKey(
        Library, related_name="dashboard_topsongs_library", on_delete=models.CASCADE
    )
    instagram = models.CharField(
        _("Instagram Account"), null=True, blank=True, max_length=200
    )
    rating = models.DecimalField(
        _("Rating"), max_digits=10, decimal_places=2, default=D("0.00")
    )

    def __str__(self):
        return str(self.dashboard)

    class Meta:
        app_label = "airadio"
        ordering = ["-rating"]
        db_table = "dashboardtopsongs"
        verbose_name = "Dashboard Top Song"
        verbose_name_plural = "Dashboard Top Songs"


class Installation(models.Model):
    device_token = models.TextField()

    def __str__(self):
        return str(self.pk)

    class Meta:
        app_label = "airadio"
        db_table = "installation"
        verbose_name = "Installation"
        verbose_name_plural = "Installations"
