import base64
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from airadio.models.settings import Stations
from utils.helpers import create_storage_filename


def get_file_path_for_dj_user_photo(instance, filename):
    return create_storage_filename("djuser", filename)


class Users(models.Model):
    ACCESS_LEVEL = (
        (1, "admin"),
        (2, "station"),
        (3, "editor"),
        (4, "studio"),
        (5, "user"),
    )
    AGE_GROUP = (
        (1, "Teens"),
        (2, "P18-34"),
        (3, "P25-34"),
        (4, "P34-45"),
        (5, "P45+"),
    )
    ANDROID_INSTALLED = (
        (1, "Yes"),
        (2, "No"),
    )
    IOS_INSTALLED = (
        (1, "Yes"),
        (2, "No"),
    )
    username = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    date_of_birth = models.DateField(_("Date of birth"), blank=True, null=True)
    user_location = models.CharField(
        _("Location"), max_length=25, blank=False, null=False
    )
    email = models.URLField(_("Email"), blank=True)
    firstname = models.CharField(_("First name"), max_length=25, blank=False, null=False)
    lastname = models.CharField(_("Last name"), max_length=25, blank=False, null=False)
    access_level = models.PositiveSmallIntegerField(
        _("Access level"), choices=ACCESS_LEVEL, blank=False, null=False
    )
    age_group = models.PositiveSmallIntegerField(
        _("Age group"), choices=AGE_GROUP, blank=False, null=False
    )
    android_installed = models.PositiveSmallIntegerField(
        _("Android installed"), choices=ANDROID_INSTALLED, blank=False, null=False
    )
    ios_installed = models.PositiveSmallIntegerField(
        _("iOS installed"), choices=IOS_INSTALLED, blank=False, null=False
    )

    def __str__(self):
        return str(self.username)

    class Meta:
        app_label = "airadio"
        db_table = "users"
        verbose_name = "Users"
        verbose_name_plural = "Users"


class Playlist(models.Model):
    CONTENT_TYPE = (
        (1, "latest"),
        (2, "funny"),
        (3, "entertainment news"),
        (4, "traffic"),
        (5, "interview"),
    )

    content_type = models.PositiveSmallIntegerField(
        _("Content type"), choices=CONTENT_TYPE, blank=False, null=False
    )
    master_station_checksum = models.CharField(
        _("Check Sum"), max_length=25, blank=False, null=False
    )
    personalized_station = models.ForeignKey(Stations, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.personalized_station)

    class Meta:
        app_label = "airadio"
        db_table = "playlist"
        verbose_name = "Playlist"
        verbose_name_plural = "Playlist"


class DJUser(models.Model):
    EXPIRY_CHOICES = ((True, "Active"), (False, "Expired"))
    user = models.OneToOneField(User, related_name="dj_user", on_delete=models.CASCADE)
    photo = models.FileField(upload_to=get_file_path_for_dj_user_photo)
    confirmation_code = models.CharField(max_length=255, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    station = models.ForeignKey(
        Stations,
        related_name="station_dj_user",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    token = models.CharField(
        _("API Token"), max_length=100, blank=True, null=True, editable=False
    )
    token_stat = models.BooleanField(
        choices=EXPIRY_CHOICES,
        verbose_name=_("API Token Status"),
        default=False,
        editable=False,
    )
    expiry_date = models.DateTimeField(
        _("API Token Expiry Date"), null=True, blank=True, editable=False
    )

    def __str__(self):
        return str(self.user.username)

    @property
    def get_follower_count(self):
        return self.user.user_activity_to_user.all().count()

    class Meta:
        app_label = "airadio"
        db_table = "djuser"
        verbose_name = "DJ User"
        verbose_name_plural = "DJ Users"

    def create_token(self, username):
        if self.token:
            # If token already exists, check for status
            self.check_token()
        if not self.token_stat:
            # Create token from sales agen name, mobile and timetoken
            now = timezone.now()
            nextcheck = now + datetime.timedelta(days=1)
            timetoken = datetime.datetime.strftime(nextcheck, "%Y%m%d%h%m%s")
            user = str(self.user)
            id = str(self.pk)
            token = user + "||" + id + "||" + timetoken
            token = base64.b64encode(token)
            self.expiry_date = nextcheck
            self.token = token
            #    Set token status to true
            self.token_stat = True
            self.save()
            return token
        else:
            return self.token

    # Function for checking token validity
    def check_token(self):
        now = timezone.now()
        if self.expiry_date <= now:
            self.token_stat = False
            self.token = None
            self.save()
            # If token is expired, return error
            error = {"code": 1405, "description": "Token Expired.. Please Login.."}
        else:
            error = None
        return error


class DJReputation(models.Model):
    dj = models.ForeignKey(DJUser, related_name="dj_reputation", on_delete=models.CASCADE)
    num_followers = models.PositiveIntegerField("Followers", default=0)

    def __str__(self):
        return str(self.dj)

    class Meta:
        app_label = "airadio"
        db_table = "djreputation"
        verbose_name = "DJ Reputation"
        verbose_name_plural = "DJ Reputations"


class DJStationStatus(models.Model):
    dj = models.ForeignKey(
        DJUser, related_name="dj_station_status", on_delete=models.CASCADE
    )
    station = models.ForeignKey(
        Stations, related_name="station_dj_status", on_delete=models.CASCADE
    )
    date = models.DateField("Subscription Date", default=timezone.now)

    def __str__(self):
        return str(self.dj)

    def check_expiry(self):
        current = timezone.now().date()
        d1 = datetime.datetime.strptime(str(self.date), "%Y-%m-%d")
        d2 = datetime.datetime.strptime(str(current), "%Y-%m-%d")
        diff = abs((d2 - d1).days)
        return "Active" if diff < 31 else "Expired"

    class Meta:
        app_label = "airadio"
        db_table = "djstationstatus"
        verbose_name = "DJ Station Subscription"
        verbose_name_plural = "DJ Station Subscriptions"


class DJMusicBed(models.Model):
    station = models.ForeignKey(
        Stations, related_name="station_dj_musicbeds", on_delete=models.CASCADE
    )
    name = models.CharField(_("Name"), max_length=255)
    url = models.CharField(_("URL"), max_length=255)

    def __str__(self):
        return str(self.name)

    class Meta:
        app_label = "airadio"
        db_table = "djmusicbed"
        verbose_name = "DJ Music Bed"
        verbose_name_plural = "DJ Music Beds"


class UserActivity(models.Model):
    TYPE = ("follow", "Follow")
    from_user = models.ForeignKey(
        User, related_name="user_activity_from_user", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name="user_activity_to_user", on_delete=models.CASCADE
    )
    type = models.CharField(max_length=255, default="follow")

    def __str__(self):
        return str(self.from_user)

    class Meta:
        app_label = "airadio"
        db_table = "useractivity"
        verbose_name = "User Activity"
        verbose_name_plural = "User activities"
