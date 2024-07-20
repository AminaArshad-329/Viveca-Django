from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from airadio.models import DJTracks

class Command(BaseCommand):
    def handle(self, *args, **options):
        hr_24_before = timezone.now() - timedelta(days=1)
        try:
            DJTracks.objects.filter(created__lt = hr_24_before).delete()
        except Exception as e:
            print e
