from selenium import webdriver
import time
from os import system
from PIL import Image
from StringIO import StringIO
import falcon
import urlparse
from re import compile
from json import dumps

class StreamResource:
	patterns = {
		"livestream.com" : {
			"path" : "//div[@id='image-container']/img",
			"extra": compile("app-argument=http://livestream.com/accounts/(\d+)/events/(\d+)")
		}
	}

	def __init__(self):
		profile = webdriver.FirefoxProfile()
		profile.set_preference("general.useragent.override","Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/8.0.57838 Mobile/12H321 Safari/600.1.4")
		self.driver = webdriver.Firefox(profile)
		self.driver.set_window_size(1024, 768)

	def on_post(self, req, resp):
		url = req.params["url"]
		res = urlparse.urlparse(url)
		loc = res.netloc
		if loc == "":
			raise falcon.HTTPBadRequest("Bad URL", "'%s' is not a valid URL" % url)
		if loc not in self.patterns.keys():
			raise falcon.HTTPBadRequest("Video host %s is not supported" % loc, "Try a different host")
		settings = self.patterns[loc]
		self.driver.get(url)
		element = self.driver.find_element_by_xpath(settings["path"])
		if settings.has_key("extra"):
			extra = settings["extra"].search(self.driver.page_source).groups()
			resp.append_header("X-Extra", dumps(extra))
		ss = self.driver.get_screenshot_as_png()
		im = Image.open(StringIO(ss))
		r = element.rect
		box = (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])
		cropped = im.crop(box)
		out = StringIO()
		cropped.save(out, format='png')
		resp.body = out.getvalue()
		resp.status = falcon.HTTP_200
		resp.content_type = "image/png"

app = falcon.API()
streams = StreamResource()
app.add_route('/streams', streams)
