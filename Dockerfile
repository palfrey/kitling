FROM ubuntu:15.04
# make sure the package repository is up to date
RUN echo "deb http://archive.ubuntu.com/ubuntu vivid multiverse\n" >> /etc/apt/sources.list
RUN apt-get update

RUN apt-get install -fy xvfb firefox python-pip python-dev libjpeg-dev zlib1g-dev && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
VOLUME ["/kittens"]
WORKDIR /kittens
ADD requirements.txt /kittens/requirements.txt
RUN pip install -r /kittens/requirements.txt
#ADD test.py /kittens/test.py
RUN apt-get update && apt-get install -y curl
#RUN apt-get install -y python-scipy
CMD xvfb-run -e /kittens/error.log gunicorn test:app
