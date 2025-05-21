<template>
  <div class="billing">

    <section class="billingCurrent">
      <p>
        Your organization is <strong>{{ currentOrganizationName }}</strong>
      </p>
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
          >
            Generate new link
          </button>
        </div>
      </div>
    </section>

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
import Pager from "@/components/_ui/Pager.vue";

import type { Notification } from "@/types/ui-types";

const currentOrganizationId = useStore(organizationToken);
const currentOrganizationName = useStore(organizationName);
const currentSub = useStore(currentSubscription);

const isSuccessDisplayed = ref<boolean>(false);
const isFailDisplayed = ref<boolean>(false);

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
