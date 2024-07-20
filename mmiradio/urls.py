from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import re_path, path, include
from django.views.generic.base import RedirectView
from django.views.static import serve
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from airadio.views.viveca_dashboard import PlaylistExportJson

openapi_info = openapi.Info(
    title="AI RADIO API",
    default_version="v1",
    description="The Radio Schema",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="contact@snippets.local"),
    license=openapi.License(name="BSD License"),
)

schema_view = get_schema_view(
    openapi_info,
    urlconf="airadio.urls.urls",
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# openapi_info_api_v2 = openapi.Info(
#     title="AI RADIO API",
#     default_version="v2",
#     description="The Radio Schema",
#     terms_of_service="https://www.google.com/policies/terms/",
#     contact=openapi.Contact(email="contact@snippets.local"),
#     license=openapi.License(name="BSD License"),
# )

# schema_view_api_v2 = get_schema_view(
#     openapi_info_api_v2,
#     patterns=[
#         path("api/v2.0/", include("airadio.urls.api_v2"))
#     ],
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

import os
from django.shortcuts import render
import yaml


def swagger_ui(request):
    # Path to your YAML file
    yaml_file_path = os.path.join("api_v2_swagger.yaml")

    # Load YAML file
    with open(yaml_file_path, "r") as yaml_file:
        swagger_yaml = yaml.safe_load(yaml_file)

    return render(request, "swagger.html", {"swagger_yaml": (swagger_yaml)})


urlpatterns = [
    re_path(r"^api/swagger/", swagger_ui, name="swagger_yaml"),
]

urlpatterns += [
    # re_path(r"^grappelli/", include("grappelli.urls")),  # Grappelli URLS
    re_path(r"^api/v1.0/", include("airadio.urls.api")),  # API URLS
    re_path(r"^api/v2.0/", include("airadio.urls.api_v2")),  # API V2.0 URLS
    re_path(r"^widget/web/", include("airadio.urls.widget")),  # WEB WIDGET URLS
    re_path(r"^registration/", include("airadio.urls.registration")),
    re_path(
        r"^playlist/export/$", PlaylistExportJson.as_view(), name="playlist_export_json"
    ),
    path("", include("airadio.urls.urls")),
    path("admin/", admin.site.urls),
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path(
        "favicon.ico",
        RedirectView.as_view(url=settings.STATIC_URL + "images/favicon.ico"),
    ),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
