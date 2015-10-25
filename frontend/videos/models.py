from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
	url = models.URLField(unique = True)
	working = models.BooleanField(default = False)
	lastRetrieved = models.DateTimeField(default = None, null = True)
	motion = models.FloatField(default = 0.0)

	def __unicode__(self):
		return self.url

class Feed(models.Model):
	name = models.CharField(max_length = 200)
	owner = models.ForeignKey(User)
	videos = models.ManyToManyField(Video)

	class Meta:
		unique_together = ("name", "owner")
