import { DateTime } from "luxon";

export function machineDate(dateIso) {
  return DateTime.fromISO(dateIso).toFormat("yyyy-MM-dd");
}

export function humanDate(dateIso) {
  return DateTime.fromISO(dateIso).toFormat("LLLL dd, yyyy");
}

export function humanDateWithDay(dateIso) {
  return DateTime.fromISO(dateIso).toFormat("ccc, dd LLLL yyyy");
}
