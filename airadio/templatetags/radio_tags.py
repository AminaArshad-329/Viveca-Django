from django import template
from django.utils.safestring import mark_safe
from airadio.models import Adverts

register = template.Library()

TIME_CHART = {
    1: "12am",
    2: "1am",
    3: "2am",
    4: "3am",
    5: "4am",
    6: "5am",
    7: "6am",
    8: "7am",
    9: "8am",
    10: "9am",
    11: "10am",
    12: "11am",
    13: "12pm",
    14: "1pm",
    15: "2pm",
    16: "3pm",
    17: "4pm",
    18: "5pm",
    19: "6pm",
    20: "7pm",
    21: "8pm",
    22: "9pm",
    23: "10pm",
    24: "11pm",
}


@register.simple_tag
def get_point_stars(value):
    val = int(value)
    list_of_stars = ['<i class="fa-solid fa-star fa-fw ml-2 text-white"></i>'] * 5
    stars = 0
    if val > 0 and val < 26:
        stars = 1
    elif val > 25 and val < 51:
        stars = 2
    elif val > 50 and val < 76:
        stars = 3
    elif val > 75 and val < 101:
        stars = 4
    elif val > 100:
        stars = 5
    else:
        stars = 0
    if stars > 0:
        for i in range(stars):
            list_of_stars[i] = (
                '<i class="fa-solid fa-star fa-fw ml-2 text-amber-500"></i>'
            )
    return mark_safe("".join(str(star) for star in list_of_stars))


@register.simple_tag
def get_advert_types():
    return Adverts().ADVERT_TYPES


@register.simple_tag
def get_playlist_item(content_object):
    content = content_object.content_type.model_class()
    try:
        object = content.objects.get(id=content_object.object_id)
        return object
    except:
        return []


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter
def text_color_class(value):
    if value.__class__.__name__ == "Adverts":
        return "text-red-700"
    elif value.__class__.__name__ == "BrandingTOH":
        return "text-green-700"
    else:
        return "text-blue-700"


@register.filter
def to_time(value):
    return TIME_CHART[value]
