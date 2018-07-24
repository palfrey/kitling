from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from .serialisers import *
from .models import *
from urllib.parse import urlparse
from django.http import HttpResponseBadRequest
from django.db.models import F
from django.shortcuts import render

class UserViewSet(viewsets.ModelViewSet):
	permission_classes = (permissions.IsAdminUser,)
	queryset = User.objects.all().order_by('-date_joined')
	serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
	permission_classes = (permissions.IsAdminUser,)
	queryset = Group.objects.all()
	serializer_class = GroupSerializer

class VideoViewSet(viewsets.ModelViewSet):
	permission_classes = (permissions.IsAdminUser,)
	queryset = Video.objects.all()
	serializer_class = VideoSerializer

class FeedViewSet(viewsets.ModelViewSet):
	queryset = Feed.objects.all()
	serializer_class = FeedSerializer

def index(request):
	feeds = {}
	users = User.objects.all()
	all_feeds = Feed.objects.all()
	for user in users:
		feeds[user.username] = [x for x in all_feeds if x.owner == user]
	return render(request, "index.xml", {"all_feeds" : feeds })

def display(request, username, feedName):
	feed = Feed.objects.get(owner__username__iexact = username, name__iexact = feedName)
	url = "/feed/%s/%s/" % (feed.owner.username, feed.name)
	return render(request, "display.xml", {"feed": feed, "url": url } )

def all_display(request):
	class AllFeed(object):
		def __init__(self):
			self.videos = Video.objects.all()
			self.name = "All videos"
			self.all = True

	return render(request, "display.xml", {"feed": AllFeed(), "url": "/feed/_all/" } )

feed_order = (F('motion') + F('offset')).desc()

def feed(request, username, feedName):
	feed = Feed.objects.get(owner__username__iexact = username, name__iexact = feedName)
	return feed_core(request, feed.videos.filter(enabled__exact = True, working__exact = True).order_by(feed_order).first())

def all_feeds(request):
	return feed_core(request, Video.objects.filter(enabled__exact = True, working__exact = True).order_by(feed_order).first())

def feed_core(request, video):
	if video == None:
		return HttpResponseBadRequest("No usable videos")
	res = urlparse(video.url)
	loc = res.netloc
	if loc == "":
		return HttpResponseBadRequest("Can't determine host")
	elif loc == "livestream.com":
		url = "http://livestream.com/accounts/%s/events/%s/player?autoPlay=true&amp;mute=false" % tuple(video.extra)
		return render(request, "feed.xml", {"url": url, "streamURL": video.streamURL} )
	elif loc == "www.ustream.tv":
		url = "%s?html5ui=1&autoplay=true" % video.url
		return render(request, "feed.xml", {"url": url, "streamURL": video.streamURL} )
	elif loc == "www.youtube.com":
		url = "%s?autoplay=1" % video.url
		return render(request, "feed.xml", {"url": url, "streamURL": video.streamURL} )
	else:
		return HttpResponseBadRequest("Don't know what to do with host '%s' from %s" % (loc, video.url))

def grabber(request):
	url = request.GET["url"]
	headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/8.0.57838 Mobile/12H321 Safari/600.1.4'}
	r = requests.get(url, headers = headers)
	return HttpResponse(r.text)
