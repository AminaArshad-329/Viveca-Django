from django.utils import timezone
from django.core.management.base import BaseCommand
from parse_rest.connection import register as parse_register
from parse_rest.datatypes import Object
from django.utils import timezone
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(timezone.now())
        parse_register(
            settings.APPLICATION_ID, settings.REST_API_KEY, master_key=settings.MASTER_KEY
        )
        myClassName = "TestClass"
        myClass = Object.factory(myClassName)
        gameScore = myClass(score=1337, player_name="John Doe", cheat_mode=False)
        gameScore.save()
        print(timezone.now())
