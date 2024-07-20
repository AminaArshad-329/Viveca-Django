import hashlib
import random
import base64
import requests

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _
from django.utils.http import int_to_base36
from django.template import loader

from utils.views import send_accout_activation_mail, send_email_verification_mail
from airadio.models import (
    Library,
    Stations,
    Locations,
    Genres,
    Sequence,
    Scheduling,
    BrandingTOH,
    Adverts,
    Wall,
    DJTracks,
    DJUser,
    StationPlaylistSocialCode,
    DJMusicBed,
)


class DashboardLibraryForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(DashboardLibraryForm, self).__init__(*args, **kwargs)
        self.fields["genre"].widget.attrs["class"] = "form-control"
        self.fields["rotation_category"].widget.attrs["class"] = "form-control"


class DashboardUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    is_active = forms.BooleanField(required=False)

    def save(self, commit=True):
        user = super(DashboardUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = self.cleaned_data["is_active"]

        if commit:
            user.save()

        return user


class DashboardUserEditForm(forms.Form):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    is_active = forms.BooleanField(required=False)

    def __init__(self, instance, *args, **kwargs):
        super(DashboardUserEditForm, self).__init__(*args, **kwargs)
        self.user = instance

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            if username == self.user.username:
                return username
            else:
                try:
                    User.objects.get(username=username)
                except:
                    return username
                else:
                    raise forms.ValidationError(
                        "A user with that username already exists."
                    )

        else:
            raise forms.ValidationError("This field is required.")

        return username

    def save(self, **kwargs):
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.is_active = self.cleaned_data["is_active"]
        self.user.save()

        if self.cleaned_data["is_active"]:
            try:
                send_accout_activation_mail(self.user)
            except Exception as e:
                print(e)

        return self.user


class DashboardStationForm(forms.ModelForm):
    class Meta:
        model = Stations
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(DashboardStationForm, self).__init__(*args, **kwargs)
        self.fields["location"].widget.attrs["class"] = "form-control"


class SettingStationForm(forms.ModelForm):
    class Meta:
        model = Stations
        fields = (
            "station_name",
            "station_description",
            "station_logo",
            "station_preview",
            "order_id",
            "microsite",
            "location",
            "published",
        )

    def __init__(self, *args, **kwargs):
        super(SettingStationForm, self).__init__(*args, **kwargs)
        self.fields["location"].widget.attrs["class"] = "form-control"


class DashboardLocationForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = "__all__"


class DashboardGenresForm(forms.ModelForm):
    class Meta:
        model = Genres
        fields = "__all__"


class DashboardSequenceForm(forms.ModelForm):
    class Meta:
        model = Sequence
        fields = ("related_station",)

    def __init__(self, *args, **kwargs):
        super(DashboardSequenceForm, self).__init__(*args, **kwargs)
        self.fields["related_station"].widget.attrs["class"] = "select-input"

    def get_station(self):
        return self.cleaned_data["related_station"]


class DashboardSchedulingForm(forms.ModelForm):
    class Meta:
        model = Scheduling
        fields = "__all__"
        exclude = (
            "link",
            "wall",
        )

    def __init__(self, *args, **kwargs):
        super(DashboardSchedulingForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class DashboardStationLocationForm(forms.ModelForm):
    class Meta:
        model = BrandingTOH
        fields = (
            "station",
            "location",
        )

    def __init__(self, *args, **kwargs):
        super(DashboardStationLocationForm, self).__init__(*args, **kwargs)
        self.fields["station"].widget.attrs["class"] = "form-control"
        self.fields["location"].widget.attrs["class"] = "form-control"
        self.fields["location"].empty_label = "All"
        self.fields["station"].empty_label = None


class DashboardBrandingTOHForm(forms.ModelForm):
    class Meta:
        model = BrandingTOH
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(DashboardBrandingTOHForm, self).__init__(*args, **kwargs)
        self.fields["station"].widget.attrs["class"] = "form-control"
        self.fields["location"].widget.attrs["class"] = "form-control"
        self.fields["location"].empty_label = "All"
        # self.fields['station'].empty_label = None


class DashboardAdvertForm(forms.ModelForm):
    class Meta:
        model = Adverts
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(DashboardAdvertForm, self).__init__(*args, **kwargs)
        self.fields["type"].widget.attrs["class"] = "select-input"
        self.fields["cover_art"].widget.attrs["class"] = "form-control"
        self.fields["location"].widget.attrs["class"] = "form-control"
        self.fields["location"].empty_label = "All"


class DashboardWallForm(forms.ModelForm):
    class Meta:
        model = Wall
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(DashboardWallForm, self).__init__(*args, **kwargs)
        self.fields["related_station"].widget.attrs["class"] = "select-input"
        self.fields["media_type"].widget.attrs["class"] = "select-input"


class DJUserSignupForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    password = forms.CharField(required=True)

    class Meta:
        model = DJUser
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        super(DJUserSignupForm, self).__init__(*args, **kwargs)
        self.fields["station"].required = True

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            try:
                User.objects.get(username=username)
            except:
                return username
            else:
                raise forms.ValidationError("A user with that username already exists.")
        else:
            raise forms.ValidationError("This field is required.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            try:
                User.objects.get(email=email)
            except:
                return email
            else:
                raise forms.ValidationError("A user with that email already exists.")
        else:
            raise forms.ValidationError("This field is required.")
        return email

    def save(self, **kwargs):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        user = User.objects.create_user(username, email, password)
        user.is_active = True
        user.save()
        dj_user = super(DJUserSignupForm, self).save(commit=False)
        dj_user.user = user
        dj_user.save()

        self.verify_mail(dj_user)

        try:
            g, created = Group.objects.get_or_create(name="DJ")
            g.user_set.add(user)
        except:
            pass

        return dj_user

    def verify_mail(self, dj_user):
        key = hashlib.sha1(str(random.random())).hexdigest()[:5]
        usernamekey = dj_user.user.username
        if isinstance(usernamekey, unicode):
            usernamekey = usernamekey.encode("utf8")
        dj_user.confirmation_code = hashlib.sha1(key + usernamekey).hexdigest()
        dj_user.save()
        send_email_verification_mail(dj_user)


class DJTracksForm(forms.ModelForm):
    class Meta:
        model = DJTracks
        exclude = ("dj",)

    def __init__(self, *args, **kwargs):
        super(DJTracksForm, self).__init__(*args, **kwargs)

    def save(self, **kwargs):
        user = kwargs.pop("user")
        track = DJTracks.objects.create(
            dj=user.dj_user,
            media=self.cleaned_data["media"],
            recorded="-",
            in_point=self.cleaned_data["in_point"],
            aux_point=self.cleaned_data["aux_point"],
            tags=self.cleaned_data["tags"],
            title=self.cleaned_data["title"],
            cover_art=self.cleaned_data["cover_art"],
            published=True,
        )
        return track


class PasswordResetForm(forms.Form):
    error_messages = {
        "unknown": _(
            "That email address doesn't have an associated "
            "user account. Are you sure you've registered?"
        ),
        "unusable": _(
            "The user account associated with this email "
            "address cannot reset the password."
        ),
    }
    email = forms.EmailField(label=_("Email"), max_length=254)

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        self.users_cache = UserModel._default_manager.filter(email__iexact=email)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages["unknown"])
        if not any(user.is_active for user in self.users_cache):
            # none of the filtered users are active
            raise forms.ValidationError(self.error_messages["unknown"])
        # if any((user.password == UNUSABLE_PASSWORD)
        #        for user in self.users_cache):
        #     raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
    ):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail

        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                "email": user.email,
                "domain": domain,
                "site_name": site_name,
                "uid": int_to_base36(user.pk),
                "user": user,
                "token": base64.b64encode(token_generator.make_token(user)),
                "protocol": use_https and "https" or "http",
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = "".join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])
        return "%s-%s" % (c["uid"], c["token"])


class DashboardStationPlaylistSocialCode(forms.ModelForm):
    class Meta:
        model = StationPlaylistSocialCode
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(DashboardStationPlaylistSocialCode, self).__init__(*args, **kwargs)
        self.fields["type"].widget.attrs["class"] = "form-control"


class DashboardDJMusicBedForm(forms.ModelForm):
    class Meta:
        model = DJMusicBed
        fields = "__all__"


class NewsGenerateForm(forms.Form):
    voice_code = forms.ChoiceField(required=True)
    location_code = forms.ChoiceField(required=True)
    no_of_stories = forms.ChoiceField(
        required=True,
        choices=[(str(i), str(i)) for i in range(1, 6)],
    )
    # news_category = forms.MultipleChoiceField(
    #     required=True,
    #     widget=forms.CheckboxSelectMultiple,
    #     choices=[
    #         ("news", "News"),
    #         ("sports", "Sports"),
    #         ("entertainment", "Entertainment"),
    #         ("weather", "Weather"),
    #     ],
    # )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["voice_code"].empty_label = "SELECT"
        self.fields["location_code"].empty_label = "SELECT"
        self.fields["voice_code"].choices = self.get_voices()
        self.fields["location_code"].choices = self.get_countries()
        fields_to_add_empty_label = ["voice_code", "location_code"]
        for field_name in fields_to_add_empty_label:
            field = self.fields.get(field_name)
            if field:
                field.choices = [("", "SELECT")] + field.choices

    def get_voices(self):
        try:
            newsgenerator_endpoint = "https://newsgenerator.radiostation.ai/voices"
            headers = {"accept": "application/json"}
            response = requests.get(newsgenerator_endpoint, headers=headers)
            if response.status_code == 200:
                voices = [
                    (voice["id"], voice["name"])
                    for voice in response.json().get("voices", [])
                ]
                return voices
        except Exception as e:
            pass
        return []

    def get_countries(self):
        try:
            newsgenerator_endpoint = "https://newsgenerator.radiostation.ai/countries"
            headers = {"accept": "application/json"}
            response = requests.get(newsgenerator_endpoint, headers=headers)
            if response.status_code == 200:
                countries = [
                    (country["code"], country["name"])
                    for country in response.json().get("countries", [])
                ]
                return countries
        except Exception as e:
            pass
        return []
