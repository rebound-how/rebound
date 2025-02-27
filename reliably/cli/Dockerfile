FROM ubuntu:24.10 AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG PDM_BUILD_SCM_VERSION=0.1.0

RUN groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc

COPY pyproject.toml pdm.lock README.md /home/svc/
COPY reliably_cli/ /home/svc/reliably_cli/

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential apt-transport-https curl gcc && \
    apt-get install -y python3.12 python3.12-venv && \
    curl -LsSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3.12 - && \
    export PATH="$PATH:/root/.local/bin" && \
    cd /home/svc/ && \
    pdm sync -v --no-editable --prod -G chaostoolkit && \
    chown --recursive svc:svc /home/svc && \
    apt-get remove -y build-essential apt-transport-https curl gcc python3.12-venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

FROM ubuntu:24.10

LABEL org.opencontainers.image.authors="Reliably <sylvain@reliably.com>"
LABEL org.opencontainers.image.vendor="Reliably"
LABEL org.opencontainers.image.url="https://reliably.com"
LABEL org.opencontainers.image.licenses="Apache-2.0"

RUN apt-get update && \
    apt-get install -y python3.12 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc
USER 1001

WORKDIR /home/svc
COPY --from=builder --chown=svc:svc /home/svc/.venv /home/svc/.venv
ENV PATH="/home/svc/.venv/bin:${PATH}"
ENV PYTHONPATH="/home/svc/.venv/lib"

ENTRYPOINT ["/home/svc/.venv/bin/reliably"]
CMD ["--help"]
