FROM ubuntu:24.10 AS backend-builder

ARG DEBIAN_FRONTEND=noninteractive
ARG PDM_BUILD_SCM_VERSION=0.1.0

RUN groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc

WORKDIR /home/svc

COPY backend/pyproject.toml /home/svc/pyproject.toml
COPY backend/pdm.lock /home/svc/prod.lock
COPY backend/README.md /home/svc/docs/README.md
COPY backend/reliably_app /home/svc/reliably_app

RUN ls .

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl git libpq-dev gcc && \
    apt-get install -y python3.12 python3.12-dev python3-pip python3.12-venv && \
    curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 - && \
    export PATH=/root/.local/bin:$PATH  && \
    pdm venv create --with venv `which python3.12` && \
    pdm install --no-editable -v --prod --lock prod.lock && \
    chown --recursive svc:svc /home/svc && \
    apt-get remove -y build-essential git gcc  && \
    apt-get clean && rm -rf /var/lib/apt/lists/* 


FROM node:lts as frontend-builder

WORKDIR /usr/src/app
COPY frontend/package*.json ./
RUN npm install

COPY frontend .
RUN npm run build



FROM ubuntu:24.10

ARG DEBIAN_FRONTEND=noninteractive
ARG APP_HOST=0.0.0.0
ARG APP_PORT=9090

LABEL org.opencontainers.image.vendor="Rebound"
LABEL org.opencontainers.image.url="https://rebound.how"

RUN apt-get update && \
    groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc && \
    apt-get install -y --no-install-recommends python3.12 libpq5 && \
    mkdir -p /home/svc/bin && \
    chown svc:svc /home/svc && \
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY --from=backend-builder --chown=svc:svc /home/svc/.venv /home/svc/.venv
COPY --from=backend-builder --chown=svc:svc /home/svc/reliably_app/cli/default.docker.env /home/svc/.config/rebound/reliably.env
COPY --from=frontend-builder /usr/src/app/dist/ /home/svc/www

WORKDIR /home/svc
USER 1001

RUN printf '#!/bin/bash \n\
set -e \n\
export APP_HOST=${HOST} \n\
export APP_PORT=${PORT} \n\
export APP_DOMAIN=${HOST}:${PORT} \n\
exec "$@" \n\
' > /home/svc/entrypoint.sh && chmod a+x /home/svc/entrypoint.sh

ENV PATH="/home/svc/bin:/home/svc/.venv/bin:${PATH}"
ENV PYTHONPATH="/home/svc/.venv/lib"
ENV HOST=${APP_HOST}
ENV PORT=${APP_PORT}

ENTRYPOINT ["./entrypoint.sh"]
CMD ["reliably-server", "run", "--no-pid-file"]
