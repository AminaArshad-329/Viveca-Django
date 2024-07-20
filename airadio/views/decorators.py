from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt

from .Response import GenericResponse as api_response
from urllib.parse import urlparse
from airadio.views.backends import APIAuthBackend
from airadio.models import AuthorizedRetailUser
from functools import wraps


def token_required(view_func):
    """Decorator which ensures the user has provided a correct user and token pair."""

    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = None
        token = None
        basic_auth = request.META.get("HTTP_AUTHORIZATION")

        if basic_auth:
            auth_method, auth_string = basic_auth.split(" ", 1)

            if auth_method.lower() == "basic":
                auth_string = auth_string.strip().decode("base64")
                user, token = auth_string.split(":", 1)

        if request.method == "POST":
            try:
                token = json.loads(request.body).get("token")
            except:
                token = request.POST.get("token")

            if token:
                user = APIAuthBackend().authenticate(token_string=token)
                if user:
                    user.backend = "airadio.views.backends.APIAuthBackend"
                    login(request, user)
                    return view_func(request, *args, **kwargs)
                else:
                    response = api_response(
                        meta={},
                        result={},
                        error={"code": 1400, "description": "token invalid/expired."},
                    )
            else:
                response = api_response(
                    meta={},
                    result={},
                    error={"code": 1400, "description": "token Required"},
                )
        else:
            response = api_response(
                meta={},
                result={},
                error={
                    "code": "1403",
                    "description": str(request.method.lower())
                    + " is not in allowable http methods",
                },
            )

        return HttpResponse(json.dumps(response), mimetype="application/json")

    return _wrapped_view


def check_authorized(view_func):
    """Decorator which ensures the request from a mmi authorized retailer."""

    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        ref = request.META.get("HTTP_REFERER")
        if ref and not ref == "":
            domain = urlparse(ref).hostname
            auths = AuthorizedRetailUser.objects.filter(domain=domain)
            if auths:
                return view_func(request, *args, **kwargs)
        #        authorised_ip = AuthorizedRetailUser.objects.filter(ipaddress = ip)
        #        if authorised_ip:
        #            return view_func(request, *args, **kwargs)
        return HttpResponse(
            json.dumps(
                {"code": "401", "error": "You are not authorised to view this content."}
            ),
            mimetype="application/json",
        )

    return _wrapped_view
