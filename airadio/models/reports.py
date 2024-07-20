from django.db import models
from django.utils.translation import gettext_lazy as _

from airadio.models.settings import Stations


class Reports(models.Model):
    ITEM_TYPE = (
        (1, "music"),
        (2, "video"),
        (3, "banner"),
        (4, "social"),
        (5, "advert"),
    )
    CONTENT_TYPE = (
        (1, "latest"),
        (2, "funny"),
        (3, "entertainment news"),
        (4, "traffic"),
        (5, "interview"),
    )
    AGE_GROUP = (
        (1, "Teens"),
        (2, "P18-34"),
        (3, "P25-34"),
        (4, "P34-45"),
        (5, "P45+"),
    )
    content_type = models.PositiveSmallIntegerField(
        _("Content type"), choices=CONTENT_TYPE, default=1
    )
    related_station = models.ForeignKey(Stations, on_delete=models.CASCADE)
    title = models.CharField(_("Title"), max_length=15, blank=False, null=False)
    artist = models.TextField(_("Artist"), max_length=15, blank=True, null=True)
    points = models.IntegerField(default=0)
    played = models.IntegerField(default=0)
    skipped = models.BooleanField(_("Skipped"), blank=True, null=True)
    age_group = models.PositiveSmallIntegerField(
        _("Age Group"), choices=AGE_GROUP, blank=False, null=False
    )
    love_rating = models.IntegerField(default=0)

    def __str__(self):
        return str(self.reports)

    class Meta:
        app_label = "airadio"
        db_table = "reports"
        verbose_name = "Reports"
        verbose_name_plural = "Reports"


class DJTag(models.Model):
    name = models.CharField("Tags", max_length=255)

    def __str__(self):
        return str(self.name)

    class Meta:
        app_label = "airadio"
        db_table = "djtag"
        verbose_name = "DJTag"
        verbose_name_plural = "DJTags"
