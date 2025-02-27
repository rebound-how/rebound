import { test } from "uvu";
import * as assert from "uvu/assert";

import {
  removeLeadingSlash,
  removeTrailingSlash,
  addTrailingSlash,
  shortenUuid,
  urlToRepository,
  humanReadableTime,
  humanReadableDuration,
  isStringSerializedJson,
  formatScalarTolerance,
  validateLabelSelector,
  formatTolerance,
  generateKey,
} from "../src/utils/strings";

import type { Repository } from "@/types/ui-types";
import type { Probe } from "@/types/experiments";

test("remove one leading slash", () => {
  const expected: string = "path";
  const x = removeLeadingSlash("/path");
  assert.is(x, expected);
});

test("remove all leading slashes", () => {
  const expected: string = "path";
  const x = removeLeadingSlash("/////path");
  assert.is(x, expected);
});

test("string with no leading slash is unchanged", () => {
  const expected: string = "path";
  const x = removeLeadingSlash("path");
  assert.is(x, expected);
});

test("remove one trailling slash", () => {
  const expected: string = "path";
  const x = removeTrailingSlash("path/");
  assert.is(x, expected);
});

test("remove all trailing slashes", () => {
  const expected: string = "path";
  const x = removeTrailingSlash("path/////");
  assert.is(x, expected);
});

test("string with no trailing slash is unchanged", () => {
  const expected: string = "path";
  const x = removeTrailingSlash("path");
  assert.is(x, expected);
});

test("add trailling slash", () => {
  const expected: string = "path/";
  const x = addTrailingSlash("path");
  assert.is(x, expected);
});

test("add trailling slash to empty string", () => {
  const expected: string = "/";
  const x = addTrailingSlash("");
  assert.is(x, expected);
});

test("can't add trailling slash to string already having one", () => {
  const expected: string = "path/";
  const x = addTrailingSlash("path/");
  assert.is(x, expected);
});

test("slash functions are chainable", () => {
  const expected: string = "path";
  const x = removeTrailingSlash(removeLeadingSlash(addTrailingSlash("/path")));
  assert.is(x, expected);
});

test("UUID is shortened", () => {
  const expected: string = "05b1eda";
  const x = shortenUuid("05b1eda4-088b-4f66-b454-7077bd73f427");
  assert.is(x, expected);
});

test("non-UUID long string is untouched", () => {
  const expected: string = "loremipsumdolorsitamet";
  const x = shortenUuid("loremipsumdolorsitamet");
  assert.is(x, expected);
});

test("empty string is untouched", () => {
  const expected: string = "";
  const x = shortenUuid("");
  assert.is(x, expected);
});

test("non-UUID short string is untouched", () => {
  const expected: string = "abc";
  const x = shortenUuid("abc");
  assert.is(x, expected);
});

test("valid github URL is transformed", () => {
  const expected: Repository = {
    organization: "reliablyhq",
    repository: "reliably",
  };
  const x = urlToRepository("https://github.com/reliablyhq/reliably/");
  assert.equal(x, expected);
});

test("valid github URL with no trailing slash is transformed", () => {
  const expected: Repository = {
    organization: "reliablyhq",
    repository: "reliably",
  };
  const x = urlToRepository("https://github.com/reliablyhq/reliably");
  assert.equal(x, expected);
});

test("long github URL is transformed", () => {
  const expected: Repository = {
    organization: "reliablyhq",
    repository: "reliably",
  };
  const x = urlToRepository(
    "https://github.com/reliablyhq/reliably/blob/main/frontend/src/stores/user.ts"
  );
  assert.equal(x, expected);
});

test("a string that isn't a URL return an empty Repository object", () => {
  const expected: Repository = {
    organization: "",
    repository: "",
  };
  const x = urlToRepository("reliablyhq/reliably");
  assert.equal(x, expected);
});

test("Date object is correctly converted", () => {
  const expected: string = "17 December 1995, 3:24:00";
  const date = new Date("1995-12-17T03:24:00");
  const x = humanReadableTime(date);
  assert.equal(x, expected);
});

test("Date string is correctly converted", () => {
  const expected: string = "17 December 1995, 3:24:00";
  const date = "1995-12-17T03:24:00";
  const x = humanReadableTime(date);
  assert.equal(x, expected);
});

test("Date object is correctly converted to short form", () => {
  const expected: string = "17 Dec 1995, 3:24:00";
  const date = new Date("1995-12-17T03:24:00");
  const x = humanReadableTime(date, "short");
  assert.equal(x, expected);
});

test("Date string is correctly converted to short form", () => {
  const expected: string = "17 Dec 1995, 3:24:00";
  const date = "1995-12-17T03:24:00";
  const x = humanReadableTime(date, "short");
  assert.equal(x, expected);
});

test("Incorrect format parameter is ignored", () => {
  const expected: string = "17 December 1995, 3:24:00";
  const date = new Date("1995-12-17T03:24:00");
  const x = humanReadableTime(date, "long");
  assert.equal(x, expected);
});

test("duration under one minute is correctly converted", () => {
  const expected: string = "17.234s";
  const x = humanReadableDuration(17.2345678);
  assert.equal(x, expected);
});

test("duration under one hour is correctly converted", () => {
  const expected: string = "17m 17.234s";
  const x = humanReadableDuration(1037.2345678);
  assert.equal(x, expected);
});

test("longer duration is correctly converted", () => {
  const expected: string = "17h 17m 17.234s";
  const x = humanReadableDuration(62237.2345678);
  assert.equal(x, expected);
});

test("very long duration is correctly converted", () => {
  const expected: string = "173h 17m 17.234s";
  const x = humanReadableDuration(623837.2345678);
  assert.equal(x, expected);
});

test("string is serialized JSON", () => {
  const expected: boolean = true;
  const str: string = '{"name":"John"}';
  const x = isStringSerializedJson(str);
  assert.equal(x, expected);
});

test("'1234' is not serialized JSON", () => {
  const expected: boolean = false;
  const str: string = "1234";
  const x = isStringSerializedJson(str);
  assert.equal(x, expected);
});

test("empty string is not serialized JSON", () => {
  const expected: boolean = false;
  const str: string = "";
  const x = isStringSerializedJson(str);
  assert.equal(x, expected);
});

test("string tolerance is returned unchanged", () => {
  const expected: string = "string";
  const str: string = "string";
  const x = formatScalarTolerance(str);
  assert.equal(x, expected);
});

test("number tolerance is returned as a string representing that number", () => {
  const expected: string = "200";
  const n: number = 200;
  const x = formatScalarTolerance(n);
  assert.equal(x, expected);
});

test("truthy boolean tolerance is returned as 'true'", () => {
  const expected: string = "true";
  const b: boolean = true;
  const x = formatScalarTolerance(b);
  assert.equal(x, expected);
});

test("falsy boolean tolerance is returned as 'false'", () => {
  const expected: string = "false";
  const b: boolean = false;
  const x = formatScalarTolerance(b);
  assert.equal(x, expected);
});

test("object tolerance is returned as 'NaN'", () => {
  const expected: string = "NaN";
  const o: any = {
    type: "url",
    value: "https://reliably.com",
  };
  const x = formatScalarTolerance(o);
  assert.equal(x, expected);
});

test("string tolerance is returned unchanged", () => {
  const expected: string = "string";
  const str: string = "string";
  const x = formatTolerance(str);
  assert.equal(x, expected);
});

test("number tolerance is returned as a string representing that number", () => {
  const expected: string = "200";
  const n: number = 200;
  const x = formatTolerance(n);
  assert.equal(x, expected);
});

test("truthy boolean tolerance is returned as 'true'", () => {
  const expected: string = "true";
  const b: boolean = true;
  const x = formatTolerance(b);
  assert.equal(x, expected);
});

test("falsy boolean tolerance is returned as 'false'", () => {
  const expected: string = "false";
  const b: boolean = false;
  const x = formatTolerance(b);
  assert.equal(x, expected);
});

test("array tolerance is returned as a string representing this array", () => {
  const expected: string = "[200, false, hello]";
  const t: Array<any> = [200, false, "hello"];
  const x = formatTolerance(t);
  assert.equal(x, expected);
});

test("array tolerance with an invalid value is returned as a string representing this array", () => {
  const expected: string = "[200, false, hello, NaN]";
  const t: Array<any> = [200, false, "hello", [200, false, "hello"]];
  const x = formatTolerance(t);
  assert.equal(x, expected);
});

test("probe tolerance is returned as a 'Probe'", () => {
  const expected: string = "Probe";
  const t: Probe["tolerance"] = {
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
  };
  const x = formatTolerance(t);
  assert.equal(x, expected);
});

test("app=my-app is a valid label selector", () => {
  const ls: string = "app=my-app";
  const expected: boolean = true;
  const x = validateLabelSelector(ls);
  assert.equal(x, expected);
});

test("a label selector can contain multiple requirements", () => {
  const ls: string = "app=my-app, truc=bidule";
  const expected: boolean = true;
  const x = validateLabelSelector(ls);
  assert.equal(x, expected);
});

test("a label selector requirement must contain an equal sign", () => {
  const ls: string = "app:my-app, truc=bidule";
  const expected: boolean = false;
  const x = validateLabelSelector(ls);
  assert.equal(x, expected);
});

test("a label selector requirement can't start with an equal sign", () => {
  const ls: string = "=my-app, truc=bidule";
  const expected: boolean = false;
  const x = validateLabelSelector(ls);
  assert.equal(x, expected);
});

test("a label selector requirement can't end with an equal sign", () => {
  const ls: string = "app=, truc=bidule";
  const expected: boolean = false;
  const x = validateLabelSelector(ls);
  assert.equal(x, expected);
});

test("a label selector requirement can't contain more than one equal sign", () => {
  const ls: string = "app=myapp, truc=bidule=machin";
  const expected: boolean = false;
  const x = validateLabelSelector(ls);
  assert.equal(x, expected);
});

test("secret key is a string", () => {
  if (!("crypto" in globalThis)) {
    globalThis.crypto = require("crypto");
  }
  const expected: string = "string";
  let k = generateKey(32);
  const x = typeof k;
  assert.equal(x, expected);
});

test("secret key is 32 characters long", () => {
  const expected: number = 32;
  let k = generateKey(32);
  const x = k.length;
  assert.equal(x, expected);
});

test.run();
