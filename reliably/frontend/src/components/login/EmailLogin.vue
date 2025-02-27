<template>
  <div class="emailLogin">
    <form class="emailLoginForm form">
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': emailHasErrors }"
      >
        <label for="loginEmail">Email</label>
        <input
          type="email"
          id="loginEmail"
          name="loginEmail"
          placeholder="you@example.com"
          v-model="loginEmail"
          ref="emailInput"
          required
          @keyup.enter="captureEnter"
        />
        <ul v-if="emailHasErrors" class="inputWrapper__help list-reset">
          <li v-for="(e, index) in emailErrors" :key="index">{{ e }}</li>
        </ul>
      </div>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': passwordHasErrors }"
      >
        <label for="loginPassword">Password</label>
        <template v-if="register">
          <input
            v-if="isPasswordVisible"
            type="text"
            id="loginPassword"
            name="loginPassword"
            placeholder="••••••••"
            v-model="loginPassword"
            autocomplete="off"
            required
            @keyup.enter="captureEnter"
          />
          <input
            v-else
            type="password"
            id="loginPassword"
            name="loginPassword"
            placeholder="••••••••"
            v-model="loginPassword"
            autocomplete="new-password"
            required
            @keyup.enter="captureEnter"
          />
        </template>
        <template v-else>
          <input
            v-if="isPasswordVisible"
            type="text"
            id="loginPassword"
            name="loginPassword"
            placeholder="••••••••"
            v-model="loginPassword"
            autocomplete="off"
            required
            @keyup.enter="captureEnter"
          />
          <input
            v-else
            type="password"
            id="loginPassword"
            name="loginPassword"
            placeholder="••••••••"
            v-model="loginPassword"
            required
            @keyup.enter="captureEnter"
          />
        </template>

        <p v-if="register && passwordHasErrors" class="inputWrapper__help">
          Your password does not fulfill the requirements below.
        </p>
        <div v-if="register" class="inputWrapper__help passwordValidation">
          Your password must:
          <ul class="list-reset">
            <li :class="{ isValid: pwHas8Characters }">
              <span><CheckIcon /></span>
              be at least 8-characters long
            </li>
            <li :class="{ isValid: pwHas1LowerCase }">
              <span><CheckIcon /></span>
              contain at least 1 lower case letter [a-z]
            </li>
            <li :class="{ isValid: pwHas1UpperCase }">
              <span><CheckIcon /></span>
              contain at least 1 upper case letter [A-Z]
            </li>
            <li :class="{ isValid: pwHas1Number }">
              <span><CheckIcon /></span>
              contain at least 1 number
            </li>
            <li :class="{ isValid: pwHas1Special }">
              <span><CheckIcon /></span>
              contain at least 1 special character
              <span
                class="help hasTooltip hasTooltip--bottom-center"
                label="- + _ ! @ # $ % ^ & * . , ?"
                aria-label="- + _ ! @ # $ % ^ & * . , ?"
                ><HelpCircle
              /></span>
            </li>
          </ul>
        </div>
        <button
          type="button"
          @click.prevent="togglePasswordVisibility"
          class="revealPassword hasTooltip hasTooltip--bottom-center"
          :label="revealPasswordMessage"
          :aria-label="revealPasswordMessage"
        >
          <EyeOffIcon v-if="isPasswordVisible" />
          <EyeIcon v-else />
        </button>
      </div>
      <div
        v-if="register"
        class="inputWrapper inputWrapper--tick"
        :class="{ 'inputWrapper--error': tosHaveErrors }"
      >
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
        <p v-if="tosHaveErrors" class="inputWrapper__help">
          You must accept Reliably's terms of service.
        </p>
      </div>
      <div v-if="register" class="inputWrapper">
        <button
          type="button"
          @click.prevent="submitRegister"
          class="button button--primary"
        >
          Register
        </button>
      </div>
      <div v-else class="inputWrapper">
        <button
          type="button"
          @click.prevent="submitLogin"
          class="button button--primary"
        >
          Login
        </button>
      </div>
      <div v-if="hasApiErrors" class="inputWrapper emailLoginErrors">
        {{ apiErrorMessage }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, onMounted, watch } from "vue";

import { loginWithEmail } from "@/stores/user";
import type { LoginApiResponse, LoginAppResponse } from "@/types/user";

import EyeIcon from "@/components/svg/EyeIcon.vue";
import EyeOffIcon from "@/components/svg/EyeOffIcon.vue";
import CheckIcon from "@/components/svg/CheckIcon.vue";
import HelpCircle from "@/components/svg/HelpCircle.vue";

const props = defineProps<{
  register: boolean;
  join: boolean;
}>();
const { register, join } = toRefs(props);

const loginEmail = ref<string>("");
const emailInput = ref(null);
const loginPassword = ref<string>("");
const isPasswordVisible = ref<boolean>(false);
const revealPasswordMessage = computed<string>(() => {
  return isPasswordVisible.value ? "Hide password" : "Reveal password";
});
const acceptTOS = ref<boolean>(false);
const inviteHash = ref<string>("");

const pwHas8Characters = computed<boolean>(() => {
  return loginPassword.value.length > 7;
});
const pwHas1LowerCase = computed<boolean>(() => {
  const re = new RegExp(".*[a-z].*");
  return re.test(loginPassword.value);
});
const pwHas1UpperCase = computed<boolean>(() => {
  const re = new RegExp(".*[A-Z].*");
  return re.test(loginPassword.value);
});
const pwHas1Number = computed<boolean>(() => {
  const re = new RegExp(".*[0-9].*");
  return re.test(loginPassword.value);
});
const pwHas1Special = computed<boolean>(() => {
  const re = new RegExp(".*[-+_!@#$%^&*.,?]");
  return re.test(loginPassword.value);
});

const emailHasErrors = ref<boolean>(false);
const emailErrors = ref<string[]>([]);
const passwordHasErrors = ref<boolean>(false);
const tosHaveErrors = ref<boolean>(false);

const hasApiErrors = ref<boolean>(false);
const apiErrorMessage = ref<string>("");

function resetErrors() {
  emailHasErrors.value = false;
  emailErrors.value = [];
  passwordHasErrors.value = false;
  tosHaveErrors.value = false;
}

function handleEmailErrors() {
  (emailInput.value! as HTMLElement).addEventListener("invalid", (e) => {
    emailErrors.value.push((e.target! as HTMLObjectElement).validationMessage);
  });
}

function setInviteHash() {
  let location = window.location;
  let p = new URLSearchParams(location.search);
  if (p.has("invite")) {
    inviteHash.value = p.get("invite")!;
  }
}

function captureEnter() {
  if (register.value) {
    submitRegister();
  } else {
    submitLogin();
  }
}

async function submitLogin() {
  emailErrors.value = [];
  if (!(emailInput.value! as HTMLInputElement).checkValidity()) {
    emailHasErrors.value = true;
  } else {
    emailHasErrors.value = false;
  }
  if (!emailHasErrors.value && loginPassword.value.length > 0) {
    let loginResponse: LoginAppResponse = await loginWithEmail(
      {
        email: loginEmail.value,
        password: loginPassword.value,
        register: false,
      },
      join.value,
      inviteHash.value
    );
    if (loginResponse.status === 200) {
      hasApiErrors.value = false;
      apiErrorMessage.value = "";
      let location = window.location;
      let qsarr: string[] = [];
      let params: LoginApiResponse = loginResponse.api_response!;
      let keys = Object.keys(params) as Array<keyof LoginApiResponse>;
      keys.forEach((k: keyof LoginApiResponse) => {
        if (k === "org_id") {
          qsarr.push(`orgid=${params[k]}`);
        } else {
          qsarr.push(`${k}=${params[k]}`);
        }
      });
      const qs: string = qsarr.join("&");
      location.assign(`/authorized/?${qs}`);
    } else {
      hasApiErrors.value = true;
      apiErrorMessage.value = loginResponse.message;
    }
  }
}

async function submitRegister() {
  emailErrors.value = [];
  if (!(emailInput.value! as HTMLInputElement).checkValidity()) {
    emailHasErrors.value = true;
  } else {
    emailHasErrors.value = false;
  }
  if (
    !pwHas8Characters.value ||
    !pwHas1LowerCase.value ||
    !pwHas1UpperCase.value ||
    !pwHas1Number.value ||
    !pwHas1Special.value
  ) {
    passwordHasErrors.value = true;
  } else {
    passwordHasErrors.value = false;
  }
  if (!acceptTOS.value) {
    tosHaveErrors.value = true;
  } else {
    tosHaveErrors.value = false;
  }

  if (
    !emailHasErrors.value &&
    !passwordHasErrors.value &&
    !tosHaveErrors.value
  ) {
    let loginResponse: LoginAppResponse = await loginWithEmail(
      {
        email: loginEmail.value,
        password: loginPassword.value,
        register: true,
      },
      join.value,
      inviteHash.value
    );
    if (loginResponse.status === 200) {
      hasApiErrors.value = false;
      apiErrorMessage.value = "";
      let location = window.location;
      let qsarr: string[] = [];
      let params: LoginApiResponse = loginResponse.api_response!;
      let keys = Object.keys(params) as Array<keyof LoginApiResponse>;
      keys.forEach((k: keyof LoginApiResponse) => {
        if (k === "org_id") {
          qsarr.push(`orgid=${params[k]}`);
        } else {
          qsarr.push(`${k}=${params[k]}`);
        }
      });
      const qs: string = qsarr.join("&");
      location.assign(`/authorized/?${qs}`);
    } else {
      hasApiErrors.value = true;
      apiErrorMessage.value = loginResponse.message;
    }
  }
}

function togglePasswordVisibility() {
  isPasswordVisible.value = !isPasswordVisible.value;
}

onMounted(() => {
  handleEmailErrors();
  if (join !== undefined && join.value === true) {
    setInviteHash();
  }
});

watch(register, () => {
  resetErrors();
});
</script>

<style lang="scss" scoped>
.emailLogin {
  .inputWrapper {
    position: relative;
  }

  .revealPassword {
    position: absolute;
    right: 0.2rem;
    top: 3.6rem;

    background-color: transparent;
    border: none;
    cursor: pointer;

    color: var(--text-color);

    svg {
      height: 2.4rem;
    }
  }

  .passwordValidation {
    color: var(--text-color-dim);

    li {
      position: relative;

      padding-left: var(--space-small);

      span:first-child {
        position: absolute;
        top: 50%;
        left: 0;

        display: grid;
        place-content: center;
        height: 1.4rem;
        width: 1.4rem;

        background-color: var(--green-500);
        border-radius: 50%;
        visibility: hidden;

        color: white;

        transform: translateY(calc(-50% + 0.1rem));

        svg {
          height: 1rem;

          stroke-width: 4;
        }
      }
      &.isValid {
        color: var(--text-color);

        span {
          visibility: visible;
        }
      }

      .help {
        svg {
          height: 1.4rem;
        }
      }
    }
  }

  .emailLoginErrors {
    padding: var(--space-small);

    background-color: var(--red-100);
    border-radius: var(--border-radius-m);

    color: var(--red-800);
  }
}
</style>
