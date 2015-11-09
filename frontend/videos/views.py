from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from serialisers import *
from models import *
import urlparse
from django.http import HttpResponseBadRequest
from django_genshi import render_to_response
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse
import requests

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
	return render_to_response("index.xml", {"users": User.objects.all(), "feeds" : Feed.objects.all() } )

def display(request, username, feedName):
	feed = Feed.objects.get(owner__username__iexact = username, name__iexact = feedName)
	return render_to_response("display.xml", {"feed": feed } )

def all_display(request):
	class AllFeed(object):
		def __init__(self):
			self.videos = Video.objects.all()
			self.name = "All videos"
			self.all = True

	return render_to_response("display.xml", {"feed": AllFeed(), 'static': staticfiles_storage.url } )

def feed(request, username, feedName):
	feed = Feed.objects.get(owner__username__iexact = username, name__iexact = feedName)
	return feed_core(feed.videos.filter(working__exact = True).order_by("-motion").first())

def all_feeds(request):
	return feed_core(Video.objects.filter(working__exact = True).order_by("-motion").first())

def feed_core(video):
	if video == None:
		return HttpResponseBadRequest("No usable videos")
	res = urlparse.urlparse(video.url)
	loc = res.netloc
	if loc == "":
		return HttpResponseBadRequest("Can't determine host")
	elif loc == "livestream.com":
		url = "http://livestream.com/accounts/%s/events/%s/player?autoPlay=true&amp;mute=false" % tuple(video.extra)
		return render_to_response("feed.xml", {"url": url, "streamURL": video.streamURL} )
	elif loc == "www.ustream.tv":
		url = "%s?html5ui=1&autoplay=true" % video.url
		return render_to_response("feed.xml", {"url": url, "streamURL": video.streamURL} )
	elif loc == "www.youtube.com":
		url = "%s?autoplay=1" % video.url
		return render_to_response("feed.xml", {"url": url, "streamURL": video.streamURL} )
	else:
		return HttpResponseBadRequest("Don't know what to do with host '%s' from %s" % (loc, video.url))

def grabber(request):
	url = request.GET["url"]
	headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/8.0.57838 Mobile/12H321 Safari/600.1.4'}
	r = requests.get(url, headers = headers)
	return HttpResponse(r.text)
