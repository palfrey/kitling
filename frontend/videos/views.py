from django.shortcuts import render

from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from serialisers import *
from models import *

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
