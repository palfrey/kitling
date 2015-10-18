FROM ubuntu:15.04
# make sure the package repository is up to date
RUN echo "deb http://archive.ubuntu.com/ubuntu vivid multiverse\n" >> /etc/apt/sources.list
RUN apt-get update

RUN apt-get install -fy xvfb firefox python-pip python-dev libjpeg-dev zlib1g-dev && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
WORKDIR /imager
ADD requirements.txt /imager/requirements.txt
RUN pip install -r /imager/requirements.txt
ADD image.py /imager/image.py
EXPOSE 8000
CMD xvfb-run -e /imager/error.log gunicorn --bind 0.0.0.0:8000 image:app