# Fault Injection Into Kubernetes

This guide will walk you through injecting network faults into Kubernetes
resources such as a service and its pods. You will not need to change any
code.

While you may manually 
[deploy fault into Kubernetes](../platform/run-on-kubernetes.md), {==fault==}
comes with a friendly automated fault injection command to simplify the process.

??? abstract "Prerequisites"

    -   [X] Install fault

        If you haven’t installed fault yet, follow the
        [installation instructions](../install.md).

## Inject Latency Into a Kubernetes Service/Pod

-   [X] Create a basic nginx pod and its service

    ```yaml title="nginx.yaml"
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx
      labels:
        app: nginx
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: nginx
      template:
        metadata:
          labels:
            app: nginx
        spec:
          containers:
          - name: nginx
            image: nginx
            ports:
          - containerPort: 80
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: nginx-service
    spec:
      selector:
        app: nginx
      type: NodePort
      ports:
      - protocol: TCP
        port: 80
        targetPort: 80
    ```

    Let the API server create the resources:

    ```bash
    kubectl apply -f nginx.yaml
    ```

-   [X] Grab the service's IP

    ```bash
    export NGINX_IP=$(kubectl get -o template service/nginx-service --template='{{.spec.clusterIP}}')
    ```

-   [X] Make a first request

    This first request establishes nginx is running:

    ```bash
    curl -w "Connected IP: %{remote_ip}\nTotal time: %{time_total}s\n" http://$NGINX_IP
    Connected IP: 10.43.30.208
    Total time: 0.000680s
    ```

-   [X] Inject {==fault==} into the nginx service

    ```bash
    fault inject kubernetes --ns default --service nginx-service --with-latency --latency-mean 300
    ```

    When you do not explicitly set the service, fault lets you pick up one
    from the CLI:

    ```bash
    fault inject kubernetes --with-latency --latency-mean 300
    ? Service:  
    grafana
    kubernetes
    > nginx-service
    [↑↓ to move, enter to select, type to filter]
    ```

-   [X] Make a new request

    This second request establishes nginx is running with a latency of 300ms

    ```bash
    curl -w "Connected IP: %{remote_ip}\nTotal time: %{time_total}s\n" http://$NGINX_IP
    Connected IP: 10.43.30.208
    Total time: 0.303097s
    ```

    The nginx response time is now greater from the client's perspective.
