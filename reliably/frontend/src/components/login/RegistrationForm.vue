<template>
  <form class="register form">
    <div class="inputWrapper">
      <label for="username">
        Username
        <InfoBox>
          The username we received from your authentication provider (GitHub,
          Google...) will be used as your Reliably username.
        </InfoBox>
      </label>
      <input
        type="text"
        name="username"
        id="username"
        v-model="username"
        readonly
      />
    </div>
    <div class="inputWrapper">
      <label for="email">
        Email <span class="required">Required</span>
        <InfoBox v-if="hasEmail">
          <p>
            Your email will only be used by Reliably to send you alerts and
            important messages. It will not be used for marketing purposes nor
            shared with third parties.
          </p>
          <p>
            You can change it if you don't want to use this particular email
            address.
          </p>
        </InfoBox>
        <InfoBox v-else>
          <p>
            We could not retrieve an email address from your authentication
            provider.
          </p>
          <p>
            Your email will only be used by Reliably to send you alerts and
            important messages. It will not be used for marketing purposes nor
            shared with third parties.
          </p>
        </InfoBox>
      </label>
      <input type="email" name="email" id="email" v-model="email" required />
    </div>
    <div class="inputWrapper">
      <button
        @click.prevent="proceed"
        :disabled="isSubmitDisabled"
        class="button button--primary"
      >
        Register
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

import { useStore } from "@nanostores/vue";
import { user, isLoggedIn, organizationToken, tryLogin } from "@/stores/user";
import InfoBox from "@/components/_ui/InfoBox.vue";

const useUser = useStore(user);
const useIsLoggedIn = useStore(isLoggedIn);
const useOrganizationToken = useStore(organizationToken);

const context = ref<string | null>(null);
const getContext = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("context")) {
    context.value = params.get("context")!;
  }
};

const username = ref<string>(useUser.value.profile.username);
const email = ref<string>(useUser.value.profile.email);
const hasEmail = computed<boolean>(() => {
  return useUser.value.profile.email !== "";
});

const proceed = async () => {
  // update user
  await tryLogin(context.value!);
  if (useIsLoggedIn && useOrganizationToken.value) {
    location.replace("/");
  } else {
    location.replace("/login?s=failed");
  }
};

const isSubmitDisabled = computed<boolean>(() => {
  return context.value === null || username.value === "" || email.value === "";
});

onMounted(async () => {
  await getContext();
  await tryLogin(context.value!);
});
</script>

<style lang="scss" scoped>
.register {
  position: relative;

  display: flex;
  flex-direction: column;
  gap: var(--space-medium);
  padding: var(--space-medium);
  width: 40rem;
  max-width: 100%;

  background-color: var(--section-background);
  border-radius: var(--border-radius-m);

  color: var(--text-color-bright);
}
</style>
