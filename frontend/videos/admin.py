from django.contrib import admin
from models import *

class VideoAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'enabled', 'working', 'last_retrieved', 'corrected_motion')

admin.site.register(Video, VideoAdmin)

class FeedAdmin(admin.ModelAdmin):
	list_display = ('name', 'owner')

admin.site.register(Feed, FeedAdmin)

class ChannelAdmin(admin.ModelAdmin):
	list_display = ('name', 'url')

admin.site.register(Channel, ChannelAdmin)
