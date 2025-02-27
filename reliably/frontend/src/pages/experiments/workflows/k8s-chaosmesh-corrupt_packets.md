---
name: corrupt_packets
target: Kubernetes
category: Network
type: action
module: chaosk8s.chaosmesh.network.actions
description: Corrupt packets on a Pod network link
layout: src/layouts/ActivityLayout.astro
related: |
    - method:reliably-pauses-pause_execution
    - rollbacks:k8s-chaosmesh-delete_network_fault
---

|            |                       |
| ---------- | --------------------- |
| **Type**   | action                |
| **Module** | chaosk8s.chaosmesh.network.actions |
| **Name**   | corrupt_packets           |
| **Return** | mapping                  |

**Usage**

JSON

```json
{
  "name": "corrupt-packets",
  "type": "action",
  "provider": {
    "type": "python",
    "module": "chaosk8s.chaosmesh.network.actions",
    "func": "corrupt_packets",
    "arguments": {
      "name": ""
    }
  }
}
```

YAML

```yaml
name: corrupt-packets
provider:
  arguments:
    name: ''
  func: corrupt_packets
  module: chaosk8s.chaosmesh.network.actions
  type: python
type: action
```

**Arguments**

| Name               | Type   | Default | Required | Title          | Description                                    |
| ------------------ | ------ | ------- | -------- | -------------- | ---------------------------------------------- |
| **name**           | string |         | Yes       | Name           | A unique name to identify this particular fault  |
| **direction** | string |  to   | No       | Direction | Which direction to apply the corruption:  `from`, `to` or `both`    |
| **corrupt** | string |     | Yes       | Probability | Packet corruption probability between 0 and 100    |
| **correlation** | string |     | No       | Correlation | How much correlation compared to the previous corruption. Between 0 and 100    |
| **ns** | string | default    | No       | Namespace | Namespace where to apply the fault      |
| **namespaces_selectors** | string |  | No       | Namespaces Selectors | Comma-separated list of namespaces to scope the fault to      |
| **label_selectors** | string |  | No       | Label Selectors | Comma-separated list of key=value pairs to scope the fault to      |
| **annotations_selectors** | string |  | No       | Annotation Selectors | Comma-separated list of key=value pairs to scope the fault to      |
| **mode** | string | one    | No       | Mode | Mode of fault injection: `one`, `all`, `fixed`, `fixed-percent`, `random-max-percent`     |
| **mode_value** | string |     | No       | Mode Value | Value depending on the mode above    |
| **external_targets** | string |     | No       | External Targets | IPv4 or domain targetted by the fault when direction is set to "to"   |
| **target_namespaces_selectors** | string |  | No       | Target Namespaces Selectors | Comma-separated list of namespaces to scope the fault to the right target pod. Only works when direction is set to `both` or `from`     |
| **target_label_selectors** | string |  | No       | Target Label Selectors | Comma-separated list of key=value pairs to scope the network fault to the right target pod. Only works when direction is set to `both` or `from`     |
| **target_annotations_selectors** | string |  | No       | Target Annotation Selectors | Comma-separated list of key=value pairs to scope the fault to the right target pod. Only works when direction is set to `both` or `from`      |
| **target_mode** | string | one    | No       | Target Mode | Target Mode of fault injection: `one`, `all`, `fixed`, `fixed-percent`, `random-max-percent`     |
| **target_mode_value** | string |     | No       | Target Mode Value | Value depending on the mode above    |

This action relies on [Chaos Mesh](https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/)
to perform the fault. Make sure to install it before hand.

**Signature**

```python
def corrupt_packets(
        name: str,
        ns: str = 'default',
        namespaces_selectors: Optional[str] = None,
        label_selectors: Optional[str] = None,
        annotations_selectors: Optional[str] = None,
        mode: str = 'one',
        mode_value: Optional[str] = None,
        direction: str = 'to',
        corrupt: Optional[str] = None,
        correlation: Optional[str] = None,
        external_targets: Union[str, List[str], NoneType] = None,
        target_mode: Optional[str] = 'one',
        target_mode_value: Optional[str] = None,
        target_namespaces_selectors: Union[str, List[str], NoneType] = None,
        target_label_selectors: Union[str, Dict[str, Any], NoneType] = None,
        target_annotations_selectors: Union[str, Dict[str, Any],
                                            NoneType] = None,
        secrets: Dict[str, Dict[str, str]] = None) -> Dict[str, Any]:
    pass
```
