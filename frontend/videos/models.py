from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from jsonfield import JSONField
import humanize

class Video(models.Model):
	url = models.URLField(unique = True)
	working = models.BooleanField(default = False)
	lastRetrieved = models.DateTimeField(default = datetime.min)
	motion = models.FloatField(default = 0.0)
	offset = models.FloatField(default = 0.0)
	hash = models.CharField(max_length = 100, null = True, blank=True, default = None)
	extra = JSONField(default = {}, blank=True)
	streamURL = models.CharField(max_length = 2048, null = True, blank = True)

	def corrected_motion(self):
		return self.motion + self.offset

	corrected_motion.admin_order_field = 'motion'

	def last_retrieved(self):
		return humanize.naturaltime(datetime.now(self.lastRetrieved.tzinfo) - self.lastRetrieved)

	last_retrieved.admin_order_field = 'lastRetrieved'

	def __unicode__(self):
		return self.url

class Feed(models.Model):
	name = models.CharField(max_length = 200)
	description = models.TextField()
	owner = models.ForeignKey(User)
	videos = models.ManyToManyField(Video, blank = True)
	all = False

	class Meta:
		unique_together = ("name", "owner")
