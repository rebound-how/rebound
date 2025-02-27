<template>
  <form class="form entityFilter">
    <div class="inputWrapper">
      <label for="searchTerm">Search</label>
      <input
        type="text"
        id="searchTerm"
        name="searchTerm"
        v-model="searchTerm"
        @keyup="handleSearch"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { updateURLParameter } from "@/utils/strings";

const searchTerm = ref<string>("");

const emit = defineEmits<{
  (e: "search"): void;
}>();

const getSearchParams = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("search")) {
    searchTerm.value = params.get("search")!;
  } else {
    searchTerm.value = "";
  }
};

let timeout: ReturnType<typeof setTimeout> | null = null;
function handleSearch() {
  // clear timeout variable
  if (timeout !== null) {
    clearTimeout(timeout);
  }

  timeout = setTimeout(function () {
    const newURL = updateURLParameter(
      window.location.href,
      "search",
      searchTerm.value
    );
    window.history.replaceState("", "", newURL);
    emit("search");
  }, 500);
}

onMounted(() => {
  getSearchParams();
});
</script>

<style lang="scss">
.entityFilter {
  margin-top: var(--space-medium);
  margin-bottom: var(--space-medium);
  padding: var(--space-small);

  background-color: var(--section-background);
  border-radius: var(-border-radius-m);
}
</style>
