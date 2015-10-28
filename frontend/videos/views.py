from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from serialisers import *
from models import *
import urlparse

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

def feed(request, username, feedName):
	feed = Feed.objects.get(owner__username__iexact = username, name__iexact = feedName)
	video = feed.videos.order_by("-motion").first()
	res = urlparse.urlparse(video.url)
	loc = res.netloc
	if loc == "":
		return HttpResponseBadRequest("Can't determine host")
	elif loc == "livestream.com":
		url = "http://livestream.com/accounts/%s/events/%s/player?autoPlay=true&amp;mute=false" % tuple(video.extra)
		return render_to_response("feed.xml", {"url": url} )
	else:
		return HttpResponseBadRequest("Don't know what to do with host '%s' from %s" % (loc, video.url))
