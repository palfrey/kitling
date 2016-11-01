from models import Channel, Video
import re
import requests
from django.utils import timezone
from os import environ

import logging
logging.basicConfig()

channels = {
    "livestream": re.compile("http://api.new.livestream.com/accounts/(\d+)"),
    "youtube": re.compile("https://www.youtube.com/channel/(.*)")
}

def get_channel_type(channel_url):
    for key in channels:
        pattern = channels[key]
        res = pattern.search(channel_url)
        if res != None:
            return (key, res)
    return (None, None)

def update_channels():
    print "Updating channels"
    for channel in Channel.objects.all():
        try:
            print "Channel", channel
            channel.lastRetrieved = timezone.now()
            videos = Video.objects.filter(channel=channel)
            existing_videos = []
            (kind, res) = get_channel_type(channel.url)
            video_urls = []
            if kind == "livestream":
                url = "http://api.new.livestream.com/accounts/%s/events?newer=9" % res.groups(1)
                data = requests.get(url).json()
                for item in data["data"]:
                    video_url = "http://livestream.com/%s/%s" % (item["owner"]["short_name"], item["short_name"])
                    video_urls.append(video_url)
            elif kind == "youtube":
                api_key = environ.get("YOUTUBE_API_KEY", None)
                if api_key == None:
                    raise Exception, "No YOUTUBE_API_KEY"
                url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=%s&eventType=live&type=video&key=%s"%(res.group(1), api_key)
                print url
                data = requests.get(url).json()
                for item in data["items"]:
                    video_url = "https://www.youtube.com/embed/%s" % (item["id"]["videoId"])
                    video_urls.append(video_url)
            else:
                print "Don't know %s channel" % channel.url
                channel.working = False
                channel.save()
                continue
            for video_url in video_urls:
                print video_url
                filtered = videos.filter(url=video_url)
                if filtered.exists():
                    existing_videos.append(filtered.first().id)
                else:
                    existing_videos.append(Video.objects.create(url=video_url, channel=channel).id)
            missing = videos.exclude(id__in = Video.objects.filter(id__in=existing_videos).values_list('id', flat=True))
            for m in missing:
                m.delete()
            channel.working = True
        except Exception, e:
            print e
            channel.working = False
        print "Updated", channel
        channel.save()
