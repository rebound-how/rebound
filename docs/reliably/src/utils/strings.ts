/** Remove \ and / from beginning of string */
export function removeLeadingSlash(path: string) {
  return path.replace(/^[/\\]+/, "");
}

/** Remove \ and / from end of string */
export function removeTrailingSlash(path: string) {
  return path.replace(/[/\\]+$/, "");
}

export function addTrailingSlash(path: string) {
  if (!path.endsWith("/")) {
    path += "/";
  }
  return path;
}

export function localStorageToBoolean(
  storedValue: string
): boolean | undefined {
  if (storedValue === "false") {
    return false;
  } else if (storedValue === "true") {
    return true;
  }
  return undefined;
}

export function booleanToLocalStorage(b: boolean): string {
  return b ? "true" : "false";
}
