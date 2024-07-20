from django.views.generic.base import View
from django.shortcuts import HttpResponse

from airadio.models import DJUser


class EmailVerfiyView(View):
    def get(self, request, key, *args, **kwargs):
        response = "Successfully verified your email, please login to continue."
        try:
            djuser = DJUser.objects.get(confirmation_code=key, email_verified=False)
            djuser.email_verified = True
            djuser.save()
        except (DJUser.DoesNotExist, DJUser.MultipleObjectsReturned):
            response = "This link has got expired."
        return HttpResponse(response)
