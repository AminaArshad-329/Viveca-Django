# Django settings for mmiradio project.
import os
from pathlib import Path

# from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()


def gettext(s):
    return s


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)
# SUPER_DIR = os.path.abspath(os.path.join(PROJECT_DIR, os.path.pardir))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS = (
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    # 'grappelli',
    # 'grappelli.dashboard',
    "debug_toolbar",
    "airadio",
    "drf_yasg",
    "utils",
    "el_pagination",
    "django_extensions",
    "mailer",
    "tailwind",
    "theme",
    "mmiradio",
    "storages",
    "corsheaders",
)


ADMINS = (("Akhil", "akhil.sayone@gmail.com"),)

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", ""),
        "USER": os.environ.get("POSTGRES_USER", ""),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", ""),
        "PORT": "5432",
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "America/Chicago"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


DEFAULT_FILE_STORAGE = "storages.backends.s3.S3Storage"
# GS_BUCKET_NAME = "viveca_static"
# STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
#     os.path.join(PROJECT_DIR, "googleserviceaccount.json")
# )
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "skgq5-9-w9+(mf=1i3k5%j4xfarn_$-x7ly5jqqp2@)ov+!sgs"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mmiradio.urls"

WSGI_APPLICATION = "mmiradio.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": True,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# django-tailwind settings
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = ["127.0.0.1"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://airadioplayer.com",
    "https://cms.radiostation.ai",
]

CSRF_TRUSTED_ORIGINS = [
    "https://cms.radiostation.ai",
    "http://143.42.119.227:8008",
    "http://143.42.119.227:8000",
]
# CORS_ALLOW_ALL_ORIGINS = True

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "airadio.views.backends.APIAuthBackend",
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[DJANGO] %(levelname)s %(asctime)s %(module)s "
            "%(name)s.%(funcName)s:%(lineno)s: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "loggers": {
        "*": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        }
    },
}

GRAPPELLI_ADMIN_TITLE = "MMi Radio"

LOGIN_REDIRECT_URL = "/"

# CUMULUS = {
#     'USERNAME': 'tairamo',
#     'API_KEY': '3f46261945c6253df63725a870f16bb4',
#     'CONTAINER': 'mmiradio',
#     "CONTAINER_URI": 'http://3004f301d515392d9d43-0bd327dd7f8ce1ad6b1c6a3e47538218.r48.cf5.rackcdn.com',
#     'REGION': 'IAD',
# }

# RACKSPACE_CONTAINER_URL = CUMULUS['CONTAINER_URI']

# DEFAULT_FILE_STORAGE = 'cumulus.storage.SwiftclientStorage'

# CUMULUS = {
#    "CONTAINER_URI": 'https://storage101.iad3.clouddrive.com/v1/MossoCloudFS_800d2e2c-71d7-49d6-8dd6-2a5f55653974/viveca',
#    "CONTAINER_URI": 'http://97a1e7965e64b41551fb-5f5df0c2db5912b5a47201968ee41d97.r43.cf5.rackcdn.com',
# }

AWS_S3_REGION_NAME = os.environ["AWS_S3_REGION_NAME"]
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = "assets.radiostation.ai"
AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_REGION_NAME}.linodeobjects.com"
AWS_BUCKET_URL = f"{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.linodeobjects.com"

DISCOGS_API_KEY = os.environ.get("DISCOGS_API_KEY")
DISCOGS_API_SECRET = os.environ.get("DISCOGS_API_SECRET")
LAST_FM_API_KEY = os.environ.get("LAST_FM_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
OPEN_WEATHER_API_KEY = os.environ.get("OPEN_WEATHER_API_KEY")

# Email Settings
# EMAIL_HOST = 'outlook.office365.com'
# EMAIL_HOST_PASSWORD = 'PL7272002M1neral'
# EMAIL_HOST_USER = 'info@mmibroadcasting.com'
# EMAIL_PORT = 443
# EMAIL_USE_TLS = True
# ADMIN_EMAIL = 'info@mmibroadcasting.com'

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
#         "LOCATION": "cache:11211",
#     }
# }

# EMAIL_BACKEND = "mailer.backend.DbBackend"


ADMIN_SHORTCUTS = [
    {
        "shortcuts": [
            {
                "url": "/",
                "open_new_window": True,
            },
            {
                "url": "/",
                "title": "AI Radio Dashboard",
            },
            {
                "url": "/admin/auth/user/",
                "title": "Users",
            },
            # {
            #     'url_name': 'admin:site_changelist',
            #     'title': 'Site',
            # },
        ]
    }
]

ADMIN_SHORTCUTS_SETTINGS = {
    "hide_app_list": False,
    "open_new_window": False,
}

# Parse Settings
APPLICATION_ID = "0YUsoEJkRskpRDQkAN8xeLsDzzmy3RHv5dzNKBM5"
REST_API_KEY = "M2RoC2m9owrpRLqGRmrZNOg8LC8FaZJeq6nLtW6j"
MASTER_KEY = "m8HCbmuN6uqBbhAuWnYeGNzrjrEbXxbah6tHK0Vd"

# TWITTER PARAMETERS
TWITTER_CONSUMER_KEY = "Ec3zxoJ80bi5vZWOLajYDx121"
TWITTER_CONSUMER_SECRET = "LCtmkq9PE08i1iT8SdKPEO4QUVwt6s6HSI3blKzMr1MBzDogXH"
TWITTER_ACCESS_TOKEN = "1553598391-QlAbTWGQbrLrvKwpi5NK5VCCgyd7kffpYuIJzwa"
TWITTER_ACCESS_TOKEN_SECRET = "OFoExBQOi3s4cqeoptdn6xuoo8RuM4nnDFqhdokCnHwR0"

# INSTAGRAM PARAMETERS
INSTAGRAM_CLIENT_ID = "7d98f4c968f5447297de56225de60883"

SESSION_COOKIE_AGE = 86400

# Email Settings
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_PASSWORD = "noreply619#"
EMAIL_HOST_USER = "noreplytothis4@gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMIN_EMAIL = "noreplytothis4@gmail.com"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# NPM_BIN_PATH = "/usr/local/bin/npm"
