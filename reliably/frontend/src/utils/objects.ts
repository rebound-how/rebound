export function hasProp(obj: object, prop: string): boolean {
  if (typeof obj !== "object") {
    return false;
  } else {
    return Object.prototype.hasOwnProperty.call(obj, prop);
  }
}
