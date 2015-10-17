FROM ubuntu:15.04
# make sure the package repository is up to date
RUN echo "deb http://archive.ubuntu.com/ubuntu vivid multiverse\n" >> /etc/apt/sources.list
RUN apt-get update

RUN apt-get install -fy xvfb firefox python-pip python-dev libjpeg-dev zlib1g-dev && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
VOLUME ["/kittens"]
WORKDIR /kittens
ADD requirements.txt /kittens/requirements.txt
RUN pip install -r /kittens/requirements.txt
ADD test.py /kittens/test.py
CMD xvfb-run -e /kittens/error.log python /kittens/test.py
#CMD xvfb-run -e /kittens/error.log -s "+extension GLX +extension XVideo +extension Composite +extension DAMAGE +extension RENDER +extension RANDR -dpi 100 -s 1048x768x16" python /kittens/test.py
