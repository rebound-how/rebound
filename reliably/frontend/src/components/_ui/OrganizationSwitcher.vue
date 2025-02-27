<template>
  <details class="organizationSwitcher" ref="switcherRef">
    <summary>{{ currentOrganizationName }} <ChevronDown /></summary>
    <ul class="organizationSwitcher__list list-reset">
      <li v-for="(o, index) in organizations" :key="index">
        <button @click="switchOrganization(o.id)">
          {{ o.name }}
          <span
            v-if="o.name === currentOrganizationName"
            class="currentOrganizationMarker"
          >
            Current
          </span>
        </button>
      </li>
    </ul>
  </details>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { onClickOutside } from "@vueuse/core";
import { useStore } from "@nanostores/vue";

import {
  user,
  organizationName,
  changeOrganization,
  organizationToken,
  updateOrganizationName,
} from "@/stores/user";
import ChevronDown from "@/components/svg/ChevronDown.vue";

const organizations = ref<{ name: string; id: string }[]>([]);
const currentOrganizationName = useStore(organizationName);

const switchOrganization = async (id: string) => {
  await changeOrganization(id);
  location.replace("/");
};

const switcherRef = ref();

onClickOutside(switcherRef, (event) => {
  switcherRef.value.removeAttribute("open");
});

onMounted(async () => {
  let u = user.get();
  await u.orgs.forEach((o) => {
    organizations.value.push({
      name: o.name,
      id: o.id,
    });
    if (o.id === organizationToken.get()) {
      updateOrganizationName(o.name);
    }
  });
});
</script>

<style lang="scss" scoped>
@use "../../styles/abstracts/mixins" as *;
.organizationSwitcher {
  position: relative;
  margin-left: var(--space-medium);

  @media print {
    display: none;
  }


  summary {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    height: 2.4rem;
    padding: 0.6rem;

    background-color: var(--switcher-summary-background);
    border-radius: var(--border-radius-s);
    cursor: pointer;
    list-style: none;

    color: var(--text-color-bright);
    font-weight: 500;

    &:hover {
      background-color: var(--switcher-summary-background-hover);
    }

    svg {
      height: 1.8rem;
    }
  }

  ul {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 9;

    min-width: 20rem;
    padding: 0.6rem;

    background-color: var(--switcher-background);
    border: 1px solid var(--switcher-border-color);
    border-radius: var(--border-radius-s);

    &::after {
      @include shadow;

      border-radius: var(--border-radius-s);
    }

    button {
      display: flex;
      align-items: center;
      padding: 0.6rem;
      width: calc(100% - 1.2rem);

      background-color: transparent;
      border: none;
      border-radius: var(--border-radius-s);
      cursor: pointer;

      font-size: 1.6rem;
      text-align: left;

      &:hover {
        background-color: var(--switcher-button-hover);
      }

      .currentOrganizationMarker {
        display: inline-block;
        margin-left: auto;
        padding: 0.1rem 0.2rem;

        background-color: var(--current-organization-background);
        border-radius: var(--border-radius-s);

        color: var(--current-organization-text);
        font-size: 1.4rem;
      }
    }
  }
}
</style>
