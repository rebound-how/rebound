import { test } from "uvu";
import * as assert from "uvu/assert";

import { cleanStores } from "nanostores";
import {
  notifications,
  addNotification,
  removeNotification,
} from "../src/stores/notifications";

import type { Notification } from "@/types/ui-types";

test.before.each(() => {
  notifications.set([]);
});

test.after.each(() => {
  cleanStores(notifications);
});

test("Notifications are empty on app start", () => {
  assert.equal(notifications.get(), []);
});

test("Add a simple notification", () => {
  const expected: Notification = {
    title: "Test",
    message: "This a test notification",
    autoClose: false,
    hide: false,
  };
  addNotification({
    title: "Test",
    message: "This a test notification",
  });
  const n: Notification = notifications.get()[0];
  const x: Notification = {
    title: n.title,
    message: n.message,
    autoClose: n.autoClose,
    hide: n.hide,
  };
  assert.equal(x, expected);
});

test("Add a complex notification", () => {
  const expected: Notification = {
    title: "Test",
    message: "This a test notification",
    autoClose: true,
    hide: true,
  };
  addNotification({
    title: "Test",
    message: "This a test notification",
    autoClose: true,
    hide: true,
  });
  const n: Notification = notifications.get()[0];
  const x: Notification = {
    title: n.title,
    message: n.message,
    autoClose: n.autoClose,
    hide: n.hide,
  };
  assert.equal(x, expected);
});

test("id is properly generated", () => {
  const regexExp =
    /^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$/gi;
  addNotification({
    title: "Test",
    message: "This a test notification",
  });
  const x: Notification = notifications.get()[0];
  assert.is(x.id === undefined, false);
  assert.is(regexExp.test(x.id!), true);
});

test("createdAt is properly generated", () => {
  addNotification({
    title: "Test",
    message: "This a test notification",
  });
  const x: Notification = notifications.get()[0];
  assert.is(x.createdAt === undefined, false);
  assert.instance(x.createdAt, Date);
});

test("Add more than one notification", () => {
  const expected: number = 2;
  addNotification({
    title: "Test",
    message: "This a test notification",
  });
  addNotification({
    title: "Another",
    message: "This a test notification",
  });
  const x: number = notifications.get().length;
  assert.equal(x, expected);
});

test("Delete notification", () => {
  const expected: number = 0;
  addNotification({
    title: "Test",
    message: "This a test notification",
  });
  const n: Notification[] = notifications.get();
  const id: string = n[0].id!;
  removeNotification(id);
  const x: number = notifications.get().length;
  assert.equal(x, expected);
});

test.run();
