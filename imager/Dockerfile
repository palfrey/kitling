FROM jimmycuadra/rust:1.8.0
#RUN echo "deb http://archive.ubuntu.com/ubuntu vivid multiverse\n" >> /etc/apt/sources.list
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update

WORKDIR /imager

RUN apt-get install -fy --force-yes --no-install-recommends \
	wget \
	unzip \
	chromium \
	xvfb \
	libgconf2-4 \
	libexif12 \
	xauth \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget http://chromedriver.storage.googleapis.com/2.21/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /imager

ENV RUST_BACKTRACE=1

ADD src/ /imager/src
ADD Cargo.* /imager/
RUN cargo build
ADD log.toml /imager/
EXPOSE 8000
CMD cargo run
