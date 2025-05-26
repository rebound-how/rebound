<template>
  <nav role="navigation" aria-label="pagination">
    <ul class="list-reset">
      <li>
        <a :href="page.url.prev" :class="{ disabled: noPreviousPage }">
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
          <a href="/blog" :class="{ active: page.currentPage === 1 }">1</a>
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
        <a :href="page.url.next" :class="{ disabled: noNextPage }">
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
import { toRefs, ref, computed } from "vue";

export interface AstroPaginationUrl {
  current: string;
  prev: string | undefined;
  next: string | undefined;
}

export interface AstroPaginationPage {
  // cf https://docs.astro.build/en/reference/api-reference/#the-pagination-page-prop
  data: any[];
  start: number;
  end: number;
  size: number;
  total: number;
  currentPage: number;
  lastPage: number;
  url: AstroPaginationUrl;
}

export interface PagerPage {
  number: number;
  url: string;
}

const props = defineProps<{
  page: AstroPaginationPage;
}>();
const { page } = toRefs(props);

const pagesArray = ref<PagerPage[]>([]);
for (let i: number = 1; i <= page.value.lastPage; i++) {
  if (i === 1) {
    pagesArray.value.push({
      number: 1,
      url: "/blog/",
    });
  } else {
    pagesArray.value.push({
      number: i,
      url: `/blog/${i.toString()}/`,
    });
  }
}

const noPreviousPage = computed((): boolean => {
  return page.value.url.prev === undefined;
});
const noNextPage = computed((): boolean => {
  return page.value.url.next === undefined;
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
