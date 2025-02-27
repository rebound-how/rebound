<template>
  <Matrix />
</template>

<script setup lang="ts">
import { defineAsyncComponent } from "vue";

const Matrix = defineAsyncComponent(() => import("./ExecutionsMatrix.vue"));
</script>
