from django.contrib import admin
from models import *

class VideoAdmin(admin.ModelAdmin):
    list_display = ('url', 'enabled', 'working', 'last_retrieved', 'corrected_motion')

admin.site.register(Video, VideoAdmin)

class FeedAdmin(admin.ModelAdmin):
	list_display = ('name', 'owner')

admin.site.register(Feed, FeedAdmin)

admin.site.register(Channel)
