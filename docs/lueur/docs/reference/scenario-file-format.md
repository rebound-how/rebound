# Scenario File Format

## Scenario Overview

A Lueur scenario file is a structured document that defines a suite of tests designed to simulate adverse network conditions and assess your application's resilience. Rather than being an arbitrary collection of tests, each scenario file follows a consistent structure that ensures clarity, repeatability, and ease of automation.

At the top level, a scenario file contains metadata that provides context for the entire test suite. This is followed by a collection of individual test cases, each of which is known as a scenario item.

Each scenario item is composed of three primary components:

**Call:**  
This section describes the HTTP request that will be executed during the test. It specifies essential details such as the HTTP method (for example, GET or POST), the target URL, and any headers or body content that are required. Essentially, it outlines the action that triggers the fault injection.

**Context:**  
The context defines the environment in which the test runs. It lists the upstream endpoints that will be affected by fault injection and specifies the type of faults to simulate. Faults can include network latency, packet loss, bandwidth restrictions, jitter, DNS anomalies, or HTTP errors. Additionally, an optional strategy can be included to repeat or vary the test conditions systematically.

**Expectation:**  
This component sets the criteria for a successful test. It defines what outcomes are acceptable by specifying expected HTTP status codes and performance metrics like maximum response times. By clearly stating these expectations, the scenario file provides a benchmark against which the test results can be measured.

The structured approach of a scenario file not only helps maintain consistency across tests but also simplifies troubleshooting and iterative refinement. For detailed information on individual fault parameters, refer to the relevant definitions. This ensures that each test case is both precise and aligned with your reliability objectives.

## Example

The following example demonstrates a scenario file with many tests and their
expectations. It targets the lueur demo application.

```yaml title="scenario.yaml"
---
title: "Latency Increase By 30ms Steps From Downstream"
description: ""
scenarios:
  - call:
      method: GET
      url: http://localhost:7070/ping
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

---
title: "Within Allowed Latency While Bandwidth At 5 bytes/second"
description: ""
scenarios:
  - call:
      method: POST
      url: http://localhost:7070/uppercase
      headers:
        "Content-Type": "application/json"
      body: '{"content": "hello"}'
    context:
      upstreams:
        - http://localhost:7070
      faults:
        - type: bandwidth
          rate: 5
          unit: Bps
          direction: ingress
    expect:
      response_time_under: 8

---
title: "Circuit Breaker Takes Care of 404"
description: ""
scenarios:
  - call:
      method: GET
      url: http://localhost:7070/ping/myself
    context:
      upstreams:
        - http://127.0.0.1:7070
      faults:
        - type: httperror
          status_code: 404
          probability: 0.9
    expect:
      status: 200

---
title: "Packet loss has no impact on service performance"
description: ""
scenarios:
  - call:
      method: GET
      url: http://localhost:7070/ping
    context:
      upstreams:
        - https://postman-echo.com
      faults:
        - type: packetloss
          direction: ingress
          side: client
    expect:
      status: 200
```

You can run this scenario file agains the demo server:

```bash
lueur demo run
```

To execute the scenario file, run the following command:

```bash
lueur scenario run --scenario scenario.yaml
```

## JSON Schema

Below is the full JSON schema of the scenario file:

```json title="scenario-schema.json"
{
  "$ref": "#/$defs/Scenario",
  "$defs": {
    "Scenario": {
      "title": "Scenario",
      "type": "object",
      "properties": {
        "title": {
          "type": "string"
        },
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ]
        },
        "scenarios": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/ScenarioItem"
          }
        }
      },
      "required": [
        "title",
        "description",
        "scenarios"
      ]
    },
    "ScenarioItem": {
      "title": "ScenarioItem",
      "type": "object",
      "properties": {
        "call": {
          "$ref": "#/$defs/ScenarioItemCall"
        },
        "context": {
          "$ref": "#/$defs/ScenarioItemContext"
        },
        "expect": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "$ref": "#/$defs/ScenarioItemExpectation"
            }
          ]
        }
      },
      "required": [
        "call",
        "context",
        "expect"
      ]
    },
    "ScenarioItemCall": {
      "title": "ScenarioItemCall",
      "type": "object",
      "properties": {
        "method": {
          "type": "string"
        },
        "url": {
          "type": "string"
        },
        "headers": {
          "anyOf": [
            {
              "type": "object",
              "additionalProperties": {
                "type": "string"
              }
            },
            {
              "type": "null"
            }
          ]
        },
        "body": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ]
        }
      },
      "required": [
        "method",
        "url",
        "headers",
        "body"
      ]
    },
    "ScenarioItemContext": {
      "title": "ScenarioItemContext",
      "type": "object",
      "properties": {
        "upstreams": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "faults": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/FaultConfiguration"
          }
        },
        "strategy": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "$ref": "#/$defs/ScenarioItemCallStrategy"
            }
          ]
        }
      },
      "required": [
        "upstreams",
        "faults",
        "strategy"
      ]
    },
    "FaultConfiguration": {
      "title": "FaultConfiguration",
      "type": "object",
      "properties": {
        "Latency": {
          "$ref": "#/$defs/Latency"
        },
        "PacketLoss": {
          "$ref": "#/$defs/PacketLoss"
        },
        "Bandwidth": {
          "$ref": "#/$defs/Bandwidth"
        },
        "Jitter": {
          "$ref": "#/$defs/Jitter"
        },
        "Dns": {
          "$ref": "#/$defs/Dns"
        },
        "HttpError": {
          "$ref": "#/$defs/HttpError"
        }
      },
      "required": [
        "Latency",
        "PacketLoss",
        "Bandwidth",
        "Jitter",
        "Dns",
        "HttpError"
      ]
    },
    "Latency": {
      "title": "Latency",
      "type": "object",
      "properties": {
        "distribution": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ]
        },
        "global_": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ]
        },
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ]
        },
        "mean": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "stddev": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "min": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "max": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "shape": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "scale": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "direction": {
          "anyOf": [
            {
              "enum": [
                "egress",
                "ingress"
              ]
            },
            {
              "type": "null"
            }
          ]
        }
      },
      "required": [
        "distribution",
        "global_",
        "side",
        "mean",
        "stddev",
        "min",
        "max",
        "shape",
        "scale",
        "direction"
      ]
    },
    "PacketLoss": {
      "title": "PacketLoss",
      "type": "object",
      "properties": {
        "direction": {
          "enum": [
            "egress",
            "ingress"
          ]
        },
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ]
        }
      },
      "required": [
        "direction",
        "side"
      ]
    },
    "Bandwidth": {
      "title": "Bandwidth",
      "type": "object",
      "properties": {
        "rate": {
          "type": "integer",
          "minimum": 0,
          "default": 1000
        },
        "unit": {
          "enum": [
            "bps",
            "gbps",
            "kbps",
            "mbps"
          ],
          "default": "bps"
        },
        "direction": {
          "enum": [
            "egress",
            "ingress"
          ],
          "default": "server"
        },
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "server"
        }
      },
      "required": []
    },
    "Jitter": {
      "title": "Jitter",
      "type": "object",
      "properties": {
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ]
        },
        "amplitude": {
          "type": "number",
          "minimum": 0.0,
          "default": 20.0
        },
        "frequency": {
          "type": "number",
          "minimum": 0.0,
          "default": 5.0
        }
      },
      "required": [
        "side"
      ]
    },
    "Dns": {
      "title": "Dns",
      "type": "object",
      "properties": {
        "rate": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.5
        }
      },
      "required": []
    },
    "HttpError": {
      "title": "HttpError",
      "type": "object",
      "properties": {
        "body": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ]
        },
        "status_code": {
          "$ref": "#/$defs/HTTPStatus",
          "default": 500
        },
        "probability": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 1.0
        }
      },
      "required": [
        "body"
      ]
    },
    "HTTPStatus": {
      "title": "HTTPStatus",
      "description": "HTTP status codes and reason phrases\n\n    Status codes from the following RFCs are all observed:\n\n        * RFC 7231: Hypertext Transfer Protocol (HTTP/1.1), obsoletes 2616\n        * RFC 6585: Additional HTTP Status Codes\n        * RFC 3229: Delta encoding in HTTP\n        * RFC 4918: HTTP Extensions for WebDAV, obsoletes 2518\n        * RFC 5842: Binding Extensions to WebDAV\n        * RFC 7238: Permanent Redirect\n        * RFC 2295: Transparent Content Negotiation in HTTP\n        * RFC 2774: An HTTP Extension Framework\n        * RFC 7725: An HTTP Status Code to Report Legal Obstacles\n        * RFC 7540: Hypertext Transfer Protocol Version 2 (HTTP/2)\n        * RFC 2324: Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0)\n        * RFC 8297: An HTTP Status Code for Indicating Hints\n        * RFC 8470: Using Early Data in HTTP",
      "enum": [
        100,
        101,
        102,
        103,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        207,
        208,
        226,
        300,
        301,
        302,
        303,
        304,
        305,
        307,
        308,
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        416,
        417,
        418,
        421,
        422,
        423,
        424,
        425,
        426,
        428,
        429,
        431,
        451,
        500,
        501,
        502,
        503,
        504,
        505,
        506,
        507,
        508,
        510,
        511
      ]
    },
    "ScenarioItemCallStrategy": {
      "title": "ScenarioItemCallStrategy",
      "type": "object",
      "properties": {
        "mode": {
          "anyOf": [
            {
              "$ref": "#/$defs/ScenarioItemCallStrategyMode"
            },
            {
              "type": "null"
            }
          ]
        },
        "failfast": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ]
        },
        "step": {
          "type": "number",
          "minimum": 0.0
        },
        "wait": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "add_baseline_call": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ]
        },
        "count": {
          "type": "integer",
          "minimum": 0,
          "default": 0
        }
      },
      "required": [
        "mode",
        "failfast",
        "step",
        "wait",
        "add_baseline_call"
      ]
    },
    "ScenarioItemCallStrategyMode": {
      "title": "ScenarioItemCallStrategyMode",
      "enum": [
        1
      ]
    },
    "ScenarioItemExpectation": {
      "title": "ScenarioItemExpectation",
      "type": "object",
      "properties": {
        "status": {
          "anyOf": [
            {
              "type": "integer",
              "minimum": 0
            },
            {
              "type": "null"
            }
          ]
        },
        "response_time_under": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        }
      },
      "required": [
        "status",
        "response_time_under"
      ]
    }
  }
}
```
