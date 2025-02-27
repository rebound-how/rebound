import { test } from "uvu";
import * as assert from "uvu/assert";
import { cloneDeep } from "lodash-es";

import { checkExperiment } from "../src/utils/experiments";

let fullExperiment: object = {
  title: "Are our users impacted by the loss of a function?",
  description:
    "While users query the Astre function, they should not be impacted if one instance goes down.",
  contributions: {
    reliability: "high",
    availability: "high",
    performance: "medium",
    security: "none",
  },
  tags: ["kubernetes", "openfaas", "cloudnative"],
  configuration: {
    prometheus_base_url: "http://demo.foo.bar",
  },
  secrets: {
    global: {
      auth: "Basic XYZ",
    },
  },
  controls: [
    {
      name: "tracing",
      provider: {
        type: "python",
        module: "chaostracing.control",
      },
    },
  ],
  "steady-state-hypothesis": {
    title: "Function is available",
    probes: [
      {
        type: "probe",
        name: "function-must-exist",
        tolerance: 200,
        provider: {
          type: "http",
          secrets: ["global"],
          url: "http://demo.foo.bar/system/function/astre",
          headers: {
            Authorization: "${auth}",
          },
        },
      },
      {
        type: "probe",
        name: "function-must-respond",
        tolerance: 200,
        provider: {
          type: "http",
          timeout: [3, 5],
          secrets: ["global"],
          url: "http://demo.foo.bar/function/astre",
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "${auth}",
          },
          arguments: {
            city: "Paris",
          },
        },
      },
    ],
  },
  method: [
    {
      type: "action",
      name: "simulate-user-traffic",
      background: true,
      provider: {
        type: "process",
        path: "vegeta",
        arguments:
          "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
      },
    },
    {
      type: "action",
      name: "terminate-one-function",
      provider: {
        type: "python",
        module: "chaosk8s.pod.actions",
        func: "terminate_pods",
        arguments: {
          ns: "openfaas-fn",
          label_selector: "faas_function=astre",
          rand: true,
        },
      },
      pauses: {
        before: 5,
      },
    },
    {
      type: "probe",
      name: "fetch-openfaas-gateway-logs",
      provider: {
        type: "python",
        module: "chaosk8s.pod.probes",
        func: "read_pod_logs",
        arguments: {
          label_selector: "app=gateway",
          last: "35s",
          ns: "openfaas",
        },
      },
    },
    {
      type: "probe",
      name: "query-total-function-invocation",
      provider: {
        type: "python",
        module: "chaosprometheus.probes",
        func: "query_interval",
        secrets: ["global"],
        arguments: {
          query: "gateway_function_invocation_total{function_name='astre'}",
          start: "1 minute ago",
          end: "now",
          step: 1,
        },
      },
    },
  ],
  rollbacks: [],
};

// test("check complete experiment", () => {
//   const exp: object = fullExperiment;
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with no title", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   delete exp.title;
//   const expected: string = "<code>title</code> property is missing or invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with wrong title type", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.title = 1234;
//   const expected: string = "<code>title</code> property is missing or invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with no description", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   delete exp.description;
//   const expected: string =
//     "<code>description</code> property is missing or invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with wrong description type", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.description = 1234;
//   const expected: string =
//     "<code>description</code> property is missing or invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("experiment without contributions is valid", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   delete exp.contributions;
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with invalid contributions object", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.contributions = "security";
//   const expected: string = "<code>contributions</code> property is invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with invalid contribution property", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.contributions.security = true;
//   const expected: string = "<code>contributions</code> property is invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("experiment without tags is valid", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   delete exp.tags;
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with invalid tags value", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.tags = "kubernetes, openfaas, cloudnative";
//   const expected: string = "<code>tags</code> property is invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with invalid tag", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.tags.push(123);
//   const expected: string = "<code>tags</code> property is invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("experiment without configuration is valid", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   delete exp.configuration;
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("experiment with a configuration entry being an number is valid", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.configuration = {
//     // reliably_latency: 0.2,
//     reliably_url: "https://reliably.com",
//   };
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("experiment with a configuration entry being an object is valid", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.configuration.deployment = {
//     provider: "github",
//     url: "https://github.com/reliably/reliably",
//   };
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with invalid configuration", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.configuration = "http://demo.foo.bar";
//   const expected: string = "<code>configuration</code> property is invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("experiment without secrets is valid", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   delete exp.secrets;
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with invalid secrets", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.secrets = "password";
//   const expected: string = "<code>secrets</code> property is invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with inline secret with multiple keys", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.secrets.global.password = "azerty";
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with invalid inline secret", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.secrets.password = "azerty";
//   const expected: string = "<code>secrets</code> property is invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with numeric inline secret", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.secrets.password = 123;
//   const expected: string = "<code>secrets</code> property is invalid";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

// test("check experiment with env secrets", () => {
//   const exp: any = cloneDeep(fullExperiment);
//   exp.secrets.kubernetes = {
//     token: {
//       type: "env",
//       key: "KUBERNETES_TOKEN",
//     },
//     password: {
//       type: "env",
//       key: "KUBERNETES_PWD",
//     },
//   };
//   const expected: string = "";
//   const x = checkExperiment(exp);
//   assert.is(x, expected);
// });

test("check experiment with invalid (numeric) env secrets", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.secrets.kubernetes = {
    token: {
      type: "env",
      key: 123,
    },
  };
  const expected: string = "<code>secrets</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with vault secrets", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.secrets.kubernetes = {
    token: {
      type: "vault",
      path: "secrets/something",
    },
    password: {
      type: "vault",
      path: "secrets/password",
    },
  };
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with invalid vault secrets", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.secrets.kubernetes = {
    token: {
      type: "vault",
      key: "/secrets/something",
    },
  };
  const expected: string = "<code>secrets</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with invalid secret type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.secrets.kubernetes = {
    token: {
      type: "password",
      key: "azerty",
    },
  };
  const expected: string = "<code>secrets</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with extensions", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.extensions = [
    {
      name: "A",
      data: "a",
    },
    {
      name: "B",
      data: "b",
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with wrongly formed extensions object", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.extensions = {
    name: "A",
    data: "a",
  };
  const expected: string = "<code>extensions</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with wrongly formed extension", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.extensions = [
    {
      provider: "A",
      data: "a",
    },
    {
      name: "B",
      data: "b",
    },
  ];
  const expected: string = "<code>extensions</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with full-fledged control", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      automatic: false,
      scope: "before",
      provider: {
        type: "python",
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with several controls", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      provider: {
        type: "python",
        module: "chaostracing.control",
      },
    },
    {
      name: "observability",
      provider: {
        type: "python",
        module: "chaosobs.control",
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with invalid control", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      provider: {
        type: "python",
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment whose control has no name", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      automatic: "false",
      provider: {
        type: "python",
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment whose control has an invalid name", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: 200,
      automatic: "false",
      provider: {
        type: "python",
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with invalid control scope", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      scope: "during",
      provider: {
        type: "python",
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with invalid control automatic property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      automatic: "false",
      provider: {
        type: "python",
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with invalid controls property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = {
    name: "tracing",
    automatic: "false",
    provider: {
      type: "python",
      module: "chaostracing.control",
    },
  };
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment whose control has no provider", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      automatic: false,
      scope: "before",
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment whose controls provider has no type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      scope: "during",
      provider: {
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment whose controls provider has an incorrect type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      scope: "during",
      provider: {
        type: "process",
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment whose controls provider has an invalid type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      scope: "during",
      provider: {
        type: false,
        module: "chaostracing.control",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment whose controls provider has no module", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      scope: "during",
      provider: {
        type: "python",
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment whose controls provider has an invalid module", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.controls = [
    {
      name: "tracing",
      scope: "during",
      provider: {
        type: "python",
        module: false,
      },
    },
  ];
  const expected: string = "<code>controls</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH is an array", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"] = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: 200,
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
    {
      type: "probe",
      name: "function-must-respond",
      tolerance: 200,
      provider: {
        type: "http",
        timeout: [3, 5],
        secrets: ["global"],
        url: "http://demo.foo.bar/function/astre",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "${auth}",
        },
        arguments: {
          city: "Paris",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH has no title", () => {
  const exp: any = cloneDeep(fullExperiment);
  delete exp["steady-state-hypothesis"].title;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH has the wrong title type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].title = 1234;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH has no probes property", () => {
  const exp: any = cloneDeep(fullExperiment);
  delete exp["steady-state-hypothesis"].probes;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH probes property is empty", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH probes property is null", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = null;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH probes property is wrongly formed", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = {
    type: "probe",
    name: "function-must-exist",
    tolerance: 200,
    provider: {
      type: "http",
      secrets: ["global"],
      url: "http://demo.foo.bar/system/function/astre",
      headers: {
        Authorization: "${auth}",
      },
    },
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH probes property has invalid background property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: [4, "k8s", false],
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
      background: "true",
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where SSH probes property has invalid controls", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: [4, "k8s", false],
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
      controls: [
        {
          provider: {
            type: "python",
            module: "chaostracing.control",
          },
        },
      ],
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has no type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      name: "function-must-exist",
      tolerance: 200,
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an incorrect type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "action",
      name: "function-must-exist",
      tolerance: 200,
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has no name", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      tolerance: 200,
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an incorrect name", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: 1234,
      tolerance: 200,
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has no tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an invalid tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: null,
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a tolerance array", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: [4, "k8s", false],
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an empty tolerance array", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: [],
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an tolerance array with invalid values", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: [5, 7, [6, 8]],
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a regex tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "regex",
        pattern: "[0-9]{3}",
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a regex tolerance with a non-default target", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "regex",
        pattern: "[0-9]{3}",
        target: "stdout",
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an invalid regex tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "regex",
        pattern: "[",
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a regex tolerance with invalid property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "regex",
        path: "[0-9]{3}",
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a jsonpath tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "jsonpath",
        path: "foo[*].baz",
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a jsonpath tolerance with an invalid expect property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "jsonpath",
        path: "foo[*].baz",
        expect: {
          result: "123",
          fail: false,
        },
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a jsonpath tolerance with an invalid property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "jsonpath",
        pattern: "foo[*].baz",
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a range tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "range",
        range: [4, 9],
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a 3-value range tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "range",
        range: [4, 9, 17],
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a 1-value range tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "range",
        range: [4],
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an invalid range tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "range",
        range: [4, 9, false],
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an invalid range tolerance format", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "range",
        range: { low: 4, high: 9 },
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a range tolerance with invalid property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "range",
        path: [4, 9],
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a probe tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "probe",
        name: "function-must-exist",
        provider: {
          type: "http",
          secrets: ["global"],
          url: "http://demo.foo.bar/system/function/astre",
          headers: {
            Authorization: "${auth}",
          },
        },
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an invalid probe tolerance", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "probe",
        provider: {
          type: "http",
          secrets: ["global"],
          url: "http://demo.foo.bar/system/function/astre",
          headers: {
            Authorization: "${auth}",
          },
        },
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a probe tolerance with an invalid secrets property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "probe",
        name: "function-must-exist",
        provider: {
          type: "http",
          secrets: "global",
          url: "http://demo.foo.bar/system/function/astre",
          headers: {
            Authorization: "${auth}",
          },
        },
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a tolerance which is an object of invalid type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes = [
    {
      type: "probe",
      name: "function-must-exist",
      tolerance: {
        type: "ragne",
        path: [4, 9],
      },
      provider: {
        type: "http",
        secrets: ["global"],
        url: "http://demo.foo.bar/system/function/astre",
        headers: {
          Authorization: "${auth}",
        },
      },
    },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has no provider", () => {
  const exp: any = cloneDeep(fullExperiment);
  delete exp["steady-state-hypothesis"].probes[0].provider;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has an invalid provider", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = "measure_response_time";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's provider has no type", () => {
  const exp: any = cloneDeep(fullExperiment);
  delete exp["steady-state-hypothesis"].probes[0].provider.type;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's provider is of unknown type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider.type = "pythno";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider has no URL", () => {
  const exp: any = cloneDeep(fullExperiment);
  delete exp["steady-state-hypothesis"].probes[0].provider.url;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider URL is not a string", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider.url = null;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider URL is an empty string", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider.url = "";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider method is not a string", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider.method = null;
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider method is an empty string", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider.method = "";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider has an invalid method", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider.method = "POTS";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider headers property is not an object", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider.headers = [
    { "Content-Type": "application/json" },
    { Authorization: "${auth}" },
  ];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider headers property is not an object nor array", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider.headers =
    "Content-Type: application/json";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider expected_status is not a number", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider["expected_status"] = "200";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider arguments property is not an object", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider.arguments = "city=Paris";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider timeout property is a number", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider.timeout = 5;
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider timeout property is a string", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider.timeout = "5";
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider timeout property is an array of 3 numbers", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider.timeout = [3, 5, 8];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider timeout property is an invalid array", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider.timeout = [3, false];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's HTTP provider has invalid secrets", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider.secrets = ["global", 3];
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a python provider", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "python",
    module: "chaosreliably.activities.http.probes",
    func: "measure_response_time",
    arguments: {
      url: "${reliably_url}",
    },
  };
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a python provider without module", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider = {
    type: "python",
    func: "measure_response_time",
    arguments: {
      url: "${reliably_url}",
    },
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a python provider with an invalid module", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider = {
    type: "python",
    module: 200,
    func: "measure_response_time",
    arguments: {
      url: "${reliably_url}",
    },
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a python provider without func", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider = {
    type: "python",
    module: "chaosreliably.activities.http.probes",
    arguments: {
      url: "${reliably_url}",
    },
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a python provider with an invalid func", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider = {
    type: "python",
    module: "chaosreliably.activities.http.probes",
    func: 200,
    arguments: {
      url: "${reliably_url}",
    },
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a python provider where arguments are not an object", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[1].provider = {
    type: "python",
    module: "chaosreliably.activities.http.probes",
    func: "measure_response_time",
    arguments: "${reliably_url}",
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a python provider with invalid secrets", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "python",
    module: "chaosreliably.activities.http.probes",
    func: "measure_response_time",
    arguments: {
      url: "${reliably_url}",
    },
    secrets: ["global", false],
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a python provider with invalid secrets type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "python",
    module: "chaosreliably.activities.http.probes",
    func: "measure_response_time",
    arguments: {
      url: "${reliably_url}",
    },
    secrets: "global",
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a process provider", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "process",
    path: "vegeta",
    arguments:
      "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
  };
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a process provider with an arguments array", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "process",
    path: "vegeta",
    arguments: [
      "-cpus 2",
      "attack -targets=data/scenario.txt",
      "-workers=2",
      "-connections=1",
      "-rate=3",
      "-timeout=3s",
      "-duration=30s",
      "-output=result.bin",
    ],
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a process provider with an arguments object", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "process",
    path: "vegeta",
    arguments: {
      cpus: 2,
      attack: "-targets=data/scenario.txt",
      workers: 2,
      connections: 1,
      rate: 3,
      timeout: "3s",
      duration: "30s",
      output: "result.bin",
    },
  };
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe has a process provider with a wrongly formed arguments object", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "process",
    path: "vegeta",
    arguments: [
      "cpus 2",
      'attack "-targets=data/scenario.txt"',
      "workers 2",
      "connections 1",
      "rate: 3",
      'output: "result.bin"',
    ],
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's process provider has no path", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "process",
    arguments:
      "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's process provider has an invalid path", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "process",
    path: false,
    arguments:
      "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's process provider has an invalid timeout", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "process",
    path: "vegeta",
    arguments:
      "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    timeout: "5",
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where an SSH probe's process provider has an invalid secret property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp["steady-state-hypothesis"].probes[0].provider = {
    type: "process",
    path: "vegeta",
    arguments:
      "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    timeout: 5,
    secrets: [5],
  };
  const expected: string =
    "<code>steady-state-hypothesis</code> property is invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment without a method property", () => {
  const exp: any = cloneDeep(fullExperiment);
  delete exp.method;
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with an incorrect method property type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method = {
    type: "action",
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  };
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method item has an invalid type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "actino",
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  });
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method item has no type", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  });
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action has no name", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "action",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  });
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action has an invalid name", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "action",
    name: false,
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  });
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action has no provider", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "action",
    name: "simulate-user-traffic",
    background: true,
  });
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action has an invalid provider", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "action",
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  });
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action has controls", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "action",
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
    controls: [
      {
        name: "tracing",
        provider: {
          type: "python",
          module: "chaostracing.control",
        },
      },
    ],
  });
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action has invalid controls", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method = [
    {
      type: "action",
      name: "terminate-one-function",
      provider: {
        type: "python",
        module: "chaosk8s.pod.actions",
        func: "terminate_pods",
        arguments: {
          ns: "openfaas-fn",
          label_selector: "faas_function=astre",
          rand: true,
        },
      },
      pauses: {
        before: 5,
      },
      controls: [
        {
          provider: {
            type: "python",
            module: "chaostracing.control",
          },
        },
      ],
    },
  ];
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action provider has a secret property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "action",
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      secrets: ["global"],
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  });
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action provider has an invalid secret property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "action",
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      secrets: "global",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  });
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action has an invalid background property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method.push({
    type: "action",
    name: "simulate-user-traffic",
    background: "true",
    provider: {
      type: "process",
      path: "vegeta",
      secrets: ["global"],
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
  });
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has an after property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {
    after: 5,
  };
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has an after interpolated property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {
    after: "${duration}",
  };
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has both before and after properties", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {
    before: 5,
    after: 5,
  };
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has neither before nor after properties", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {};
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses are undefined", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = undefined;
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses is invalid", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = [5, 5];
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has an invalid before property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {
    before: true,
  };
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has an invalid after property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {
    after: false,
  };
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has an invalid before property, but a valid after", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {
    before: false,
    after: 5,
  };
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has an invalid after property, but a valid before", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {
    before: 5,
    after: false,
  };
  const expected: string = "<code>method</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment where one method action pauses has an unknown property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.method[1].pauses = {
    before: 5,
    during: 5,
    after: 5,
  };
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment without rollbacks property", () => {
  const exp: any = cloneDeep(fullExperiment);
  delete exp.rollbacks;
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with a single rollback", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.rollbacks.push({
    type: "action",
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
    controls: [
      {
        name: "tracing",
        provider: {
          type: "python",
          module: "chaostracing.control",
        },
      },
    ],
  });
  const expected: string = "";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with an invalid rollbacks property", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.rollbacks = {
    type: "action",
    name: "simulate-user-traffic",
    background: true,
    provider: {
      type: "process",
      path: "vegeta",
      arguments:
        "-cpus 2 attack -targets=data/scenario.txt -workers=2 -connections=1 -rate=3 -timeout=3s -duration=30s -output=result.bin",
    },
    controls: [
      {
        name: "tracing",
        provider: {
          type: "python",
          module: "chaostracing.control",
        },
      },
    ],
  };
  const expected: string =
    "<code>rollbacks</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test("check experiment with a probe as rollback", () => {
  const exp: any = cloneDeep(fullExperiment);
  exp.rollbacks.push({
    type: "probe",
    name: "function-must-exist",
    tolerance: [4, "k8s", false],
    provider: {
      type: "http",
      secrets: ["global"],
      url: "http://demo.foo.bar/system/function/astre",
      headers: {
        Authorization: "${auth}",
      },
    },
  });
  const expected: string =
    "<code>rollbacks</code> property is missing or invalid";
  const x = checkExperiment(exp);
  assert.is(x, expected);
});

test.run();
