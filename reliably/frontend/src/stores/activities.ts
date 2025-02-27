import { atom } from "nanostores";

import { increaseLoaderCounter, decreaseLoaderCounter } from "../stores/loader";
import { addNotification } from "../stores/notifications";

import type { Activity, Notification } from "@/types/ui-types";

export const activities = atom<Activity[]>([]);

export function updateActivities(data: Activity[]) {
  activities.set(data);
  return activities.get();
};

export async function fetchActivities() {
  let current = activities.get();
  if (current.length === 0) {
    increaseLoaderCounter();
    const url = `/endpoints/workflows.json`;
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(response.statusText);
      } else {
        const a: { activities: Activity[] } = await response.json();
        updateActivities(a.activities);
      }
    } catch (e) {
      const n: Notification = {
        title: "Activities couldn't be fetched",
        message: (e as Error).message,
        type: "error",
      };
      addNotification(n);
    } finally {
      decreaseLoaderCounter();
    }
  }
};
