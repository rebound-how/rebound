<template></template>

<script setup lang="ts">
import { onMounted } from "vue";

import { addNotification } from "@/stores/notifications";
import { changeOrganization } from "@/stores/user";
import type { Notification } from "@/types/ui-types";

function handle403Redirect() {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("origin") && params.get("origin") === "403") {
    let orgName = params.get("org_name");
    const n: Notification = {
      title: `You are not a member of organization ${orgName} anymore`,
      message:
        "If you think this is an error, please contact a member of the organization.",
      type: "warning",
    };
    addNotification(n);
  }
}

async function handleJoinStatus() {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("join")) {
    const joinStatus: string = params.get("join")!;
    if (joinStatus === "success") {
      let orgId = params.get("org_id");
      if (orgId !== null) {
        let orgName = params.get("org_name");
        await changeOrganization(orgId);
        location.replace(`/?org_name=${orgName}&join=moved`);
      }
    } else if (joinStatus === "moved") {
      let orgName = params.get("org_name");
      const n: Notification = {
        title: "You joined a new organization",
        message: `You are now a member of ${orgName}`,
        type: "success",
      };
      addNotification(n);
    } else if (joinStatus === "noseats") {
      let orgName = params.get("org_name");
      const n: Notification = {
        title: `We couldn't add you to organization ${orgName}`,
        message: "The organization has no available seats.",
        type: "error",
      };
      addNotification(n);
    } else if (joinStatus === "failed") {
      let orgName = params.get("org_name");
      const n: Notification = {
        title: `We couldn't add you to organization ${orgName}`,
        message: "An unexpected error occured. Please try again.",
        type: "error",
      };
      addNotification(n);
    } else if (joinStatus === "expired") {
      const n: Notification = {
        title: "You used an expired invitation link",
        message: "Please ask the sender to send you a new link.",
        type: "error",
      };
      addNotification(n);
    }
  }
}

onMounted(async () => {
  handle403Redirect();
  await handleJoinStatus();
});
</script>
