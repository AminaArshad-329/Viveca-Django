from django.db import models

from airadio.models.settings import Stations


class WidgetUserStatistics(models.Model):
    station = models.ForeignKey(Stations, on_delete=models.CASCADE)
    user_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.location_city)

    class Meta:
        app_label = "airadio"
        db_table = "widgetuserstatistics"
        verbose_name = "Widget User Statistics"
        verbose_name_plural = "Widget User Statistics"
