<template></template>

<script setup lang="ts">
import { onMounted } from "vue";
import { tryLogout } from "@/stores/user";

onMounted(async () => {
  await tryLogout();
  location.replace("/login/");
});
</script>
