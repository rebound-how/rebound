import { test } from "uvu";
import * as assert from "uvu/assert";

import {
  contributionToNumber,
  contributionToString,
} from "../src/utils/contributions";

test("0 returns none", () => {
  const expected: string = "none";
  const x = contributionToString(0);
  assert.is(x, expected);
});

test("'0' returns none", () => {
  const expected: string = "none";
  const x = contributionToString("0");
  assert.is(x, expected);
});

test("1 returns low", () => {
  const expected: string = "low";
  const x = contributionToString(1);
  assert.is(x, expected);
});

test("'1' returns low", () => {
  const expected: string = "low";
  const x = contributionToString("1");
  assert.is(x, expected);
});

test("2 returns medium", () => {
  const expected: string = "medium";
  const x = contributionToString(2);
  assert.is(x, expected);
});

test("'2' returns medium", () => {
  const expected: string = "medium";
  const x = contributionToString("2");
  assert.is(x, expected);
});

test("3 returns high", () => {
  const expected: string = "high";
  const x = contributionToString(3);
  assert.is(x, expected);
});

test("'3' returns none", () => {
  const expected: string = "high";
  const x = contributionToString("3");
  assert.is(x, expected);
});

test("another number returns empty string", () => {
  const expected: string = "";
  const x = contributionToString(5);
  assert.is(x, expected);
});

test("another string returns empty string", () => {
  const expected: string = "";
  const x = contributionToString("5");
  assert.is(x, expected);
});

test("string that can't be converted to number returns empty string", () => {
  const expected: string = "";
  const x = contributionToString("a");
  assert.is(x, expected);
});

test("none returns 0", () => {
  const expected: number = 0;
  const x = contributionToNumber("none");
  assert.is(x, expected);
});

test("low returns 1", () => {
  const expected: number = 1;
  const x = contributionToNumber("low");
  assert.is(x, expected);
});

test("medium returns 2", () => {
  const expected: number = 2;
  const x = contributionToNumber("medium");
  assert.is(x, expected);
});

test("low returns 3", () => {
  const expected: number = 3;
  const x = contributionToNumber("high");
  assert.is(x, expected);
});

test("another string returns null", () => {
  const expected: null = null;
  const x = contributionToNumber("higher");
  assert.is(x, expected);
});

test.run();
