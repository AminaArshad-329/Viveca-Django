from django.db import models
from django.utils.translation import gettext_lazy as _

from airadio.models.users import Users


class ServerStats(models.Model):
    unique_id = models.CharField(_("UniqueID"), max_length=15)
    serverConcurrentUsers = models.ForeignKey(Users, on_delete=models.CASCADE)
    serverDataBaseLoad = models.TextField()

    def __str__(self):
        return str(self.unique_id)

    class Meta:
        app_label = "airadio"
        db_table = "serverstats"
        verbose_name = "Serverstats"
        verbose_name_plural = "Serverstats"


class TopSongs:
    """fetch from analytics"""

    def __str__(self):
        return str(self.topsongs)

    class Meta:
        db_table = "topsongs"
        verbose_name = "Topsongs"
        verbose_name_plural = "Topsongs"


class Platforms(models.Model):
    PLATFORM_USED = (
        (1, "iOS"),
        (2, "Android"),
        (3, "Web"),
    )
    platform_used = models.PositiveSmallIntegerField(
        _("Platform"), choices=PLATFORM_USED, blank=False, null=False
    )

    def __str__(self):
        return str(self.platform_used)

    class Meta:
        app_label = "airadio"
        db_table = "platforms"
        verbose_name = "Platforms"
        verbose_name_plural = "Platforms"


class Research(models.Model):
    AGE_GROUP = (
        (1, "Teens"),
        (2, "P18-34"),
        (3, "P25-34"),
        (4, "P34-45"),
        (5, "P45+"),
    )

    username = models.ForeignKey(Users, on_delete=models.CASCADE)
    location_country = models.CharField(
        _("Country"), max_length=255, blank=True, null=True
    )
    location_state = models.CharField(_("State"), max_length=255, blank=True, null=True)
    location_city = models.CharField(_("City"), max_length=255, blank=True, null=True)
    station_name = models.CharField(_("Station"), max_length=255, blank=True, null=True)
    total_users = models.IntegerField(default=0)
    average_per_head = models.IntegerField(default=0)
    average_hour_per_user = models.IntegerField(default=0)
    total_hours = models.IntegerField(default=0)
    age_group = models.PositiveSmallIntegerField(
        _("Age Group"), choices=AGE_GROUP, blank=True, null=True
    )
    gender = models.CharField(_("Gender"), max_length=255)
    love_rating = models.IntegerField(default=0)

    def __str__(self):
        return str(self.username)

    class Meta:
        app_label = "airadio"
        db_table = "research"
        verbose_name = "Research"
        verbose_name_plural = "Research"
