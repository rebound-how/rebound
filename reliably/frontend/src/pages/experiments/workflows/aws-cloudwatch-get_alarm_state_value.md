---
name: get_alarm_state_value
target: AWS
category: CloudWatch
type: probe
module: chaosaws.cloudwatch.probes
description: Return the state value of an alarm
layout: src/layouts/ActivityLayout.astro
---

|            |                            |
| ---------- | -------------------------- |
| **Type**   | probe                      |
| **Module** | chaosaws.cloudwatch.probes |
| **Name**   | get_alarm_state_value      |
| **Return** | string                     |

The possible alarm state values are described in the documentation
[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.describe_alarms](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.describe_alarms)

**Usage**

JSON

```json
{
  "name": "get-alarm-state-value",
  "type": "probe",
  "provider": {
    "type": "python",
    "module": "chaosaws.cloudwatch.probes",
    "func": "get_alarm_state_value",
    "arguments": {
      "alarm_name": ""
    }
  }
}
```

YAML

```yaml
name: get-alarm-state-value
provider:
  arguments:
    alarm_name: ""
  func: get_alarm_state_value
  module: chaosaws.cloudwatch.probes
  type: python
type: probe
```

**Arguments**

| Name           | Type   | Default | Required | Title       | Description                                 |
| -------------- | ------ | ------- | -------- | ----------- | ------------------------------------------- |
| **alarm_name** | string |         | Yes      | Alarma Name | Name of the alarm to retrieve the state for |

**Signature**

```python
def get_alarm_state_value(alarm_name: str,
                          configuration: Dict[str, Dict[str, str]] = None,
                          secrets: Dict[str, Dict[str, str]] = None) -> str:
    pass

```
