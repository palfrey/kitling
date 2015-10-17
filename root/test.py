from selenium import webdriver
import time
from os import system
from PIL import Image
from StringIO import StringIO

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override","Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/8.0.57838 Mobile/12H321 Safari/600.1.4")
driver = webdriver.Firefox(profile)
driver.set_window_size(1024, 768)
driver.get("http://livestream.com/accounts/4175709/tip")
element = driver.find_element_by_xpath("//div[@id='image-container']/img")
ss = driver.get_screenshot_as_png()
im = Image.open(StringIO(ss))
r = element.rect
box = (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])
cropped = im.crop(box)
cropped.save("element.png")
driver.quit()
