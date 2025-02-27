<template>
    <li class="resourceLinkPreview tableList__row">
      <div
        class="tableList__cell tableList__cell--center tableList__cell--status resourceLinkPreview__icon">
        <span
          v-if="link.meta.platform === 'k8s'"
          title="Kubernetes Resource"
        >
          <KubernetesLogo />
        </span>
        <span
          v-else-if="link.meta.platform === 'aws'"
          title="AWS Resource"
        >
          <AwsLogo />
        </span>
      </div>
      <div class="tableList__cell resourceLinkPreview__metaname">
        <a :href="`/resources/view/?id=${link.id}`" v-if="link.id">
          {{ link.meta.display }}
        </a>
      </div>
      <div class="tableList__cell resourceLinkPreview__meta">
        <a :href="`/resources/view/?id=${link.id}`" v-if="link.id">
          {{ link.meta.kind }}
        </a>
      </div>
      <div class="tableList__cell resourceLinkPreview__meta">
        <a :href="`/resources/view/?id=${link.id}`" v-if="link.id">
          {{ link.meta.category }}
        </a>
      </div>
      <div class="tableList__cell resourceLinkPreview__tags">
        <TagList :tags="tags" />
      </div>
    </li>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";
import type { SnapshotDiscoveryLinkInfo } from "@/types/snapshots";
import TagList from "@/components/_ui/TagList.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogo.vue";
import AwsLogo from "@/components/svg/AwsLogo.vue";

const props = defineProps<{
  link: SnapshotDiscoveryLinkInfo;
}>();
const { link } = toRefs(props);

const tags = computed<string[]>(() => {
  let t: string[] = [];

  if (link.value.meta.kind !== "pod") {
    t.push(link.value.meta.name);
  }

  if (link.value.meta.project) {
    t.push(`project: ${link.value.meta.project}`);
  };
  
  if (link.value.meta.region) {
    t.push(`region: ${link.value.meta.region}`);
  };
  
  if (link.value.meta.zone) {
    t.push(`zone: ${link.value.meta.zone}`);
  };

  if (link.value.meta.ns) {
    t.push(`ns: ${link.value.meta.ns}`);
  };

  return t;
});

</script>

<style lang="scss" scoped>
.resourceLinkPreview {
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
