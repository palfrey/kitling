FROM jimmycuadra/rust
ENV RUST_BACKTRACE=1
WORKDIR /comparer
ADD src/ /comparer/src
ADD Cargo.* /comparer/
RUN cargo build
CMD cargo run
