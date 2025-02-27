<template>
  <LoadingPlaceholder size="large" v-if="isLoading" />
  <article
    class="resourceView"
    v-else-if="current !== undefined && current !== null && current.id !== undefined"
  >
    <header class="pageHeader">
      <div>
        <h1 class="pageHeader__title">
          <span>
            {{ current.meta.display }}
          </span>
        </h1>
      </div>
    </header>
    <section class="resourceInfo">
      <span class="resourceInfo__creation">
        Refreshed <TimeAgo :timestamp="current.meta.dt" />
      </span>
    </section>
    <section class="resourceDetails">
      <h2>Details</h2>
      <dl class="resourceDetails__list">
        <div class="resourceDetails__name" :class="`resourceDetails__name--${current.meta.platform}`">
          <dt>Name</dt>
          <dd v-if="current.meta.platform === 'github'"><GithubLogo /> {{ current.meta.name }}</dd>
          <dd v-if="current.meta.platform === 'k8s'"><KubernetesLogo /> {{ current.meta.name }}</dd>
          <dd v-if="current.meta.platform === 'gcp'"><GoogleCloudLogo /> {{ current.meta.name }}</dd>
          <dd v-if="current.meta.platform === 'aws'"><AwsLogo /> {{ current.meta.name }}</dd>
        </div>
        <div class="resourceDetails__type">
          <dt>Type</dt>
          <dd>{{ current.meta.kind }}</dd>
        </div>
        <div class="resourceDetails__category">
          <dt>Category</dt>
          <dd>{{ current.meta.category }}</dd>
        </div>
        <div class="resourceDetails__project" v-if="current.meta.project !== undefined">
          <dt>Project</dt>
          <dd>{{ current.meta.project }}</dd>
        </div>
        <div class="resourceDetails__region" v-if="current.meta.region !== undefined">
          <dt>Region</dt>
          <dd>{{ current.meta.region }}</dd>
        </div>
        <div class="resourceDetails__zone" v-if="current.meta.zone !== undefined">
          <dt>Zone</dt>
          <dd>{{ current.meta.zone }}</dd>
        </div>
        <div class="resourceDetails__ns" v-if="current.meta.ns !== undefined && current.meta.ns !== null && current.meta.ns !== ''">
          <dt>Namespace</dt>
          <dd>{{ current.meta.ns }}</dd>
        </div>
        <div class="resourceDetails__linkcount">
          <dt># Relations</dt>
          <dd>{{ current.links.length }}</dd>
        </div>
      </dl>
    </section>
    <section class="resourceLinks">
      <h2>Relations</h2>
      <ul class="tableList" v-if="resourceLinks.value.total !== 0">

        <li class="tableList__row tableList__row--header">
          <div
            class="tableList__cell tableList__cell--center tableList__cell--status"
          ></div>
          <div class="tableList__cell">Name</div>
          <div class="tableList__cell">Type</div>
          <div class="tableList__cell">Usage</div>
          <div class="tableList__cell">Tags</div>
        </li>
        <ResourceLinkPreview
          v-for="(l, index) in resourceLinks.value.links"
          :key="index"
          :link="(l as SnapshotDiscoveryLinkInfo)"
        />
      </ul>
    </section>
    <section class="resourceView__diff">
      <h2>History</h2>
      <div class="resourceDiff">
          <div class="resourceDiffToggle">
            <input
              type="checkbox"
              id="resourceDiffModeSwitch"
              v-model="diffMode"
            />
            <label for="resourceDiffModeSwitch">Side by side</label>
          </div>
          <div class="resourceDiff__code">
            <CodeDiff
              :old-string="previousString"
              :new-string="currentString"
              :output-format="diffOutputFormat"
              language="yaml"
              :newFilename=currentFileName
              :filename=previousFileName
              forceInlineComparison=true
            />
          </div>
      </div>
    </section>
  </article>
  <NoData v-else message="We couldn't find any resource with this ID." />
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { CodeDiff } from 'v-code-diff'
import * as yaml from "js-yaml";
import type { SnapshotDiscoveryResource, SnapshotDiscoveryLink, SnapshotDiscoveryLinkInfo } from "@/types/snapshots";
import { useStore } from "@nanostores/vue";

import { previous, resource, resourceLinks, fetchResource, fetchPreviousResource, fetchResourceLinksInfo } from "@/stores/snapshots";

import ResourceLinkPreview from "@/components/snapshots/ResourceLinkPreview.vue";
import LoadingPlaceholder from "@/components/_ui/LoadingPlaceholder.vue";
import NoData from "@/components/_ui/NoData.vue";
import TimeAgo from "@/components/_ui/TimeAgo.vue";
import Pager from "@/components/_ui/Pager.vue";
import type { PagerData } from "@/types/pager";

import GithubLogo from "@/components/svg/GithubLogo.vue";
import AwsLogo from "@/components/svg/AwsLogo.vue";
import GoogleCloudLogo from "@/components/svg/GoogleCloudLogo.vue";
import KubernetesLogo from "@/components/svg/KubernetesLogo.vue";

const isLoading = ref(true);
const id = ref<string | undefined>(undefined);
const current = ref<SnapshotDiscoveryResource | undefined>(undefined);

const diffMode = ref<boolean>(false);
const linksInfoPagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});

const diffOutputFormat = computed<string>(() => {
  if (diffMode.value === true) {
    return "side-by-side";
  } else {
    return "line-by-line";
  }
});

const previousFileName = computed<string>(() => {
  if (previous.value !== undefined && previous.value !== null) {
    return `Previous ${previous.value?.meta.dt}`;
  } else {
    return "";
  }
});

const previousString = computed<string>(() => {
  if (previous.value !== undefined && previous.value !== null) {
    return yaml.dump(previous.value.struct, {indent: 1});
  } else {
    return "";
  }
});

const currentFileName = computed<string>(() => {
  if (previous.value !== undefined && previous.value !== null) {
    return `Current ${current.value?.meta.dt}`;
  } else {
    return "";
  }
});

const currentString = computed<string>(() => {
  if (previous.value !== undefined) {
    return yaml.dump(current.value.struct, {indent: 1});
  } else {
    return "";
  }
});

const getCurrentId = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("id")) {
    id.value = params.get("id")!;
  }
};

const getResource = async () => {
  await fetchResource(id.value!);
  await fetchResourceLinksInfo(id.value!, 1);
  await fetchPreviousResource(id.value!);
  current.value = resource.get() as SnapshotDiscoveryResource;
};

onMounted(async () => {
  isLoading.value = true;
  getCurrentId();
  await getResource();
  isLoading.value = false;
});
</script>

<style lang="scss" scoped>
.resourceView {
  > section + section {
    margin-top: var(--space-large);
  }

  .resourceInfo {
    margin-bottom: var(--space-large);
  }

  .resourceDetails {
    dl {
      display: flex;
      margin: 0;
      padding: var(--space-small);

      background-color: var(--section-background);
      border-radius: var(--border-radius-m);

      > div {
        flex: 1 0 auto;
        padding-right: var(--space-small);
      }

      > div + div {
        padding-left: var(--space-small);

        border-left: 1px solid var(--section-separator-color);
      }

      dt {
        color: var(--text-color-dim);
        font-size: 1.4rem;
        text-transform: uppercase;
      }

      dd {
        svg {
          height: 2.4rem;

          vertical-align: -0.6rem;
        }
      }
    }

    &__name {
      &--k8s {
        svg {
          color: hsl(220, 72%, 53%);
        }
      }
    }
  }
}

.resourceDiff {
  position: relative;

  &__code {
    position: relative;

    &::before {
      content: "";

      position: absolute;
      top: 0;
      left: 2.2rem;

      display: block;
      height: 100%;
      width: 0.2rem;

      background-color: var(--grey-200);

      @media (min-width: 44rem) {
        left: calc(50% - 0.1rem);
      }
    }
  }

  .resourceDiffToggle {
    position: absolute;
    top: calc(-5rem - var(--space-small));
    right: 0;

    display: none;

    @media (min-width: 44rem) {
      display: block;
    }

    input {
      height: 0;
      width: 0;
      visibility: hidden;
    }

    label {
      position: relative;

      display: block;
      height: 2.5rem;
      width: 5rem;
      padding-top: 0.2rem;

      background-color: var(--grey-400);
      border-radius: 2.5rem;
      cursor: pointer;

      color: var(--text-color-dim);
      font-size: 1.4rem;
      text-indent: -10rem;

      &::after {
        content: "";

        position: absolute;
        top: 0.25rem;
        left: 0.25rem;

        width: 2rem;
        height: 2rem;

        background-color: white;
        border-radius: 50%;
        transition: 0.3s;
      }
    }

    input:checked + label {
      background: var(--pink-500);

      &::after {
        left: calc(100% - 0.25rem);
        transform: translateX(-100%);
      }
    }

    label:active:after {
      width: 3rem;
    }
  }
}
</style>
