import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import type { Repository, Notification } from "@/types/ui-types";
import type { Experiment, Probe } from "@/types/experiments";
import { addNotification } from "../stores/notifications";

/** Remove \ and / from beginning of string */
export function removeLeadingSlash(path: string): string {
  return path.replace(/^[/\\]+/, "");
}

/** Remove \ and / from end of string */
export function removeTrailingSlash(path: string): string {
  return path.replace(/[/\\]+$/, "");
}

export function addTrailingSlash(path: string): string {
  if (!path.endsWith("/")) {
    path += "/";
  }
  return path;
}

export function updateURLParameter(
  url: string,
  param: string,
  paramVal: string
) {
  var TheAnchor = null;
  var newAdditionalURL = "";
  var tempArray = url.split("?");
  var baseURL = tempArray[0];
  var additionalURL = tempArray[1];
  var temp = "";

  if (additionalURL) {
    var tmpAnchor = additionalURL.split("#");
    var TheParams = tmpAnchor[0];
    TheAnchor = tmpAnchor[1];
    if (TheAnchor) additionalURL = TheParams;

    tempArray = additionalURL.split("&");

    for (var i = 0; i < tempArray.length; i++) {
      if (tempArray[i].split("=")[0] != param) {
        newAdditionalURL += temp + tempArray[i];
        temp = "&";
      }
    }
  } else {
    var tmpAnchor = baseURL.split("#");
    var TheParams = tmpAnchor[0];
    TheAnchor = tmpAnchor[1];

    if (TheParams) baseURL = TheParams;
  }

  if (TheAnchor) paramVal += "#" + TheAnchor;

  var rows_txt = temp + "" + param + "=" + paramVal;
  return baseURL + "?" + newAdditionalURL + rows_txt;
}

export function shortenUuid(uuid: string): string {
  const regexExp =
    /^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$/gi;
  if (regexExp.test(uuid)) {
    return uuid.substring(0, 7); // First 7 characters
  } else {
    // It's not a valid UUID
    return uuid;
  }
}

export function urlToRepository(url: string): Repository {
  let repository = {
    organization: "",
    repository: "",
  };
  try {
    const urlObject: URL = new URL(url);
    let pathname: string = urlObject.pathname;
    let pathArray: string[] = pathname.split("/");
    repository.organization = pathArray[1];
    repository.repository = pathArray[2];
  } catch (e) {
    const n: Notification = {
      title: "This is not a valid repository URL",
      message: (e as Error).message,
      type: "error",
    };
    addNotification(n);
  } finally {
    return repository;
  }
}

export function humanReadableTime(
  timestamp: string | Date | number,
  format?: string,
  unix?: boolean
): string {
  if (format === "shortest") {
    if (unix && typeof timestamp === "number") {
      return dayjs.unix(timestamp).format("DD/MM/YYYY H:mm:ss");
    } else {
      return dayjs(timestamp).format("DD/MM/YYYY H:mm:ss");
    }
  } else if (format === "short") {
    if (unix && typeof timestamp === "number") {
      return dayjs.unix(timestamp).format("D MMM YYYY, H:mm:ss");
    } else {
      return dayjs(timestamp).format("D MMM YYYY, H:mm:ss");
    }
  } else {
    if (unix && typeof timestamp === "number") {
      return dayjs.unix(timestamp).format("D MMMM YYYY, H:mm:ss");
    } else {
      return dayjs(timestamp).format("D MMMM YYYY, H:mm:ss");
    }
  }
}

export function humanReadableDuration(seconds: number): string {
  dayjs.extend(duration);
  let d: duration.Duration = dayjs.duration(seconds, "seconds");
  const ms = Math.floor(d.milliseconds());
  const s = d.seconds();
  const m = d.minutes();
  const h = Math.floor(d.asHours());

  let str: string = "";
  if (h > 0) {
    str += `${h.toString()}h `;
  }
  if (m > 0) {
    str += `${m.toString()}m `;
  }
  str += `${s.toString()}`;
  str += `.${ms.toString()}s`;
  return str;
}

export function isStringSerializedJson(str: string): boolean {
  try {
    let o: Experiment = JSON.parse(str);

    // Handle non-exception-throwing cases:
    // Neither JSON.parse(false) or JSON.parse(1234) throw errors, hence the type-checking,
    // but... JSON.parse(null) returns null, and typeof null === "object",
    // so we must check for that, too. Thankfully, null is falsey, so this suffices:
    if (o && typeof o === "object") {
      return true;
    }
  } catch (e: unknown) {}

  return false;
}

export function formatScalarTolerance(t: string | boolean | number): string {
  if (typeof t === "string") {
    return t;
  } else if (typeof t === "number") {
    return t.toString();
  } else if (typeof t === "boolean") {
    return t === false ? "false" : "true";
  } else {
    return "NaN";
  }
}

export function formatTolerance(t: Probe["tolerance"]): string {
  if (
    typeof t === "string" ||
    typeof t === "boolean" ||
    typeof t === "number"
  ) {
    return formatScalarTolerance(t);
  } else if (Array.isArray(t)) {
    t.forEach((item, index) => {
      t[index] = formatScalarTolerance(item);
    });
    let toleranceString: string = `[${t.join(", ")}]`;
    return toleranceString;
  } else {
    return "Probe";
  }
}

export function validateLabelSelector(l: string): boolean {
  let isValid: boolean = true;
  if (l !== "") {
    const arr: string[] = l.split(",").map((element) => element.trim());
    arr.every((l) => {
      if (l !== "") {
        let index = l.indexOf("=");
        if (index === -1 || index === 0 || index === l.length - 1) {
          isValid = false;
        } else {
          let index2 = l.indexOf("=", index + 1);
          if (index2 === -1) {
            // There's a second equal sign
            return true;
          } else {
            isValid = false;
          }
        }
      }
    });
  }
  return isValid;
}

// dec2hex :: Integer -> String
// i.e. 0-255 -> '00'-'ff'
// Used by generateKey()
function dec2hex(dec: number): string {
  return dec.toString(16).padStart(2, "0");
}

// generateKey :: Integer -> String
// Used to generate a random key for environment secrets
// and some v-models
export function generateKey(len: number) {
  var arr = new Uint8Array(len / 2);
  crypto.getRandomValues(arr);
  return Array.from(arr, dec2hex).join("");
}

export function dateAsId(date: string) {
  return date.replaceAll(".", "-");
}

// Make activity name breakable at "_" and "-" characters
export function breakableName(name: string) {
  return name.replaceAll("_", "_<wbr>").replaceAll("-", "-<wbr>");
}

export function trimString(str: string, length: number) {
  if (str.length > length) {
    return str.substring(0, length) + "...";
  } else {
    return str;
  }
}
