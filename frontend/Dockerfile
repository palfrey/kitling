FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
	python3-pip \
	libpq-dev \
	python3-dev \
	postgresql-client-common \
	postgresql-client \
	build-essential \
	cron \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
COPY requirements.txt requirements.txt
RUN pip3 install setuptools wheel
RUN pip3 install -r requirements.txt
WORKDIR /frontend
COPY kitling /frontend/kitling
COPY videos /frontend/videos
COPY templates /frontend/templates
COPY manage.py /frontend/manage.py
COPY wait-for-postgres.sh /frontend/wait-for-postgres.sh
EXPOSE 8000
ENV PGPASSWORD mysecretpassword
CMD ./wait-for-postgres.sh postgres && python3 manage.py migrate && python3 manage.py crontab add && /etc/init.d/cron start && python3 manage.py runserver 0.0.0.0:8000
