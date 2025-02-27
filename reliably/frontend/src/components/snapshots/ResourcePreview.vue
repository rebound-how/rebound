<template>
  <li class="resourcePreview tableList__row">
    <div
      class="tableList__cell tableList__cell--center tableList__cell--status resourcePreview__icon">
      <span
        v-if="resource.meta.platform === 'k8s'"
        title="Kubernetes Resource"
      >
        <KubernetesLogo />
      </span>
      <span
        v-else-if="resource.meta.platform === 'aws'"
        title="AWS Resource"
      >
        <AwsLogo />
      </span>
    </div>
    <div class="tableList__cell resourcePreview__metaname">
      <a :href="`/resources/view/?id=${resource.id}`" v-if="resource.id">
        {{ resource.meta.display }}
      </a>
    </div>
    <div class="tableList__cell resourcePreview__meta">
      <a :href="`/resources/view/?id=${resource.id}`" v-if="resource.id">
        {{ resource.meta.kind }}
      </a>
    </div>
    <div class="tableList__cell resourcePreview__meta">
      <a :href="`/resources/view/?id=${resource.id}`" v-if="resource.id">
        {{ resource.meta.category }}
      </a>
    </div>
    <div class="tableList__cell resourcePreview__meta">
      <a :href="`/resources/view/?id=${resource.id}`" v-if="resource.id">
        {{ resource.links.length }}
      </a>
    </div>
    <div v-if="tags.length" class="tableList__cell resourcePreview__tags">
      <TagList :tags="tags" />
    </div>
  </li>
</template>

<script setup lang="ts">
import { toRefs, computed, ref } from "vue";
import type {
  SnapshotDiscoveryResource,
} from "@/types/snapshots";
import TagList from "@/components/_ui/TagList.vue";

import AwsLogo from "@/components/svg/AwsLogo.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogo.vue";


const props = defineProps<{
  resource: SnapshotDiscoveryResource;
  page?: number;
}>();
const { resource, page } = toRefs(props);

const tags = computed<string[]>(() => {
  let t: string[] = [];

  if (resource.value.meta.kind !== "pod") {
    t.push(resource.value.meta.name);
  }

  if (resource.value.meta.project) {
    t.push(`project: ${resource.value.meta.project}`);
  };
  
  if (resource.value.meta.region) {
    t.push(`region: ${resource.value.meta.region}`);
  };
  
  if (resource.value.meta.zone) {
    t.push(`zone: ${resource.value.meta.zone}`);
  };

  if (resource.value.meta.ns) {
    t.push(`ns: ${resource.value.meta.ns}`);
  };

  return t;
});


</script>

<style lang="scss" scoped>
.resourcePreview {
  > .tableList__cell {
    small {
      display: block;

      color: var(--text-color-dim);
      font-size: 1.4rem;
    }
  }

  &__icon {
    svg {
      width: 2.4rem;
    }

    span[title="Kubernetes Resource"] {
      color: hsl(220, 72%, 53%);
    }
  }

  &__meta {
    a {
      color: inherit;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }

    &:first-letter {
        text-transform: capitalize;
      }
  }

  &__metaname {
    a {
      font-size: 1.8rem;
      font-weight: 700;
      text-decoration: none;

      &:hover {
        color: var(--accentColorSecondary);
      }
    }
  }


  &__tags {
    display: flex;
    align-items: center;
    gap: var(--space-small);

    &__heading {
      color: var(--text-color-dim);
      font-size: 1.4rem;
      text-transform: uppercase;
    }

    &__details {
      margin-top: 0;

      font-size: 2.4rem;

      &:first-letter {
        text-transform: capitalize;
      }
    }

    > div:not(-first-child) {
      padding-left: var(--space-small);

      border-left: 0.1rem solid var(--section-separator-color);
    }
  }
}
</style>
