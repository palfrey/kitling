from selenium import webdriver
import time
from os import system
from PIL import Image
from StringIO import StringIO
import falcon
import urlparse
from re import compile
from json import dumps
import sys
import livestreamer

def livestream(driver):
	patt = compile("app-argument=http://livestream.com/accounts/(\d+)/events/(\d+)")
	return patt.search(driver.page_source).groups()

def ustream(driver):
	element = driver.find_element_by_xpath("//video[@id='UViewer']")
	return element.get_attribute("src")

def youtube_rewrite(url):
	return url + "?autoplay=1"

class StreamResource:
	patterns = {
		"livestream.com" : {
			"driver": "iphone",
			"path" : "//div[@id='image-container']/img",
			"extra": livestream
		},
		"www.ustream.tv" : {
			"driver": "iphone",
			"path": "//video[@id='UViewer']",
			"extra": ustream
		},
		"www.youtube.com": {
			"driver": "default",
			"path": "//div[@id='player']",
			"rewrite": youtube_rewrite
		}
	}

	def rebuild_drivers(self):
		while True:
			for driver in self.drivers.values():
				try:
					print "killing", driver
					driver.quit()
				except Exception, e:
					print "issues closing down", driver
					print e

			def getProfile():
				profile = webdriver.FirefoxProfile()
				profile.set_preference("app.update.autoUpdateEnabled", False)
				profile.set_preference("app.update.enabled", False);
				return profile

			try:
				self.drivers = {}
				profile = getProfile()
				profile.set_preference("general.useragent.override","Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/8.0.57838 Mobile/12H321 Safari/600.1.4")
				self.drivers["iphone"] = webdriver.Firefox(profile)
				self.drivers["iphone"].set_window_size(1024, 768)

				profile = getProfile()
				profile.set_preference("media.mediasource.enabled", True)
				profile.set_preference("media.mediasource.ignore_codecs", True)
				profile.set_preference("media.fragmented-mp4.exposed", True)
				profile.set_preference("media.fragmented-mp4.ffmpeg.enabled", True)
				self.drivers["default"] = webdriver.Firefox(profile)
				self.drivers["default"].set_window_size(1024, 768)
				break
			except Exception, e:
				print "Error while loading Firefox", e
				print "Waiting 5 seconds..."
				time.sleep(5)

	def __init__(self):
		self.drivers = {}
		self.rebuild_drivers()

	def on_post(self, req, resp):
		url = req.params["url"]
		res = urlparse.urlparse(url)
		loc = res.netloc
		if loc == "":
			raise falcon.HTTPBadRequest("Bad URL", "'%s' is not a valid URL" % url)
		if loc not in self.patterns.keys():
			raise falcon.HTTPBadRequest("Video host %s is not supported" % loc, "Try a different host")
		settings = self.patterns[loc]
		if settings.has_key("rewrite"):
			url = settings["rewrite"](url)
		try:
			driver = self.drivers[settings["driver"]]
			driver.get(url)
			time.sleep(5)
			try:
				element = driver.find_element_by_xpath(settings["path"])
			except Exception, e:
				print e
				open("dump.txt","wb").write(driver.page_source.encode("utf-8"))
				raise
			if settings.has_key("extra"):
				extra = settings["extra"](driver)
				resp.append_header("X-Extra", dumps(extra))
			ss = driver.get_screenshot_as_png()
			im = Image.open(StringIO(ss))
			try:
				r = element.rect
			except Exception, e:
				raise Exception, ("rect error", element), sys.exc_info()[2]
			box = (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])
			cropped = im.crop(box)
			out = StringIO()
			try:
				cropped.save(out, format='png')
			except Exception, e:
				raise Exception, ("save failure", box, r), sys.exc_info()[2]

			streams = livestreamer.streams(url)
			if streams.has_key("best"):
				resp.append_header("X-Stream", streams['best'].url)
			resp.body = out.getvalue()
			resp.status = falcon.HTTP_200
			resp.content_type = "image/png"
		except Exception:
			self.rebuild_drivers()
			raise

app = falcon.API()
streams = StreamResource()
app.add_route('/streams', streams)
