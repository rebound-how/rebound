<template>
  <section class="dashboardActions">
    <h2 class="screen-reader-text">Suggestions</h2>
    <AiBuilder :is-small="true" />
    <a
      href="/experiments/workflows/"
      class="dashboardAction dashboardAction--starter"
    >
      <div class="dashboardAction__content">
        <h3>Experiments Builder</h3>
        <p>Kickstart your reliability journey</p>
      </div>
      <div class="dashboardAction__icon"><ZapIcon /></div>
    </a>
    <a href="/plans/new/" class="dashboardAction dashboardAction--plan">
      <div class="dashboardAction__content">
        <h3>Create a plan</h3>
        <p>Set up and schedule an experiment to start exploring</p>
      </div>
      <div class="dashboardAction__icon"><CalendarIcon /></div>
    </a>
    <a
      href="/integrations/new/"
      class="dashboardAction dashboardAction--integrations"
    >
      <div class="dashboardAction__content">
        <h3>Add integrations</h3>
        <p>Integrate Reliably with your current tooling</p>
      </div>
      <div class="dashboardAction__icon"><SettingsIcon /></div>
    </a>
  </section>
</template>

<script setup lang="ts">
import AiBuilder from "@/components/scenarios/AiBuilder.vue";

import UserPlus from "@/components/svg/UserPlus.vue";
import ZapIcon from "@/components/svg/ZapIcon.vue";
import CalendarIcon from "@/components/svg/CalendarIcon.vue";
import SettingsIcon from "@/components/svg/SettingsIcon.vue";
</script>

<style lang="scss">
.dashboardActions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-medium);
  grid-column: 1 / span 2;

  .dashboardAction {
    display: flex;
    align-items: center;
    padding: var(--space-small);

    background-color: var(--actionBackground);
    border-radius: var(--border-radius-s);

    color: var(--actionText);

    &__icon {
      display: grid;
      place-content: center;
      flex: 1 0 auto;
      height: 3.6rem;
      width: 3.6rem;

      background-color: var(--actionText);
      border-radius: 50%;

      color: var(--actionBackground);

      svg {
        height: 2rem;
      }
    }

    &__content {
      padding-right: var(--space-small);

      h3 {
        margin-bottom: 0;
      }
    }

    &:hover {
      text-decoration: none;

      background-color: var(--actionBackgroundHover);

      color: var(--actionTextHover);

      .dashboardAction__icon {
        // background-color: var(--actionIconBackgroundHover);

        color: var(--actionIconHover);
        // transform: scale(1.2);
      }
    }

    &--invite {
      --actionBackground: var(--purple-100);
      --actionBackgroundHover: var(--purple-500);
      --actionText: var(--purple-900);
      --actionTextHover: white;
      --actionIconHover: var(--purple-100);
    }

    &--starter {
      --actionBackground: var(--pink-100);
      --actionBackgroundHover: var(--pink-500);
      --actionText: var(--pink-900);
      --actionTextHover: white;
      --actionIconHover: var(--pink-100);
    }

    &--plan {
      --actionBackground: var(--blue-100);
      --actionBackgroundHover: var(--blue-800);
      --actionText: var(--blue-900);
      --actionTextHover: white;
      --actionIconHover: var(--blue-100);
    }

    &--integrations {
      --actionBackground: var(--yellow-200);
      --actionBackgroundHover: var(--yellow-500);
      --actionText: var(--yellow-900);
      --actionTextHover: var(--yellow-900);
      --actionIconHover: var(--yellow-500);
    }
  }
}
</style>
