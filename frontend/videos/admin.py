from django.contrib import admin
from models import *

class VideoAdmin(admin.ModelAdmin):
    list_display = ('url','working', 'lastRetrieved')

admin.site.register(Video, VideoAdmin)

class FeedAdmin(admin.ModelAdmin):
	list_display = ('name', 'owner')

admin.site.register(Feed, FeedAdmin)
