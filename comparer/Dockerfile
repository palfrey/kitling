FROM rust:1.38-stretch
RUN apt-get update && apt-get install -fy --force-yes --no-install-recommends \
	postgresql-client-common \
	postgresql-client-9.6 \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
ENV RUST_BACKTRACE=1
WORKDIR /comparer
ADD src/ /comparer/src
ADD Cargo.* /comparer/
RUN cargo build
ADD log.toml /comparer/
ADD config.toml /comparer/
COPY wait-for-postgres.sh /comparer/wait-for-postgres.sh
ENV PGPASSWORD mysecretpassword
CMD ./wait-for-postgres.sh postgres && cargo run
