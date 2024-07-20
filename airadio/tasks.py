import requests
import json
import os
import urllib
from django.conf import settings
from django.core.files import File
from django.contrib.sites.models import Site
from django.urls import reverse

from airadio.models import ExportPlaylist, ExportPlaylistItem, Stations
from mmiradio.celery import app


@app.task
def get_image_file_url(url, object):
    try:
        print("Started get_image_file_url")
        content = urllib.urlopen(url).read()
        mediaURL = settings.MEDIA_ROOT + "/coverart" + str(object.id) + ".png"
        localFile = open(mediaURL, "w")
        localFile.write(content)
        localFile.close()
        # return mediaURL
        print("Saving image to database.")
        object.cover_art.save("coverart.png", File(open(mediaURL)))
        os.remove(mediaURL)
        print("SAVED")
    except Exception as e:
        print("Error :", e)
        return None


@app.task
def export_palylist(location, station, lat, longi):
    site = Site.objects.get(pk=1)
    obj_station = Stations.objects.get(id=station)
    url = "http://" + site.domain + reverse("api_music")
    data = requests.post(
        url, data=json.dumps({"station_id": station, "latitude": lat, "longitude": longi})
    )
    results = json.loads(data.text)["result"]["playlist"]
    count = len(results)
    ctr = 0
    olds = ExportPlaylist.objects.filter(station=obj_station, location=location)
    for old in olds:
        old.exports.all().delete()
        old.delete()
    if count > 0:
        for x in range(24):
            temp = []
            while len(temp) <= 13:
                if not results[ctr:]:
                    ctr = 0
                item = results[ctr]
                if item["-type"] == ["MUSIC"]:
                    export, created = ExportPlaylist.objects.get_or_create(
                        hour=x + 1, station=obj_station, location=location
                    )
                    item = ExportPlaylistItem.objects.create(export=export, item=item)
                    temp.append(item)
                ctr = ctr + 1
    return None
