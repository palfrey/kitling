from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from videos import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'videos', views.VideoViewSet)
router.register(r'feeds', views.FeedViewSet)

urlpatterns = [
    url(r'^$', views.index),
    url(r'^display/(?P<username>[^/]+)/(?P<feedName>[^/]+)/$', views.display),
    url(r'^display/_all/$', views.all_display),
    url(r'^feed/(?P<username>[^/]+)/(?P<feedName>[^/]+)/$', views.feed),
    url(r'^feed/_all/$', views.all_feeds),
    url(r'^grabber/$', views.grabber),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
]
