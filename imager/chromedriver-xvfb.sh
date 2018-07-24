#!/bin/bash
xvfb-run -s "-screen 0, 1024x768x24" -a `pwd`/chromedriver $@
