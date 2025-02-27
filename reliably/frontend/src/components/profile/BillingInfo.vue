<template>
  <div class="billing">
    <div v-if="isSuccessDisplayed" class="billingEvent billingEvent--success">
      <h2>🎉 Congratulations!</h2>
      <p>
        Your payment has been processed and your
        <span class="billingEvent__plan">{{ currentSub.plan.name }}</span>
        plan has been successfully activated!
      </p>
      <button @click.prevent="closeSuccess" class="button button--icon">
        <CloseIcon />
        <span class="screen-reader-text">Close</span>
      </button>
    </div>
    <div v-if="isFailDisplayed" class="billingEvent billingEvent--fail">
      <h2>Something went wrong</h2>
      <p>
        We couldn't process your payment.
        <a
          href="https://reliably.com/contact/"
          target="_blank"
          rel="noreferer noopener"
          >Get in touch</a
        >
        so we can fix this.
      </p>
      <button @click.prevent="closeFail" class="button button--icon">
        <CloseIcon />
        <span class="screen-reader-text">Close</span>
      </button>
    </div>

    <section class="billingCurrent">
      <p>
        Your organization <strong>{{ currentOrganizationName }}</strong> is
        currently using
        <strong class="billingCurrent__plan"
          >{{ displayedPlanName }} Plan</strong
        >
      </p>
      <button
        v-if="currentSub.plan.name === 'free'"
        @click="displayModal"
        class="button button--primary"
      >
        Switch to a paid plan
      </button>
      <button
        v-if="
          currentSub.plan.name === 'start' || currentSub.plan.name === 'scale'
        "
        @click="displayModal"
        class="button button--primary"
      >
        Upgrade
      </button>
    </section>

    <section class="billingUsage">
      <h2>Remaining Resources</h2>
      <dl>
        <div>
          <dt>Custom Experiments</dt>
          <dd v-if="isOnPrem">Unlimited</dd>
          <dd v-else v-html="remaining.experiments"></dd>
        </div>
        <div>
          <dt>
            Cloud Experiments Minutes
            <span
              class="hasTooltip hasTooltip--bottom-center"
              aria-label="Reset on each billing period"
              label="Reset on each billing period"
            >
              <HelpCircle />
            </span>
          </dt>
          <dd v-if="isOnPrem">Unlimited</dd>
          <dd v-else v-html="remaining.minutes"></dd>
        </div>
        <div>
          <dt>Team Members</dt>
          <dd v-if="isOnPrem">Unlimited</dd>
          <dd v-else v-html="remaining.members"></dd>
        </div>
      </dl>
    </section>

    <section class="billingUsers" ref="billingUsers">
      <h2>Team Members</h2>
      <ul class="usersList tableList">
        <li class="tableList__row tableList__row--header">
          <div class="tableList__cell">Username</div>
          <div class="tableList__cell">
            <span class="screen-reader-text">Actions</span>
          </div>
        </li>
        <UserPreview
          v-for="user in usersList.users"
          :user="user"
          :isRemovable="usersList.users.length > 1"
          :key="user.id"
        />
      </ul>
      <Pager v-if="usersList.total > 10" :page="pagerData" />
    </section>

    <section class="invitationLink">
      <h2>Invitation Link</h2>
      <div class="invitationLink__wrapper">
        <div class="invitationLink__link">
          <input
            type="text"
            v-model="link"
            readonly
            @click.prevent="copyLink"
          />
          <button
            class="button button--primary"
            @click.prevent="copyLink"
            :disabled="areInvitationsDisabled"
          >
            Copy to clipboard
          </button>
        </div>
        <div class="invitationLink__new">
          <h3>Generate a new link</h3>
          <p>
            Generating a new link will disable the existing link. Members who
            joined using this link will remain in your organization, but no new
            members will be able to join with the disabled link.
          </p>
          <button
            class="button button--creative"
            @click.prevent="generateNewLink()"
            :disabled="areInvitationsDisabled"
          >
            Generate new link
          </button>
        </div>
      </div>
    </section>

    <ModalWindow
      v-if="isModalDisplayed"
      :isUnlimited="true"
      :hasCloseButton="true"
      :hasPadding="false"
      @close="closeModal"
    >
      <template #title>{{ modalTitle }}</template>
      <template #content>
        <PlanUpgrade
          :from="currentSub.plan.name"
          :to="preSelectedPlan"
          @close="closeModal"
        />
      </template>
    </ModalWindow>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useClipboard } from "@vueuse/core";

import { useStore } from "@nanostores/vue";
import {
  organizationToken,
  organizationName,
  setOrganizationName,
  changeOrganization,
} from "@/stores/user";
import {
  currentSubscription,
  fetchCurrentSubscription,
} from "@/stores/subscriptions";
import {
  users,
  fetchUsers,
  invitationLink,
  getInvitationLink,
  generateInvitationLink,
} from "@/stores/organization";
import { addNotification } from "@/stores/notifications";

import type { PagerData } from "@/types/pager";

import UserPreview from "@/components/profile/UserPreview.vue";
import ModalWindow from "@/components/_ui/ModalWindow.vue";
import PlanUpgrade from "@/components/profile/PlanUpgrade.vue";
import HelpCircle from "@/components/svg/HelpCircle.vue";
import CloseIcon from "@/components/svg/CloseIcon.vue";
import Pager from "@/components/_ui/Pager.vue";

import type { RemainingForUi } from "@/types/subscriptions";
import type { Notification } from "@/types/ui-types";

const currentOrganizationId = useStore(organizationToken);
const currentOrganizationName = useStore(organizationName);
const currentSub = useStore(currentSubscription);

const isOnPrem = computed<boolean>(() => {
  return currentSub.value.plan.name === "onpremise";
});

const displayedPlanName = computed<string>(() => {
  if (currentSub.value) {
    if (isOnPrem.value) {
      return "an On-Premise";
    } else {
      return `a ${
        currentSub.value.plan.name.charAt(0).toUpperCase() +
        currentSub.value.plan.name.slice(1)
      }`;
    }
  } else {
    return "";
  }
});

const isSuccessDisplayed = ref<boolean>(false);
const isFailDisplayed = ref<boolean>(false);
function closeSuccess() {
  isSuccessDisplayed.value = false;
}
function closeFail() {
  isFailDisplayed.value = false;
}

const remaining = computed<RemainingForUi>(() => {
  const plan = currentSub.value.plan.name;

  if (plan === "free") {
    return {
      experiments: `<strong>${Math.max(
        0,
        currentSub.value.plan.remaining.experiments
      )}</strong>/5`,
      minutes: `<strong>${Math.max(
        0,
        currentSub.value.plan.remaining.minutes
      )}</strong>/180`,
      members: `<strong>${Math.max(
        0,
        currentSub.value.plan.remaining.members
      )}</strong>/1`,
    };
  } else if (plan === "start") {
    return {
      experiments: "<strong>Unlimited</strong>",
      minutes: `<strong>${Math.max(
        0,
        currentSub.value.plan.remaining.minutes
      )}</strong>/300`,
      members: `<strong>${Math.max(
        0,
        currentSub.value.plan.remaining.members
      )}</strong>/3`,
    };
  } else if (plan === "scale") {
    return {
      experiments: "<strong>Unlimited</strong>",
      minutes: "<strong>Unlimited</strong>",
      members: `<strong>${Math.max(
        0,
        currentSub.value.plan.remaining.members
      )}</strong>/5`,
    };
  } else {
    return {
      experiments: Math.max(
        0,
        currentSub.value.plan.remaining.experiments
      ).toString(),
      minutes: Math.max(0, currentSub.value.plan.remaining.minutes).toString(),
      members: Math.max(0, currentSub.value.plan.remaining.members).toString(),
    };
  }
});

const usersList = useStore(users);
const usersPage = ref<number>(1);
const billingUsers = ref(null); // The template element
const pagerData = ref<PagerData>({
  currentPage: 1,
  lastPage: 1,
  urlBase: "",
});

async function getUsers() {
  await fetchUsers(usersPage.value);
  (billingUsers.value! as HTMLElement).scrollIntoView(true);
}

const getpagerData = () => {
  let pager: PagerData = {
    currentPage: usersPage.value!,
    lastPage: Math.ceil(usersList.value.total / 10),
    urlBase: "/settings/organization/?users=",
  };
  pagerData.value = pager;
};

const areInvitationsDisabled = computed<boolean>(() => {
  return currentSub.value.plan.name === "free";
});
const invitation = useStore(invitationLink);
const link = ref<string>("");
const { text, copy, copied, isSupported } = useClipboard();
const copyLink = () => {
  if (!areInvitationsDisabled.value) {
    copy(link.value);
    const n: Notification = {
      title: "Invitation link copied to clipboard",
      message:
        "Your invitation link has been copied to your clipboard. Go invite some teammates!",
      type: "success",
    };
    addNotification(n);
  }
};

async function generateNewLink() {
  await generateInvitationLink();
  updateDisplayedLink();
}

function updateDisplayedLink() {
  if (invitation.value.link === null) {
    link.value = "";
  } else {
    link.value = invitation.value.link;
  }
}

async function handleURLParams() {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  let subscriptionStatus: string = "";
  let subscriptionName: string = "";
  let subscriptionId: string = "";

  if (params.has("plan")) {
    isModalDisplayed.value = true;
    preSelectedPlan.value = params.get("plan")!;
  }

  if (params.has("success")) {
    subscriptionStatus = params.get("success")!;
  }

  if (params.has("org")) {
    subscriptionName = params.get("org")!;
  }
  if (params.has("orgid")) {
    subscriptionId = params.get("orgid")!;
  }

  if (params.has("users")) {
    usersPage.value = parseInt(params.get("users")!);
  }

  // Redirect if not in right organization
  if (
    subscriptionStatus !== "" &&
    subscriptionName !== "" &&
    subscriptionId !== ""
  ) {
    if (currentOrganizationId.value !== subscriptionId) {
      await changeOrganization(subscriptionId);
      location.replace(
        `/settings/organization/?success=${subscriptionStatus}&orgid=${subscriptionId}&org=${subscriptionName}`
      );
    } else {
      if (subscriptionStatus === "true") {
        isSuccessDisplayed.value = true;
      } else if (subscriptionStatus === "false") {
        isFailDisplayed.value = true;
      }
    }
  }
}

const isModalDisplayed = ref<boolean>(false);
const preSelectedPlan = ref<string>("");
function displayModal() {
  isModalDisplayed.value = true;
}
function closeModal() {
  isModalDisplayed.value = false;
}
const modalTitle = computed<string>(() => {
  if (preSelectedPlan.value !== "") {
    return "Configure your new Reliably organization";
  } else if (currentSub.value.plan.name === "free") {
    return "Switch to a paid plan";
  } else {
    return "Upgrade your plan";
  }
});

onMounted(async () => {
  await handleURLParams();
  if (currentOrganizationName.value === "") {
    await setOrganizationName();
  }
  await fetchCurrentSubscription();
  await getUsers();
  getpagerData();
  await getInvitationLink();
  updateDisplayedLink();
});
</script>

<style lang="scss">
.billing {
  .billingEvent {
    position: relative;

    margin-bottom: var(--space-medium);
    padding: var(--space-small);
    padding-right: var(--space-large);

    background-color: var(--billingEventBackgroundColor);
    border-radius: var(--border-radius-s);

    color: var(--billingEventTextColor);

    &__plan {
      text-transform: capitalize;
    }

    h2 {
      margin-bottom: 0;
    }

    a {
      color: inherit;
      text-decoration: underline;
    }

    button {
      position: absolute;
      top: 0.6rem;
      right: 0.6rem;

      background-color: var(--billingEventButtonBackground);

      color: var(--billingEventTextColor);

      &:hover {
        background-color: var(--billingEventButtonHoverBackground);
      }
    }

    &--success {
      --billingEventButtonBackground: var(--green-200);
      --billingEventButtonHoverBackground: var(--green-300);
      --billingEventTextColor: var(--green-900);
      --billingEventBackgroundColor: var(--green-200);
    }

    &--fail {
      --billingEventButtonBackground: var(--red-200);
      --billingEventButtonHoverBackground: var(--red-300);
      --billingEventTextColor: var(--red-900);
      --billingEventBackgroundColor: var(--red-200);
    }
  }

  .billingCurrent {
    display: flex;
    align-items: center;
    margin-bottom: var(--space-medium);

    color: var(--text-color-dim);
    font-size: 2.4rem;

    &__plan {
      text-transform: capitalize;
    }

    strong {
      color: var(--text-color);
    }

    button {
      margin-left: auto;
    }
  }

  .billingUsage {
    dl {
      display: flex;
      gap: var(--space-medium);
      padding: var(--space-small);
      background-color: var(--section-background);
      border-radius: var(--border-radius-s);

      > div {
        flex: 1;
      }

      > div + div {
        padding-left: var(--space-small);
        border-left: 1px solid var(--section-separator-color);
      }

      dt {
        color: var(--text-color-dim);
        font-size: 1.4rem;
        text-transform: uppercase;

        span {
          text-transform: none;

          svg {
            height: 1.4rem;
          }
        }
      }

      dd {
        strong {
          color: var(--text-color-bright);
          font-size: 2.4rem;
          font-weight: 700;
        }
      }
    }
  }

  .invitationLink {
    &__wrapper {
      padding: var(--space-small);

      background-color: var(--grey-100);
      border-radius: var(--border-radius-s);
    }

    &__link {
      display: flex;
      gap: var(--space-small);

      input {
        display: block;
        width: 100%;
        padding: 0.5em;

        background-color: white;
        border: 0.1rem solid var(--form-input-border);
        border-radius: var(--border-radius-m);

        color: var(--text-color);
        font-size: 1.6rem;

        &:focus {
          outline: 2px solid var(--form-input-focus);
        }

        &[readonly] {
          &:focus {
            outline: none;
          }
        }
      }
    }

    &__new {
      margin-top: var(--space-medium);

      h3 {
        margin-bottom: 0;
      }

      button {
        margin-top: var(--space-small);
      }
    }
  }
}
</style>
