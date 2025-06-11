# Fault Injection Into Google Cloud Platform

This guide will walk you through injecting network faults into Google Cloud
Platform Cloud Run. You will not need to change any code.

???+ abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../install.md).

## Inject Latency Into a Cloud Run Service

-   [X] Create a basic Cloud Run service

    You may want to follow the official [GCP documentation](https://cloud.google.com/run/docs/quickstarts/deploy-container) to deploy a sample  service.

-   [X] Upload the <span class="f">fault</span> container image to a GCP artifactory

    Cloud Run will expect the <span class="f">fault</span> image to be pulled
    from an artifactory in the same region (or a global one). So this means,
    you must upload the official <span class="f">fault</span> image to your
    own artifactory repository.

    Follow the [official documentation](https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling#pushing) to upload the [fault image](https://github.com/rebound-how/rebound/pkgs/container/fault)

    Something along the lines:

    ```bash
    # locally download the official fault image
    docker pull ghcr.io/rebound-how/fault:<version>
    
    # tag it to match your nex GCP Artifactory repository
    docker tag ghcr.io/rebound-how/fault:<version> <region>-docker.pkg.dev/<project>/<repository>/fault:<version>

    # push it to the repository
    docker push <region>-docker.pkg.dev/<project>/<repository>/fault:<version>
    ```

-   [X] Inject <span class="f">fault</span> into the nginx service

    The following injects a `800ms` into the service response time.

    ```bash
    fault inject gcp \
        --project <project> \  # (1)!
        --region <region>  \  # (2)!
        --service <service> \  # (3)!
        --image <image> \  # (4)!
        --duration 30s \  # (5)!
        --with-latency --latency-mean 800
    ```

    1. The GCP project where your CloudRun service is running
    2. The GCP region where your CloudRun service is running
    3. The GCP CloudRun service name
    4. The <span class="f">fault</span> container image full url
    5. Optional [duration](https://docs.rs/parse_duration/latest/parse_duration/#syntax) after which the injection rollbacks. If unset, the user input is expected

    When you do not explicitly set the service, <span class="f">fault</span>
    lets you pick up one from the CLI:

    ```bash
    fault inject gcp \
        --project <project> \
        --region <region>  \
        --image <image> \
        --with-latency --latency-mean 800
    ? Service:  
    > hello
    [↑↓ to move, enter to select, type to filter]
    ```

    Once started, a new revision of the service will be deployed with the
    <span class="f">fault</span> process running as a sidecar container
    of the service's main container. It will expose a port to receive traffic
    and route it to the application.
