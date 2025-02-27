<template>
  <div></div>
  <section v-if="join" class="loginMessage">
    You've been invited to join an organization on Reliably
  </section>
  <section class="login" :class="{ 'login--error': hasLoginFailed }">
    <ReliablyLogo class="logo" />
    <ul class="loginOptions list-reset">
      <li :class="{ active: isLoginActive }">
        <button @click.prevent="setLoginMode('login')">Login</button>
      </li>
      <li :class="{ active: isRegisterActive }">
        <button @click.prevent="setLoginMode('register')">Register</button>
      </li>
    </ul>
    <div v-if="mode === 'oauth' || mode === 'both'">
      <div class="screen-reader-text">Login with OpenID</div>
      <form class="form">
        <div class="inputWrapper inputWrapper--tick">
          <div>
            <input
              type="checkbox"
              v-model="acceptTOS"
              id="acceptTOS"
              name="acceptTOS"
            />
            <label for="acceptTOS">
              I accept Reliably's
              <a
                href="https://reliably.com/legal/"
                target="_blank"
                rel="noopener noreferer"
              >
                Terms of Service
              </a>
            </label>
          </div>
        </div>
      </form>
      <div
        class="login__links"
        :class="{ 'login__links--disabled': !acceptTOS }"
      >
        <a
          v-if="providers && providers.includes('github')"
          :href="loginWithGitHubUrl"
          class="loginButton loginButton--github button"
        >
          <GithubLogo />
          {{ actionVerb }} with GitHub
        </a>
        <a
          v-if="providers && providers.includes('google')"
          :href="loginWithGoogleUrl"
          class="loginButton loginButton--google button"
        >
          <GoogleG />
          {{ actionVerb }} with Google
        </a>
      </div>
    </div>
    <div v-if="mode === 'both'" class="loginSeparator">or</div>
    <div v-if="mode === 'mail' || mode === 'both'">
      <div class="screen-reader-text">
        Register and login with an email address
      </div>
      <EmailLogin :register="isRegisterActive" :join="join || false" />
    </div>
    <p v-if="hasLoginFailed" class="login__error">
      We couldn't log you in. Please try again.
    </p>
  </section>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted } from "vue";

import EmailLogin from "@/components/login/EmailLogin.vue";
import GithubLogo from "@/components/svg/GithubLogo.vue";
import GoogleG from "@/components/svg/GoogleG.vue";
import ReliablyLogo from "@/components/svg/ReliablyLogo.vue";

const props = defineProps<{
  // register?: boolean;
  join?: boolean;
  mode?: string;
  providers?: string[];
}>();
const { join, mode, providers } = toRefs(props);

const loginOption = ref<string>("login");
const isLoginActive = computed<boolean>(() => {
  return loginOption.value === "login";
});
const isRegisterActive = computed<boolean>(() => {
  return loginOption.value === "register";
});
function setLoginMode(option: string) {
  if (option === "login") {
    var newUrl =
      window.location.protocol +
      "//" +
      window.location.host +
      window.location.pathname +
      `${params.value !== "" ? "?" + params.value : ""}`;
    window.history.pushState({ path: newUrl }, "", newUrl);
    loginOption.value = "login";
  } else if (option === "register") {
    var newUrl =
      window.location.protocol +
      "//" +
      window.location.host +
      window.location.pathname +
      `?register=true${params.value !== "" ? "&" + params.value : ""}`;
    window.history.pushState({ path: newUrl }, "", newUrl);
    loginOption.value = "register";
  }
  // resetErrors();
}
function getLoginMode() {
  let params = new URLSearchParams(location.search);
  if (params.has("register") && params.get("register") === "true") {
    setLoginMode("register");
  }
}

const acceptTOS = ref<boolean>(false);

const loginWithGitHubUrl = computed<string>(() => {
  return acceptTOS.value ? `/login/with/github${apiParams.value}` : "";
});

const loginWithGoogleUrl = computed<string>(() => {
  return acceptTOS.value ? `/login/with/google${apiParams.value}` : "";
});

const hasLoginFailed = ref(false);
const getLoginStatus = () => {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("s")) {
    if (params.get("s") === "failed") {
      hasLoginFailed.value = true;
    }
  }
};

const params = ref<string>("");
const apiParams = ref<string>("");

function getRedirectParameters() {
  let location = window.location;
  let p = new URLSearchParams(location.search);
  if (
    p.has("redirect_to") &&
    p.get("redirect_to") === "subscribe" &&
    p.has("plan")
  ) {
    params.value = `redirect_to=subscribe&plan=${p.get("plan")}`;
    apiParams.value = `?redirect_to=subscribe&plan=${p.get("plan")}`;
  } else if (
    p.has("redirect_to") &&
    p.get("redirect_to") === "templates" &&
    p.has("activity")
  ) {
    params.value = `redirect_to=templates&activity=${p.get("activity")}`;
    apiParams.value = `?redirect_to=templates&activity=${p.get("activity")}`;
  }
}

function getInviteParameters() {
  if (join !== undefined && join.value === true) {
    let location = window.location;
    let p = new URLSearchParams(location.search);
    if (p.has("invite")) {
      params.value = `invite=${p.get("invite")}`;
      apiParams.value = `?join=${p.get("invite")}`;
      if (localStorage.getItem("reliably:context")) {
        const u = localStorage.getItem("reliably:user");
        if (u !== null) {
          const user = JSON.parse(u);
          const picture = user.profile.picture;
          if (picture.startsWith("https://avatars.githubusercontent.com")) {
            location.replace(`/login/with/github/${apiParams.value}`);
          } else if (picture.startsWith("https://lh3.googleusercontent.com")) {
            location.replace(`/login/with/google/${apiParams.value}`);
          }
        }
      }
    } else {
      location.replace("/login/");
    }
  }
}

const actionVerb = computed<string>(() => {
  if (isRegisterActive.value) {
    return "Register";
  } else if (join !== undefined && join.value === true) {
    return "Join";
  } else {
    return "Log in";
  }
});

onMounted(() => {
  getLoginStatus();
  getRedirectParameters();
  if (join !== undefined && join.value === true) {
    getInviteParameters();
  }
  getLoginMode();
});
</script>

<style lang="scss" scoped>
.loginMessage {
  margin-bottom: var(--space-medium);
  max-width: 80rem;

  color: var(--text-color-bright);
  font-size: 3rem;
  font-weight: 700;
  text-align: center;
}

.login {
  position: relative;

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-medium);
  margin-bottom: var(--space-small);
  padding: var(--space-large);
  width: 40rem;
  max-width: 100%;

  background-color: var(--section-background);
  border-radius: var(--border-radius-m);

  color: var(--text-color-bright);

  &--error {
    background-color: var(--pink-100);
    outline: 0.2rem solid var(--pink-500);
  }

  .logo {
    width: 20rem;
  }

  .loginOptions {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-small);
    margin-bottom: var(--space-medium);
    width: 28rem;

    li {
      position: relative;

      &::after {
        content: "";

        position: absolute;
        bottom: -0.2rem;
        left: 50%;

        display: block;
        height: 0.3rem;
        width: 100%;

        background-color: var(--pink-500);
        border-radius: 0.2rem;

        transform: translateX(-50%) scaleX(0);
        transition: all 0.3s ease-in-out;
      }
      &.active {
        border-bottom-width: 0.2rem;

        &::after {
          transform: translateX(-50%) scaleX(0.5);
          transition: all 0.1s ease-in-out;
        }
      }

      &:hover {
        &::after {
          transform: translateX(-50%) scaleX(1);
          transition: all 0.1s ease-in-out;
        }
      }

      button {
        display: block;
        padding: 0.6rem var(--space-small);
        width: 100%;

        background-color: transparent;
        border: none;
        cursor: pointer;

        color: var(--text-color);
        font-size: 1.6rem;
        text-align: center;

        transition: all 0.2s ease-in-out;

        &:hover {
          color: var(--text-color-bright);
          text-decoration: none;
        }
      }
    }
  }

  .loginSeparator {
    position: relative;

    display: block;
    // height: 3.2rem;
    width: 4rem;
    margin-top: var(--space-medium);
    margin-bottom: var(--space-medium);

    // border: 0.1rem solid var(--grey-300);
    // border-radius: 50%;

    color: var(--text-color-dim);
    // font-size: 1.6rem;
    font-weight: 700;
    text-align: center;
    text-transform: uppercase;

    &::before,
    &::after {
      content: "";

      position: absolute;
      top: 50%;

      display: block;
      height: 0.1rem;
      width: 10.4rem;

      background-color: var(--grey-400);
    }

    &::before {
      left: calc(-1 * var(--space-small));

      transform: translateX(-100%);
    }

    &::after {
      left: calc(100% + var(--space-small));
    }
  }

  &__links {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-medium);
    margin-top: var(--space-medium);

    &--disabled {
      cursor: not-allowed;
    }
  }

  .loginButton {
    display: flex;
    align-items: center;

    svg {
      height: 2rem;
      margin-right: var(--space-small);
    }

    &--github {
      background-color: var(--github-background);

      color: var(--github-color);
    }

    &--google {
      background-color: var(--google-background);

      color: var(--text-color);
    }

    &[href=""] {
      opacity: 0.5;
      pointer-events: none;
    }
  }

  &__error {
    position: absolute;
    bottom: 0.2rem;

    color: var(--pink-500);
    font-weight: 500;
  }
}
</style>
