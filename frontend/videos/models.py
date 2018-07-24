from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from jsonfield import JSONField
import humanize

min_date = timezone.make_aware(datetime(1970,1,1))

class Video(models.Model):
	url = models.URLField(unique = True)
	name = models.CharField(max_length=255, default="", blank=True)
	enabled = models.BooleanField(default = True)
	working = models.BooleanField(default = False)
	lastRetrieved = models.DateTimeField(default = min_date)
	motion = models.FloatField(default = 0.0)
	offset = models.FloatField(default = 0.0)
	hash = models.CharField(max_length = 100, null = True, blank=True, default = None)
	extra = JSONField(default = {}, blank=True)
	streamURL = models.CharField(max_length = 2048, null = True, blank = True)
	notes = models.CharField(max_length = 1024, null = True, blank = True)
	channel = models.ForeignKey('Channel', null = True, blank = True, default = None, on_delete=models.CASCADE)

	def corrected_motion(self):
		return self.motion + self.offset

	corrected_motion.admin_order_field = 'motion'

	def last_retrieved(self):
		if self.lastRetrieved == min_date:
			return "Never"
		return humanize.naturaltime(timezone.now() - self.lastRetrieved)

	last_retrieved.admin_order_field = 'lastRetrieved'

	def __unicode__(self):
		return self.url

class Feed(models.Model):
	name = models.CharField(max_length = 200)
	description = models.TextField()
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	videos = models.ManyToManyField(Video, blank = True)
	all = False

	class Meta:
		unique_together = ("name", "owner")

class Channel(models.Model):
	url = models.URLField(unique = True)
	name = models.CharField(max_length=255, default="", blank=True)
	enabled = models.BooleanField(default = True)
	working = models.BooleanField(default = False)
	lastRetrieved = models.DateTimeField(default = min_date)
	notes = models.CharField(max_length = 1024, null = True, blank = True)

	def last_retrieved(self):
		if self.lastRetrieved == min_date:
			return "Never"
		return humanize.naturaltime(timezone.now() - self.lastRetrieved)

	last_retrieved.admin_order_field = 'lastRetrieved'

	def __unicode__(self):
		return self.name if self.name != "" else self.url
