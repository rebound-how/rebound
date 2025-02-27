import { test } from "uvu";
import * as assert from "uvu/assert";

import { formatDeploymentType } from "../src/utils/deployments";

test("github is returned as [GitHub]", () => {
  const expected: string = "[GitHub]";
  const x = formatDeploymentType("github");
  assert.is(x, expected);
});

test("reliably_cloud is returned as Reliably Cloud", () => {
  const expected: string = "[Reliably Cloud]";
  const x = formatDeploymentType("reliably_cloud");
  assert.is(x, expected);
});

test("reliably_cli is returned as Reliably CLI", () => {
    const expected: string = "[Reliably CLI]";
    const x = formatDeploymentType("reliably_cli");
    assert.is(x, expected);
  });
  
test("reliably-cloud is returned between brackets", () => {
  const expected: string = "[reliably-cloud]";
  const x = formatDeploymentType("reliably-cloud");
  assert.is(x, expected);
});

test.run();
