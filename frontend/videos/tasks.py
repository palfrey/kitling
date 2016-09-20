from models import Channel, Video
import re
import requests

import logging
logging.basicConfig()

def update_channels():
    print "Updating channels"
    livestream = re.compile("http://api.new.livestream.com/accounts/(\d+)")
    for channel in Channel.objects.all():
        print channel
        videos = Video.objects.filter(channel=channel)
        existing_videos = []
        res = livestream.search(channel.url)
        if res != None:
            url = "http://api.new.livestream.com/accounts/%s/events?newer=9" % res.groups(1)
            data = requests.get(url).json()
            for item in data["data"]:
                video_url = "http://livestream.com/%s/%s" % (item["owner"]["short_name"], item["short_name"])
                print video_url
                filtered = videos.filter(url=video_url)
                if filtered.exists():
                    existing_videos.append(filtered.first().id)
                else:
                    existing_videos.append(Video.objects.create(url=video_url, channel=channel).id)
        else:
            print "Don't know %s channel" % channel.url
            continue
        missing = videos.exclude(id__in = Video.objects.filter(id__in=existing_videos).values_list('id', flat=True))
        for m in missing:
            m.delete()
