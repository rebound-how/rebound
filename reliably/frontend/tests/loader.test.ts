import { test } from "uvu";
import * as assert from "uvu/assert";

import { cleanStores } from "nanostores";
import * as loader from "../src/stores/loader";

test.before.each(() => {
  loader.counter.set(0);
});

test.after.each(() => {
  cleanStores(loader.counter);
});

test("Loader initial state", () => {
  assert.is(loader.counter.get(), 0);
});

test("Loader increase", () => {
  loader.increaseLoaderCounter();
  assert.is(loader.counter.get(), 1);
});

test("Loader decrease", () => {
  loader.decreaseLoaderCounter();
  assert.is(loader.counter.get(), -1);
});
test.run();
