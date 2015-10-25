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
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
]
