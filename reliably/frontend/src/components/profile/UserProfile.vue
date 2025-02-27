<template>
  <div class="userProfile">
    <div class="userProfile__user form">
      <div>
        <h2>You</h2>
        <p>Your personal information</p>
        <div class="inputWrapper">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            name="username"
            v-model="username"
            readonly
          />
        </div>
        <div class="inputWrapper">
          <label for="email">Email</label>
          <input type="text" id="email" name="email" v-model="email" readonly />
        </div>
        <p
          v-if="picture.startsWith('https://avatars.githubusercontent.com')"
          class="loginProvider"
        >
          You log in to Reliably using <GithubLogo /> <strong>GitHub</strong>
        </p>
        <p
          v-else-if="picture.startsWith('https://lh3.googleusercontent.com')"
          class="loginProvider"
        >
          You log in to Reliably using <GoogleLogo /> <strong>Google</strong>
        </p>
      </div>
      <div>
        <img v-if="picture !== ''" :src="picture" loading="lazy" alt="" />
      </div>
    </div>
    <div class="userProfile__orgs">
      <h2>Organizations</h2>
      <p>The organizations you belong to</p>
      <ul class="tableList">
        <li class="tableList__row tableList__row--header">
          <div class="tableList__cell">Name</div>
          <div class="tableList__cell">ID</div>
        </li>
        <li v-for="o in orgs" :key="o.id" class="tableList__row">
          <div class="tableList__cell">
            {{ o.name }}
            <small>Created <TimeAgo :timestamp="o.created_date" /></small>
          </div>
          <div class="tableList__cell">
            {{ o.id }}
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

import { useStore } from "@nanostores/vue";
import { user } from "@/stores/user";
import type { Organization } from "@/types/user";

import TimeAgo from "@/components/_ui/TimeAgo.vue";
import GithubLogo from "@/components/svg/GithubLogo.vue";
import GoogleLogo from "@/components/svg/GoogleG.vue";

const you = useStore(user);

const username = ref<string>("");
const email = ref<string>("");
const picture = ref<string>("");
const orgs = ref<Organization[]>([]);

onMounted(() => {
  username.value = you.value.profile.username;
  email.value = you.value.profile.email;
  picture.value = you.value.profile.picture;
  you.value.orgs.forEach((o) => {
    orgs.value.push(o);
  });
});
</script>

<style lang="scss" scoped>
.userProfile {
  &__user {
    display: flex;
    gap: var(--space-large);

    > div:first-child {
      min-width: 34rem;

      .loginProvider {
        svg {
          height: 1.6rem;
          margin-left: 0.2rem;
          vertical-align: -0.2rem;
        }
      }
    }

    img {
      display: block;
      height: 20rem;

      border: 0.1rem solid var(--profile-picture-border);
      border-radius: 50%;
    }
  }

  &__orgs {
    margin-top: var(--space-large);

    ul {
      small {
        display: block;

        color: var(--text-color-dim);
        font-size: 1.4rem;
      }
    }
  }

  h2 + p {
    margin-top: calc(-1 * var(--space-small));
    margin-bottom: var(--space-small);

    color: var(--text-color-dim);
    font-size: 1.8rem;
  }
}
</style>
