import { atom } from "nanostores";
import { uuid } from "vue-uuid";

import type { Notification } from "@/types/ui-types";

export const notifications = atom<Notification[]>([]);

export function addNotification(n: Notification) {
  const notification: Notification = {
    title: n.title,
    message: n.message,
    autoClose: n.autoClose === undefined ? false : n.autoClose,
    hide: n.hide === undefined ? false : n.hide,
    createdAt: new Date(),
    id: uuid.v4(),
    type: n.type === undefined ? null : n.type,
  };
  notifications.set([...notifications.get(), notification]);
  return notifications.get();
}

export function removeNotification(id: string) {
  let arr: Notification[] = notifications.get();
  const index: number = arr.findIndex((n) => n.id === id);
  if (index !== -1) {
    arr.splice(index, 1);
    notifications.set([...arr]);
    return notifications.get();
  }
};

export function clearNotifications() {
  notifications.set([]);
  return notifications.get();
};
