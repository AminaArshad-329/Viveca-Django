from django.views.generic.base import View
from django.http import HttpResponse
from .Response import GenericResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import resolve
import json
import time
import base64


class APIBaseView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        Override the standard ``django.view.generic.base.View.dispatch``
        behavior to do the following:
        1.Attempt to retrieve any POST data as JSON, otherwise fall back to
        deserializing POST data as urlformencoded data.
        """
        """ set the start time """
        self.start_time = time.time()
        self.error = None
        self.login_error = None
        self.request = request
        self.args = args
        self.kwargs = kwargs
        """ Find the url of the request """
        current_url = resolve(request.get_full_path()).url_name
        """
        Default to JSON POST data, but allow urlformencoded data unless the
        data is explicitly designated as JSON via an HTTP Content-type header
        """

        if request.method == "POST":
            try:
                request.POST = json.loads(request.body)
            except Exception as e:
                if "application/json" in request.META.get("CONTENT_TYPE", ""):
                    self.error = {"code": 1301, "description": "Invalid Json Format"}
                elif not request.body:
                    """If it is login then set login error"""
                    if current_url == "login":
                        self.login_error = {
                            "code": 1404,
                            "description": "No data in request",
                        }
                    else:
                        self.error = {"code": 1404, "description": "No data in request"}

        if request.method.lower() in self.http_method_names:
            """get handler"""
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
            handler(request, *args, **kwargs)
            """ method not allowed error """
            error = {
                "code": "1403",
                "description": str(request.method.lower())
                + " is not in allowable http methods",
            }
            response = GenericResponse(error=error)
            return HttpResponse(json.dumps(response), content_type="application/json")
        """
        Here we will find tken errors.
        If the token cannot be base64 decoded then error will be shown.
        Also shows token not found error.
        """
        if not self.error:
            token = request.POST.get("token", "")
            if token:
                try:
                    self.token = base64.decodestring(token)
                except:
                    self.error = {"code": 1400, "description": "Base64 decode error"}
            else:
                self.error = {"code": 1400, "description": "Token not found"}

        self.request = request
        self.args = args
        self.kwargs = kwargs
        """ call the handler """
        data = handler(request, *args, **kwargs)
        """ Find run time """
        self.elapsed_time = time.time() - self.start_time
        data["meta"]["runtime"] = self.elapsed_time
        return HttpResponse(json.dumps(data), content_type="application/json")


class testview(APIBaseView):
    http_method_names = ["post"]

    #    def dispatch(self, request, *args, **kwargs):
    #        print data
    #        return HttpResponse(data)

    def post(self, request, *args, **kwargs):
        data = request.POST
        return data
