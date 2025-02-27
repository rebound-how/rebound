<template></template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useStore } from "@nanostores/vue";
import { isLoggedIn, organizationToken, tryLogin } from "@/stores/user";

const isUserLoggedIn = useStore(isLoggedIn);
const userToken = useStore(organizationToken);

const context = ref<string | undefined>(undefined);

const getContext = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("context")) {
    context.value = params.get("context")!;
  }
};

const loginSubmitHandler = async () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);

  if (
    params.has("join") &&
    params.get("join") === "success" &&
    params.has("orgid") &&
    params.get("orgid") !== undefined
  ) {
    context.value === params.get("orgid");
  }

  if (context.value !== undefined) {
    await tryLogin(context.value);
    if (isUserLoggedIn && userToken.value) {
      if (params.has("redirect_to")) {
        const redirect = params.get("redirect_to")!;
        if (redirect === "subscribe") {
          const plan = params.get("plan");
          location.replace(`/settings/organization/?plan=${plan}`);
        } else if (redirect === "templates") {
          const activity = params.get("activity");
          location.replace(
            `/experiments/custom-templates/create/?activity=${activity}`
          );
        }
      } else if (params.has("join")) {
        const join = params.get("join");
        const org_name = params.get("org");
        const org_id = params.get("orgid");
        location.replace(
          `/?org_name=${org_name}&org_id=${org_id}&join=${join}`
        );
      } else {
        location.replace("/");
      }
    } else {
      location.replace("/login?s=failed");
    }
  }
};

onMounted(async () => {
  await getContext();
  await loginSubmitHandler();
});
</script>
