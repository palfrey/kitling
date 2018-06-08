from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from .serialisers import *
from .models import *
from urllib.parse import urlparse
from django.http import HttpResponseBadRequest
from django.db.models import F

from django_genshi import render_to_response

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

	return render_to_response("display.xml", {"feed": AllFeed() } )

feed_order = (F('motion') + F('offset')).desc()

def feed(request, username, feedName):
	feed = Feed.objects.get(owner__username__iexact = username, name__iexact = feedName)
	return feed_core(feed.videos.filter(enabled__exact = True, working__exact = True).order_by(feed_order).first())

def all_feeds(request):
	return feed_core(Video.objects.filter(enabled__exact = True, working__exact = True).order_by(feed_order).first())

def feed_core(video):
	if video == None:
		return HttpResponseBadRequest("No usable videos")
	res = urlparse(video.url)
	loc = res.netloc
	if loc == "":
		return HttpResponseBadRequest("Can't determine host")
	elif loc == "livestream.com":
		url = "http://livestream.com/accounts/%s/events/%s/player?autoPlay=true&amp;mute=false" % tuple(video.extra)
		return render_to_response("feed.xml", {"url": url} )
	elif loc == "www.ustream.tv":
		url = "%s?html5ui=1&autoplay=true" % video.url
		return render_to_response("feed.xml", {"url": url} )
	elif loc == "www.youtube.com":
		url = "%s?autoplay=1" % video.url
		return render_to_response("feed.xml", {"url": url} )
	else:
		return HttpResponseBadRequest("Don't know what to do with host '%s' from %s" % (loc, video.url))
