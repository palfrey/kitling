from django.contrib import admin
from models import *

class VideoAdmin(admin.ModelAdmin):
	list_display = ('name', 'url', 'enabled', 'working', 'last_retrieved', 'corrected_motion')
	list_display_links = list_display

admin.site.register(Video, VideoAdmin)

class FeedAdmin(admin.ModelAdmin):
	list_display = ('name', 'owner')
	list_display_links = list_display

admin.site.register(Feed, FeedAdmin)

class ChannelAdmin(admin.ModelAdmin):
	list_display = ('name', 'url')
	list_display_links = list_display

admin.site.register(Channel, ChannelAdmin)
