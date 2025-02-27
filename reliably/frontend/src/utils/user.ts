import { useStore } from "@nanostores/vue";
import { organizationName, updateUserInfo } from "../stores/user";

/* c8 ignore start */
// I don't know how to test this yet
export async function handleError403(orgId: string) {
  const currentOrganizationName = useStore(organizationName);
  let displayedName: string =
    currentOrganizationName.value === ""
      ? "[unknown]"
      : currentOrganizationName.value;
  await updateUserInfo();
  window.location.replace(
    `/?origin=403&org_name=${displayedName}&org_id=${orgId}`
  );
}
/* c8 ignore stop */
