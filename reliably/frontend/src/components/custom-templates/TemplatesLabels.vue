<template>
  <ul class="templatesLabels list-reset pills">
    <li v-for="label in Object.keys(labelsObject)" :key="label">
      <TemplatesLabel
        :label="{ label: label, active: labelsObject[label] }"
        @update-search-params="updateParams"
      />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";
import TemplatesLabel from "@/components/custom-templates/TemplatesLabel.vue";

const props = defineProps<{
  labels: readonly string[];
}>();

const emit = defineEmits<{
  (e: "getTemplatesByLabels", terms: string[]): void;
}>();

const { labels } = toRefs(props);

const loc = ref<Location | null>(null);

const labelsObject = computed<{ [key: string]: boolean }>(() => {
  let obj: { [key: string]: boolean } = {};
  labels.value.forEach((l) => {
    obj[l] = false;
  });
  return obj;
});

const queryTerms = ref<string[]>([]);
const getQueryParams = () => {
  if (loc.value !== null) {
    let params = new URLSearchParams(loc.value.search);
    queryTerms.value = params.getAll("q");
    queryTerms.value.forEach((t) => {
      labelsObject.value[t] = true;
    });
  }
};

function updateParams(term: string, action: string) {
  if (action === "add") {
    if (!queryTerms.value.includes(term)) {
      queryTerms.value.push(term);
    }
  } else if (action === "remove") {
    let index: number = queryTerms.value.indexOf(term);
    if (index !== -1) {
      queryTerms.value.splice(index, 1);
    }
  }
  let queryTermsString = "";
  if (queryTerms.value.length) {
    queryTermsString += "?";
    queryTerms.value.forEach((t) => {
      queryTermsString += `q=${t}&`;
    });
    queryTermsString = queryTermsString.slice(0, -1);
  } else {
    queryTermsString = `${window.location.origin}/${window.location.pathname}`;
  }
  history.pushState({}, "", queryTermsString);
  emit("getTemplatesByLabels", queryTerms.value);
}

onMounted(() => {
  loc.value = window.location;
  getQueryParams();
});
</script>

<style lang="scss" scoped>
.templatesLabels {
  margin-bottom: var(--space-medium);
}
</style>
