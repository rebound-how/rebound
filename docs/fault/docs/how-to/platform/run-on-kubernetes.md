# Introduce Network Fault Into an Application Running on Kubernetes

This guide will walk you through emulating faults into an application running
in a Kubernetes cluster.

## Run fault's proxy as a Deployment

-   [X] Deploy fault's demo application in the cluster

    This steps serves only the purpose of demonstrating fault's working
    in a Kubernetes cluster. You can safely ignore it if you have another
    application you wish to try.

    ```yaml title="fault-demo.yaml"
    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: fault-demo
      labels:
        app: fault-demo
    automountServiceAccountToken: false

    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: fault-demo
      labels:
        app: fault-demo
    spec:
      selector:
        app: fault-demo
      ports:
        - protocol: TCP
          port: 7070
          targetPort: 7070

    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: fault-demo
      labels:
        app: fault-demo
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: fault-demo
      template:
        metadata:
          labels:
            app: fault-demo
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          serviceAccountName: fault-demo
          securityContext:
            runAsUser: 65532
            runAsGroup: 65532
            fsGroup: 65532
          containers:
            - name: fault-demo
              image: rebound/fault:latest
              imagePullPolicy: Always
              tty: true
              args:
                - demo
                - run
                - "0.0.0.0"
                - "7070"
              ports:
                - containerPort: 7070
                  name: http
              securityContext:
                allowPrivilegeEscalation: false
                readOnlyRootFilesystem: true
                privileged: false
                capabilities:
                  drop:
                    - ALL
    ```

    Apply it as follows:

    ```bash
    kubectl apply -f fault-demo.yaml
    ```


-   [X] Deploy fault's proxy Kubernetes Resources

    Below is an example of running fault's proxy as a deployment, with a single
    replica.

    ```yaml title="fault-proxy.yaml"

    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: fault-proxy
      labels:
        app: fault-proxy
    automountServiceAccountToken: false

    ---
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: fault-proxy-config
      labels:
        app: fault-proxy
    data:
      fault_UPSTREAMS: "http://fault-demo:7070" # (1)!
      fault_WITH_LATENCY: "true" # (2)!
      fault_LATENCY_MEAN: "300"

    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: fault-proxy
      labels:
        app: fault-proxy
    spec:
      selector:
        app: fault-proxy
      ports:
        - protocol: TCP
          port: 3180
          targetPort: 3180

    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: fault-proxy
      labels:
        app: fault-proxy
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: fault-proxy
      template:
        metadata:
          labels:
            app: fault-proxy
          annotations:
            sidecar.istio.io/inject: "false"  # (3)!
        spec:
          serviceAccountName: fault-proxy
          securityContext:
            runAsUser: 65532
            runAsGroup: 65532
            fsGroup: 65532
          containers:
            - name: fault-proxy
              image: rebound/fault:latest
              imagePullPolicy: Always
              tty: true
              args:
                - --log-stdout
                - --log-level
                - debug
                - run
                - --no-ui  # (4)!
                - --proxy-address
                - "0.0.0.0:3180"  # (5)!
              ports:
                - containerPort: 3180
                  name: http
              envFrom:
                - configMapRef:
                    name: fault-proxy-config
              securityContext:
                allowPrivilegeEscalation: false
                readOnlyRootFilesystem: true
                privileged: false
                capabilities:
                  drop:
                    - ALL
    ```

    1. Comma-seperated list of hosts that the proxy is allowed to impact. We resolve to the demo application via its Kubernetes service name.
    2. Enable a latency fault, read the reference for more details on [environment variables](../../reference/environment-variables.md)
    3. Not really needed but in case you run in a Istio-aware environment, tell Istio not to add any sidecar to the proxy
    4. Disable the proxy terminal's UI which isn't really useful in this environment
    5. Make the fault proxy address listen on a non-loopback interface to be reachable

    Apply it as follows:

    ```bash
    kubectl apply -f fault-proxy.yaml
    ```

-   [X] Make a HTTP request to the demo service via the proxy

    First, start a throwaway {==curl==} pod. This will start a shell from it:

    ```bash
    kubectl run fault-test --rm -it --restart=Never --image=curlimages/curl -- sh
    ```

    Once the pod is started and its shell available, you can run the following
    command from it:

    ```bash
    curl -w "\nConnected IP: %{remote_ip}\nTotal time: %{time_total}s\n" -x http://fault-proxy:3180 http://fault-demo:7070
    <h1>Hello, World!</h1>
    Connected IP: 10.152.183.146
    Total time: 0.315056s
    ```

    This resolves both the proxy and the demo application from within the
    cluster, demonstrating a latency of roughly `315ms`.

    Once you exist the pod, its resources will be automatically released.

## Run fault's scenario as a Job

-   [X] Deploy fault's demo application in the cluster

    This steps serves only the purpose of demonstrating fault's working
    in a Kubernetes cluster. You can safely ignore it if you have another
    application you wish to try.

    ```yaml title="fault-demo.yaml"
    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: fault-demo
      labels:
        app: fault-demo
    automountServiceAccountToken: false

    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: fault-demo
      labels:
        app: fault-demo
    spec:
      selector:
        app: fault-demo
      ports:
        - protocol: TCP
          port: 7070
          targetPort: 7070

    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: fault-demo
      labels:
        app: fault-demo
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: fault-demo
      template:
        metadata:
          labels:
            app: fault-demo
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          serviceAccountName: fault-demo
          securityContext:
            runAsUser: 65532
            runAsGroup: 65532
            fsGroup: 65532
          containers:
            - name: fault-demo
              image: rebound/fault:latest
              imagePullPolicy: Always
              tty: true
              args:
                - demo
                - run
                - "0.0.0.0"
                - "7070"
              ports:
                - containerPort: 7070
                  name: http
              securityContext:
                allowPrivilegeEscalation: false
                readOnlyRootFilesystem: true
                privileged: false
                capabilities:
                  drop:
                    - ALL
    ```

    Apply it as follows:

    ```bash
    kubectl apply -f fault-demo.yaml
    ```

-   [X] Load a fault scenario as a Kubernetes ConfigMap

    Let's play a simple scenario with a single test call executed 4 times in
    total: 12 baseline call without latency applied and three calls with
    latencies gradually increasing by `30ms` steps.

    ```yaml title="scenario.yaml"
    ---
    title: "Latency Increase By 30ms Steps From Downstream"
    description: ""
    scenarios:
      - call:
          method: GET
          url: http://fault-demo:7070/ping
        context:
          upstreams:
            - https://postman-echo.com
          faults:
            - type: latency
              mean: 80
              stddev: 5
              direction: ingress
              side: client
          strategy:
            mode: Repeat
            step: 30
            count: 3
            add_baseline_call: true
        expect:
          status: 200
          response_time_under: 490
    ```

    To load this scenario as a configmap, run the next command:

    ```bash
    kubectl create configmap fault-scenario-file \
      --from-file=scenario.yaml=scenario.yaml
    ```

-   [X] Deploy fault's scenario as a Kubernetes Job

    Below is an example of running fault's scenarior as a job without retry.

    ```yaml title="fault-scenario.yaml"

    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: fault-scenario
      labels:
        app: fault-scenario
    automountServiceAccountToken: false

    ---
    apiVersion: batch/v1
    kind: Job
    metadata:
      name: fault-scenario
      labels:
        app: fault-scenario
    spec:
      backoffLimit: 0  # (1)!
      template:
        metadata:
          labels:
            app: fault-scenario
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          serviceAccountName: fault-scenario
          restartPolicy: Never
          securityContext:
            runAsUser: 65532
            runAsGroup: 65532
            fsGroup: 65532
          containers:
            - name: fault-scenario
              image: rebound/fault:latest
              imagePullPolicy: Always
              tty: true
              args:
                - scenario
                - run
                - --scenario
                - rebound/scenario.yaml
                - --result
                - result.json    # (2)!
                - --report
                - report.json    # (3)!
              volumeMounts:
              - name: fault-scenario-file
                mountPath: /home/nonroot/rebound/scenario.yaml    # (4)!
                readOnly: true
              securityContext:
                allowPrivilegeEscalation: false
                readOnlyRootFilesystem: false
                privileged: false
                capabilities:
                  drop:
                    - ALL
          volumes:
          - name: fault-scenario-file
            configMap:
              name: fault-scenario-file
              items:
                - key: scenario.yaml
                  path: scenario.yaml

    ```

    1. Do not restart the job if it failed
    2. Results contain the detailed events of the tests and all the applied faults
    3. A report is a rough analysis of the results made by fault
    4. Mount the scenario into the job's container

    Apply it as follows:

    ```bash
    kubectl apply -f fault-scenario.yaml
    ```
