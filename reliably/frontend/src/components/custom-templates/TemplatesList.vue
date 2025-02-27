<template>

    <div class="templatesIntroduction">
      <p>
        Templates are ready-to-go experiments that you can fill and instanciate
        without having to build them from scratch.
      </p>
      <p v-if="temps.total !== 0">
      Select any of the labels below to filter and find the right one for you. Happy learning!
      </p>
    </div>
  
  <TemplatesLabels
    v-if="ls !== null"
    :labels="ls"
    @get-templates-by-labels="getTemplatesByLabels"
  />
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <NoData message="No templates found" v-else-if="temps.total === 0"></NoData>
  <ul v-else class="templatesList tableList">
    <li class="tableList__row tableList__row--header">
      <div class="tableList__cell">Name</div>
      <div class="tableList__cell">Labels</div>
      <div class="tableList__cell">
        <span class="screen-reader-text">Actions</span>
      </div>
    </li>
    <TemplatePreview
      v-for="template in temps.templates"
      :template="(template as Template)"
      :page="page!"
      :key="template.id"
      class="tableList__row"
    />
  </ul>
  <Pager v-if="temps.total > 10" :page="pagerData" />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { Template } from "@/types/templates";
import type { PagerData } from "@/types/pager";

import {
  templates,
  fetchTemplates,
  fetchTemplatesByLabels,
  labels,
  fetchLabels,
} from "@/stores/templates";
import { useStore } from "@nanostores/vue";

import NoData from "@/components/_ui/NoData.vue";
import TemplatePreview from "@/components/custom-templates/TemplatePreview.vue";
import TemplatesLabels from "@/components/custom-templates/TemplatesLabels.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import Pager from "@/components/_ui/Pager.vue";

const isLoading = ref(true);
const page = ref<number | undefined>(undefined);
const pagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});
const temps = useStore(templates);
const ls = useStore(labels);

const getCurrentPage = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("page")) {
    page.value = parseInt(params.get("page")!);
  } else {
    page.value = 1;
  }
};

const getpagerData = () => {
  let pager: PagerData = {
    currentPage: page.value!,
    lastPage: Math.ceil(temps.value.total / 10),
    urlBase: "/experiments/custom-templates/?page=",
  };
  pagerData.value = pager;
};

async function getTemplatesByLabels(labels: string[]) {
  if (labels.length) {
    await fetchTemplatesByLabels(labels);
  } else {
    await fetchTemplates(1);
  }
}

onMounted(async () => {
  isLoading.value = true;
  getCurrentPage();
  await fetchTemplates(page.value!);
  getpagerData();
  await fetchLabels();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
  .templatesIntroduction {
    margin-bottom: var(--space-large);
    max-width: 90rem;

    // color: var(--text-color-dim);
    font-size: 1.6rem;
}
</style>
