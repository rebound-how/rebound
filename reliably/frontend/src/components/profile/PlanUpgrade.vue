<template>
  <div class="planUpgrade">
    <form
      class="planUpgrade__form form"
      :class="{ 'planUpgrade__form--step-2': arePlansDisplayed }"
    >
      <div
        class="inputWrapper planUpgrade__organizationName"
        :class="{ 'inputWrapper--error': isNameAvailable.err !== '' }"
        v-if="from === 'free'"
      >
        <h3>Choose a name for your organization</h3>
        <div>
          <label for="organizationName">Organization name</label>
          <input
            type="text"
            name="organizationName"
            id="organizationName"
            v-model="organizationName"
            @keyup="checkAvailability"
          />
          <p v-if="isNameAvailable.err !== ''" class="inputWrapper__help">
            {{ isNameAvailable.err }}
          </p>
        </div>
        <p class="planUpgrade__help">
          Your current free organization is named after your username. When
          upgrading, you have to choose a different. Your company name, or your
          team are good options.
        </p>
        <div class="text-center">
          <button
            @click.prevent="goToPlans"
            class="button button--primary"
            :disabled="isContinueDisabled"
          >
            Continue
          </button>
        </div>
      </div>
      <div class="planUpgrade__plansWrapper">
        <h3>Select a plan</h3>
        <button
          class="button button--icon hasTooltip hasTooltip--center-right"
          aria-label="Back"
          label="Back"
          @click.prevent="goToName"
          :disabled="isBackButtonDisabled"
        >
          <ArrowLeft />
        </button>
        <ul class="planUpgrade__plans list-reset">
          <li v-if="isStartPlanDisplayed" class="planUpgradePlan">
            <input
              type="radio"
              value="start"
              id="pickStartPlan"
              name="pickStartPlan"
              v-model="selectedPlan"
            />
            <label for="pickStartPlan">
              <div class="planUpgradePlan__content">
                <div class="planUpgradePlan__name">Start</div>
                <div class="planUpgradePlan__price">
                  <span class="planUpgradePlan__currency">£</span>40
                </div>
                <div class="planUpgradePlan__billing">Billed monthly</div>
                <ul class="planUpgradePlan__features list-reset">
                  <li><CheckIcon /><strong>3</strong> team members</li>
                  <li>
                    <CheckIcon /><strong>300</strong> minutes Cloud Executions
                    per month
                  </li>
                  <li>
                    <CheckIcon /><strong>30</strong> minutes Cloud Execution
                    limit
                  </li>
                  <li>
                    <CheckIcon /><strong>Unlimited</strong> Custom Experiments
                  </li>
                  <li><CheckIcon /><strong>3</strong> Custom Templates</li>
                  <li><CheckIcon /><strong>3 months</strong> Data Retention</li>
                  <li class="unavailable">
                    <MinusIcon />
                    Email Support
                    <span class="screen-reader-text">not included</span>
                  </li>
                  <li class="unavailable">
                    <MinusIcon />
                    Private Cloud / On Prem
                    <span class="screen-reader-text">not included</span>
                  </li>
                  <li class="unavailable">
                    <MinusIcon />
                    Support SLA
                    <span class="screen-reader-text">not included</span>
                  </li>
                </ul>
              </div>
            </label>
          </li>
          <li v-if="isScalePlanDisplayed" class="planUpgradePlan">
            <input
              type="radio"
              value="scale"
              id="pickScalePlan"
              name="pickScalePlan"
              v-model="selectedPlan"
            />
            <label for="pickScalePlan">
              <div class="planUpgradePlan__content">
                <div class="planUpgradePlan__name">Scale</div>
                <div class="planUpgradePlan__price">
                  <span class="planUpgradePlan__currency">£</span>330
                </div>
                <div class="planUpgradePlan__billing">Billed monthly</div>
              </div>
              <ul class="planUpgradePlan__features list-reset">
                <li><CheckIcon /><strong>5+</strong> team members</li>
                <li>
                  <CheckIcon /><strong>Unlimited</strong> Cloud Executions per
                  month
                </li>
                <li>
                  <CheckIcon /><strong>60</strong> minutes Cloud Execution limit
                </li>
                <li>
                  <CheckIcon /><strong>Unlimited</strong> Custom Experiments
                </li>
                <li><CheckIcon /><strong>10</strong> Custom Templates</li>
                <li><CheckIcon /><strong>12 months</strong> Data Retention</li>
                <li><CheckIcon />Email Support</li>
                <li class="unavailable">
                  <MinusIcon />
                  Private Cloud / On Prem
                  <span class="screen-reader-text">not included</span>
                </li>
                <li class="unavailable">
                  <MinusIcon />
                  Support SLA
                  <span class="screen-reader-text">not included</span>
                </li>
              </ul>
            </label>
          </li>
          <li
            v-if="isEnterprisePlanDisplayed"
            class="planUpgradePlan planUpgradePlan--enterprise"
          >
            <div>
              <div class="planUpgradePlan__content">
                <div class="planUpgradePlan__name">Enterprise</div>
                <div class="planUpgradePlan__action">
                  <a
                    href="https://reliably.com/contact/"
                    target="_blank"
                    rel="noopener noreferer"
                    class="button button--secondary"
                  >
                    Contact us
                  </a>
                </div>
                <ul class="planUpgradePlan__features list-reset">
                  <li><CheckIcon /><strong>5+</strong> team members</li>
                  <li>
                    <CheckIcon /><strong>Unlimited</strong> Cloud Executions per
                    month
                  </li>
                  <li>
                    <CheckIcon /><strong>60</strong> minutes Cloud Execution
                    limit
                  </li>
                  <li>
                    <CheckIcon /><strong>Unlimited</strong> Custom Experiments
                  </li>
                  <li><CheckIcon /><strong>10</strong> Custom Templates</li>
                  <li>
                    <CheckIcon /><strong>12 months</strong> Data Retention
                  </li>
                  <li><CheckIcon />Email Support</li>
                  <li><CheckIcon />Private Cloud / On Prem</li>
                  <li><CheckIcon />Support SLA</li>
                </ul>
              </div>
            </div>
          </li>
        </ul>
        <p class="planUpgrade__plansHelp">
          Still not sure what you need? <br />
          <a
            href="https://reliably.com/pricing/"
            target="_blank"
            rel="noopener noreferer"
          >
            Check the complete list of features
          </a>
          for each plan.
        </p>
        <div class="planUpgrade__proceed text-center">
          <button
            @click.prevent="proceed"
            class="button button--primary"
            :disabled="isProceedDisabled"
          >
            Proceed to payment
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";

import { doCheckout, tryNameCandidate } from "@/stores/subscriptions";

import type { NameCandidateInternalResponse } from "@/types/subscriptions";

import ArrowLeft from "@/components/svg/ArrowLeft.vue";
import CheckIcon from "@/components/svg/CheckIcon.vue";
import MinusIcon from "@/components/svg/MinusIcon.vue";

const props = defineProps<{
  from: string;
  to: string;
}>();

const { from, to } = toRefs(props);

const organizationName = ref<string>("");
const isNameAvailable = ref<NameCandidateInternalResponse>({
  available: false,
  err: "",
});
async function checkAvailability() {
  isNameAvailable.value = await tryNameCandidate(organizationName.value);
}

const isContinueDisabled = computed<boolean>(() => {
  return organizationName.value === "" || !isNameAvailable.value.available;
});
const isBackButtonDisabled = ref<boolean>(true);
const arePlansDisplayed = ref<boolean>(false);

function goToPlans(): void {
  arePlansDisplayed.value = true;
  isBackButtonDisabled.value = false;
}
function goToName(): void {
  arePlansDisplayed.value = false;
  isBackButtonDisabled.value = true;
}

const isStartPlanDisplayed = computed<boolean>(() => {
  return from.value === "free";
});

const isScalePlanDisplayed = computed<boolean>(() => {
  return from.value === "start" || from.value === "free";
});

const isEnterprisePlanDisplayed = computed<boolean>(() => {
  return (
    from.value === "start" || from.value === "scale" || from.value === "free"
  );
});

const selectedPlan = ref<string>("");

const isProceedDisabled = computed<boolean>(() => {
  return organizationName.value === "" || selectedPlan.value === "";
});
function proceed() {
  doCheckout({
    org_name: organizationName.value,
    plan_name: selectedPlan.value,
  });
}

onMounted(() => {
  if (to.value === "start" || to.value === "scale") {
    selectedPlan.value = to.value;
  }
});
</script>

<style lang="scss" scoped>
@use "../../styles/abstracts/mixins" as *;

.planUpgrade {
  &__form {
    position: relative;
    height: 70rem;
    width: 112rem;
    overflow: hidden;

    &--step-2 {
      .planUpgrade__organizationName,
      .planUpgrade__plansWrapper {
        transform: translateX(-100%);
      }
    }
  }

  &__organizationName,
  &__plansWrapper {
    position: absolute;
    top: 0;

    padding: var(--space-small);
    width: 112rem;

    transition: transform 0.3s ease-in-out;
  }

  &__organizationName {
    left: 0;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-medium);
    height: 70rem;
    margin-right: auto;
    margin-left: auto;
    max-width: unset;

    > * {
      width: 40rem;
    }

    h3 {
      text-align: center;
    }
  }

  &__help {
    color: var(--text-color-dim);
    font-size: 1.4rem;
  }

  &__plansWrapper {
    position: relative;

    left: 112rem;
    // margin-top: var(--space-medium);
    margin-bottom: var(--space-medium);

    > h3 {
      margin-top: 0;

      // color: var(--text-color-bright);
      // font-size: 1.8rem;
      // font-weight: 500;
      text-align: center;
    }

    > button {
      position: absolute;
      top: var(--space-small);
      left: var(--space-small);
    }
  }

  &__plans {
    display: flex;
    gap: var(--space-medium);
    margin-top: var(--space-large);
  }

  .planUpgradePlan {
    --planBackgroundColor: var(--grey-100);
    --planTextColorAccent: var(--pink-500);
    --planTextColor: var(--text-color);
    --planTextColorDim: var(--text-color-dim);
    --planTextColorBright: var(--text-color-bright);

    input[type="radio"] {
      position: absolute;
      -webkit-appearance: none;
      appearance: none;

      /* Not removed via appearance */
      margin: 0;

      /* For iOS < 15 to remove gradient background */
      background-color: #fff;

      height: auto;
      width: auto;
    }

    > label,
    > div {
      position: relative;
      z-index: 2;

      display: flex;
      flex-direction: column;
      height: 100%;
      padding: var(--space-small);

      background-color: var(--planBackgroundColor);
      border-radius: var(--border-radius-m);
      cursor: pointer;

      &::after {
        @include shadow;

        border-radius: var(--border-radius-s);
      }
    }

    > label:hover {
      background-color: var(--pink-100);
    }

    input[type="radio"]:checked + label {
      outline: 0.2rem solid var(--pink-500);
    }

    input[type="radio"]:checked + label:hover {
      background-color: var(--planBackgroundColor);
    }

    &__name {
      color: var(--planTextColorAccent);
      font-size: 2.4rem;
      font-weight: 500;
      line-height: 1;
      text-align: center;
    }

    &__price {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      height: 7rem;

      color: var(--planTextColorBright);
      font-size: 6rem;
      font-weight: 700;
      text-align: center;
    }

    &__currency {
      margin-top: 2.4rem;

      color: var(--planTextColorDim);
      font-size: 1.6rem;
      font-weight: 400;
    }

    &__billing {
      margin-bottom: var(--space-small);

      color: var(--planTextColorDim);
      text-align: center;
    }

    &__action {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 11rem;
    }

    &__features {
      color: var(--planTextColor);

      li {
        position: relative;

        margin-bottom: 0.6rem;

        svg {
          position: relative;
          z-index: 3;

          height: 1.2rem;
          margin-right: 1rem;

          stroke-width: 4;

          color: var(--planBackgroundColor);
        }

        strong {
          color: var(--planTextColorAccent);
          font-weight: 500;
        }

        &::before {
          content: "";

          position: absolute;
          top: 0.3rem;
          left: -0.3rem;
          z-index: 2;

          display: block;
          height: 1.8rem;
          width: 1.8rem;

          background-color: var(--planTextColorAccent);
          border-radius: 50%;
        }

        &.unavailable {
          opacity: 0.4;

          &::before {
            background-color: var(--planTextColorDim);
          }
        }
      }
    }

    &--enterprise {
      --planBackgroundColor: var(--blue-900);
      --planTextColorAccent: var(--yellow-500);
      --planTextColor: var(--blue-100);
      --planTextColorDim: var(----blue-300);
      --planTextColorBright: white;
    }
  }

  &__plansHelp {
    margin-top: var(--space-small);
    margin-right: auto;
    margin-left: auto;
    max-width: 50rem;

    text-align: center;
  }

  &__proceed {
    margin-top: var(--space-medium);
  }
}
</style>
