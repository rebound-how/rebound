FROM rust:1-bullseye AS build-env

WORKDIR /app

RUN apt-get update && apt install -y protobuf-compiler && \
    rustup component add rust-src --toolchain nightly-x86_64-unknown-linux-gnu
RUN cargo install bpf-linker --git https://github.com/aya-rs/bpf-linker.git

COPY ./fault /app

RUN cargo +nightly build --release

FROM gcr.io/distroless/cc-debian12

LABEL org.opencontainers.image.source=https://github.com/rebound-how/rebound

COPY --from=build-env --chown=65532:65532 /app/target/release/fault /

WORKDIR /home/nonroot
USER nonroot

EXPOSE 8080

ENTRYPOINT ["/fault"]
CMD []
