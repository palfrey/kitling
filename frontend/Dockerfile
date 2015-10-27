FROM ubuntu:15.04
RUN echo "deb http://archive.ubuntu.com/ubuntu vivid multiverse\n" >> /etc/apt/sources.list
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y python-pip libpq-dev python-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /frontend
COPY kitling /frontend/kitling
COPY videos /frontend/videos
COPY manage.py /frontend/manage.py
EXPOSE 8000
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
