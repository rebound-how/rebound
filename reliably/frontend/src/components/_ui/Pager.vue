<template>
  <nav role="navigation" aria-label="pagination">
    <ul class="list-reset" v-if="isReady">
      <li>
        <a :href="previousPage" :class="{ disabled: noPreviousPage }">
          <span class="screen-reader-text">
            Previous <span v-if="noPreviousPage">(Disabled)</span></span
          >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="feather feather-arrow-left"
          >
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
        </a>
      </li>
      <template v-if="page.lastPage <= 9">
        <li v-for="p in pagesArray" :key="p.number">
          <a :href="p.url" :class="{ active: p.number === page.currentPage }">
            {{ p.number.toString() }}
          </a>
        </li>
      </template>
      <template v-else>
        <li v-if="page.currentPage >= 2" key="1">
          <a
            :href="pagesArray[0].url"
            :class="{ active: page.currentPage === 1 }"
            >1</a
          >
        </li>
        <li v-if="page.currentPage > 3">
          <span class="filler">...</span>
        </li>
        <li v-if="page.currentPage >= 3" :key="page.currentPage - 2">
          <a :href="pagesArray[page.currentPage - 2].url">
            {{ pagesArray[page.currentPage - 2].number }}
          </a>
        </li>
        <li :key="page.currentPage - 1">
          <a :href="pagesArray[page.currentPage - 1].url" class="active">
            {{ pagesArray[page.currentPage - 1].number }}
          </a>
        </li>
        <li
          v-if="page.currentPage <= page.lastPage - 2"
          :key="page.currentPage"
        >
          <a :href="pagesArray[page.currentPage].url">
            {{ pagesArray[page.currentPage].number }}
          </a>
        </li>
        <li v-if="page.currentPage < page.lastPage - 2">
          <span class="filler">...</span>
        </li>
        <li v-if="page.currentPage <= page.lastPage - 1" :key="page.lastPage">
          <a
            :href="pagesArray[page.lastPage - 1].url"
            :class="{ active: page.currentPage === page.lastPage }"
          >
            {{ page.lastPage }}
          </a>
        </li>
      </template>
      <li>
        <a :href="nextPage" :class="{ disabled: noNextPage }">
          <span class="screen-reader-text">
            Next <span v-if="noNextPage">(Disabled)</span>
          </span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="feather feather-arrow-right"
          >
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </a>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted, watch } from "vue";
import type { PagerData } from "@/types/pager";

export interface PagerPage {
  number: number;
  url: string;
}

const props = defineProps<{
  page: PagerData;
}>();
const { page } = toRefs(props);

const isReady = ref<boolean>(false);
const pagesArray = ref<PagerPage[]>([]);

const previousPage = computed<string | undefined>(() => {
  if (page.value.currentPage === 1) {
    return undefined;
  } else {
    return `${page.value.urlBase}${page.value.currentPage - 1}`;
  }
});

const nextPage = computed<string | undefined>(() => {
  if (page.value.currentPage === page.value.lastPage) {
    return undefined;
  } else {
    return `${page.value.urlBase}${page.value.currentPage + 1}`;
  }
});

const noPreviousPage = computed((): boolean => {
  return page.value.currentPage === 1;
});
const noNextPage = computed((): boolean => {
  return page.value.currentPage === page.value.lastPage;
});

const buildArray = async (): Promise<void> => {
  pagesArray.value = [];
  for (let i: number = 1; i <= page.value.lastPage; i++) {
    pagesArray.value.push({
      number: i,
      url: `${page.value.urlBase}${i.toString()}`,
    });
  }
};

watch(page, () => {
  buildArray();
});

onMounted(async () => {
  await buildArray();
  isReady.value = true;
});
</script>

<style lang="scss" scoped>
nav {
  margin-bottom: var(--space-large);
  ul {
    display: flex;
    justify-content: center;
  }

  li {
    &:not(:last-child) {
      margin-right: 1.2rem;
    }
  }

  a,
  .filler {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 3.6rem;
    width: 3.6rem;

    border-radius: 50%;
    cursor: pointer;

    color: var(--text-color);
    font-weight: 500;
  }

  a {
    padding: 0;

    background-color: transparent;
    border: none;

    text-decoration: none;

    svg {
      height: 2rem;
    }

    &:hover {
      background-color: var(--grey-200);

      color: var(--text-color-bright);
    }

    &.active {
      background-color: var(--yellow-500);
      cursor: default;

      color: var(--text-color-bright);
    }

    &.disabled {
      cursor: default;
      opacity: 0.5;

      &:hover {
        background-color: transparent;
        color: var(--text-color);
      }
    }
  }
}
</style>
