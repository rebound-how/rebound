import { test } from "uvu";
import * as assert from "uvu/assert";

import { hasProp } from "../src/utils/objects";

test("object has property", () => {
  const obj: object = {
    name: "John",
  };
  const expected: boolean = true;
  const x = hasProp(obj, "name");
  assert.is(x, expected);
});

test("object doesn't have property", () => {
  const obj: object = {
    name: "John",
  };
  const expected: boolean = false;
  const x = hasProp(obj, "last_name");
  assert.is(x, expected);
});

test("object is an array", () => {
  const obj: object = ["Sarah", "John"];
  const expected: boolean = false;
  const x = hasProp(obj, "last_name");
  assert.is(x, expected);
});

test.run();
