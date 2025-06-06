# Injecting <span class="f">fault</span> Into Your Platform

This page references the information about how <span class="f">fault</span> injects its resources
into the platform it supports.

## Kubernetes

<span class="f">fault</span> may run on Kubernetes by creating the following resources:

* a job (CronJob are not supported yet)
* a service
* a dedicated service account
* a config map that holds the environment variables used to configure the proxy

```mermaid
sequenceDiagram
  autonumber
  fault (local)->>Service Account: Create
  fault (local)->>Config Map: Create with fault's proxy environment variables
  fault (local)->>Target Service: Fetch target service's selectors and ports
  fault (local)->>Target Service: Replace target service selectors to match new fault's pod
  fault (local)->>fault Service: Create new service with target service's selectors and ports but listening on port 3180
  fault (local)->>Job: Create to manage fault's pod, with proxy sending traffic to new service's address
  Job->>fault Pod: Schedule fault's pod with config map attached
  fault Pod->>Service Account: Uses
  fault Pod->>Config Map: Loads
  Target Service->>fault Pod: Matches
  loop fault proxy
      fault (local)->>Target Service: Starts scenario
      Target Service->>fault Pod: Route traffic via fault
      loop fault injection
        fault Pod->>fault Pod: Apply faults
      end
      fault Pod->>fault Service: Forwards
      fault Service->>Target Pods: forward traffic to final endpoints
      Target Pods->>fault (local): Sends response back after faults applied
  end
```

!!! note

    Once a scenario completes, <span class="f">fault</span> rollbacks the resources to their
    original state.

<span class="f">fault</span> uses the default Kubernetes authentication mechanism to connect
to the cluster: `~/.kube/config`, `KUBECONFIG`...

The authorizations for that user needs at least the following roles:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: fault
rules:
  # ServiceAccounts (create/delete)
  - apiGroups: [""]
    resources:
      - serviceaccounts
    verbs:
      - create
      - delete
      - get

  # ConfigMaps (create/delete/get)
  - apiGroups: [""]
    resources:
      - configmaps
    verbs:
      - create
      - delete
      - get

  # Services (get/patch/delete)
  - apiGroups: [""]
    resources:
      - services
    verbs:
      - get
      - patch
      - delete

  # Jobs (create/delete/get/list)
  - apiGroups:
      - batch
    resources:
      - jobs
    verbs:
      - create
      - delete
      - get
      - list

  # Pods (list/get)
  - apiGroups: [""]
    resources:
      - pods
    verbs:
      - get
      - list
      - watch
```
