FROM ubuntu:24.10 AS build-venv

ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1001 svc && useradd -r -u 1001 -g svc svc

COPY pyproject.toml pdm.lock /home/svc/
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential apt-transport-https ca-certificates gcc curl python3.12 python3.12-venv && \
    curl -LsSf https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3.12 - && \
    export PATH="$PATH:/root/.local/bin" && \
    cd /home/svc/ && \
    pdm venv create --with venv `which python3.12` && \
    pdm install -v --no-editable --no-self --prod --lock prod.lock && \
    chown --recursive svc:svc /home/svc/.venv  && \
    apt-get remove -y build-essential gcc curl gnupg apt-transport-https python3.12-venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

FROM ubuntu:24.10

ARG DEBIAN_FRONTEND=noninteractive

LABEL org.opencontainers.image.authors="Reliably <sylvain@reliably.com>"
LABEL org.opencontainers.image.vendor="Reliably"
LABEL org.opencontainers.image.url="https://reliably.com"
LABEL org.opencontainers.image.licenses="Apache-2.0"

RUN apt-get update && apt-get install -y apt-transport-https ca-certificates gnupg curl python3.12 && \
    # next three lines whould be enabled for gcloud support
    #curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    #echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    #apt-get update && apt-get install -y nano google-cloud-cli google-cloud-sdk-gke-gcloud-auth-plugin && \
    groupadd -g 1001 svc && useradd -m -u 1001 -g svc svc && \
    curl -Lo aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.6.29/aws-iam-authenticator_0.6.29_linux_amd64 && \
    chmod +x ./aws-iam-authenticator && \
    chown svc:svc ./aws-iam-authenticator && \
    mv ./aws-iam-authenticator /home/svc/aws-iam-authenticator && \
    curl -Lo oha https://github.com/hatoo/oha/releases/download/v1.6.0/oha-linux-amd64 && \
    chmod +x ./oha && \
    chown svc:svc ./oha && \
    mv ./oha /home/svc/oha && \
    apt-get remove --auto-remove -y golang-go curl gnupg apt-transport-https && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build-venv --chown=svc:svc /home/svc/.venv /home/svc/.venv
WORKDIR /home/svc
COPY --chown=svc:svc settings.yaml /home/svc/.chaostoolkit/settings.yaml
USER 1001

RUN mkdir -p /home/svc/bin && \
    mv ./aws-iam-authenticator /home/svc/bin/aws-iam-authenticator && \
    mv ./oha /home/svc/bin/oha

ENV PATH="$PATH:/home/svc/bin:/home/svc/.venv/bin"

ENTRYPOINT ["/home/svc/.venv/bin/reliably"]
CMD ["--help"]
