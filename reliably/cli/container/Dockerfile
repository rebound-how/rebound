FROM ubuntu:23.10 AS build-venv

ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc

COPY pyproject.toml pdm.lock /home/svc/
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip python3.11-venv curl && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3.11 - && \
    export PATH="$PATH:/root/.local/bin" && \
    pdm self update && \
    cd /home/svc/ && \
    pdm venv create  && \
    pdm use .venv && \
    pdm install -v --no-editable --no-self && \
    chown --recursive svc:svc /home/svc/.venv  && \
    apt-get remove -y build-essential gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

FROM ubuntu:23.10

LABEL org.opencontainers.image.authors="Reliably <contact@reliably.com>"
LABEL org.opencontainers.image.vendor="Reliably"
LABEL org.opencontainers.image.url="https://reliably.com"
LABEL org.opencontainers.image.licenses="Apache-2.0"

RUN apt-get update && apt-get install -y curl python3.11 python3-distutils && \
    groupadd -g 1001 svc && useradd -m -u 1001 -g svc svc && \
    curl -Lo aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.6.11/aws-iam-authenticator_0.6.11_linux_amd64 && \
    chmod +x ./aws-iam-authenticator && \
    chown svc:svc ./aws-iam-authenticator && \
    mv ./aws-iam-authenticator /home/svc/aws-iam-authenticator && \
    apt-get remove -y curl && \
    apt-get remove --auto-remove -y golang-go && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build-venv --chown=svc:svc /home/svc/.venv /home/svc/.venv
WORKDIR /home/svc
COPY --chown=svc:svc settings.yaml /home/svc/.chaostoolkit/settings.yaml
USER 1001

RUN mkdir -p /home/svc/bin && \
    mv ./aws-iam-authenticator /home/svc/bin/aws-iam-authenticator

ENV PATH="$PATH:/home/svc/bin:/home/svc/.venv/bin"

ENTRYPOINT ["/home/svc/.venv/bin/reliably"]
CMD ["--help"]
