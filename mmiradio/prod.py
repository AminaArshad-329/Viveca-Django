from .settings import *  # noqa

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["*"]

# Make this unique, and don't share it with anybody.
SECRET_KEY = "skgq5-9-w9+(mf=1i3k5%j4xfarn_$-x7ly5jqqp2@)ov+!sgs"

MIDDLEWARE = MIDDLEWARE + [  # noqa
    "django.middleware.csrf.CsrfViewMiddleware",
]
