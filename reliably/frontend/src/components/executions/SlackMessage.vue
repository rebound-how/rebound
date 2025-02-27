<template>
  <div class="timelineSlackMessage">
    <h3 v-if="message.bot_profile" class="author">
      <img
        :src="message.bot_profile.icons.image_72"
        alt=""
        class="author__icon"
      />
      <span v-if="message.bot_profile" class="author__info">
        <span class="author__name">{{ message.bot_profile.name }}</span>
      </span>
    </h3>
    <h3 v-else class="author">
      <img :src="user.image" alt="" class="author__icon" />
      <span class="author__info">
        <span class="author__name">{{ longName }}</span>
      </span>
    </h3>
    <div class="info">
      <span
        class="channel"
        :style="`background-color: ${channelColor[0]}; border-color: ${channelColor[0]}; color: ${channelColor[1]}`"
      >
        {{ prefixedChannel }}
      </span>
      <span
        v-if="thread !== undefined"
        class="thread"
        :style="`border-color: ${threadColor[0]}; color: ${threadColor[0]}`"
      >
        Thread #{{ thread }}
      </span>
    </div>
    <div v-if="message.blocks" class="blocks">
      <div
        class="blocks__block"
        v-for="(b, index) in message.blocks"
        :key="index"
      >
        <div v-if="b.type === 'rich_text'">
          <div v-for="(e, index2) in b.elements" :key="index2">
            <p v-if="e.elements">
              <template v-for="(el, index3) in e.elements" :key="index3">
                <code
                  v-if="el.type === 'text' && el.style && el.style.code"
                  class="blocks__element blocks__element--text"
                  >{{ el.text }}</code
                >
                <span
                  v-else-if="el.type === 'text'"
                  class="blocks__element blocks__element--text"
                  >{{ el.text }}</span
                >
                <span
                  v-else-if="el.type === 'user'"
                  class="blocks__element blocks__element--user"
                  >{{ el.user_id }}</span
                >
                <span
                  v-else-if="el.type === 'link'"
                  class="blocks__element blocks__element--link"
                >
                  <a :href="el.url" target="_blank" rel="noopener noreferer">{{
                    el.text
                  }}</a>
                </span>
                <p
                  v-else-if="el.type === 'section'"
                  class="blocks__element blocks__element--link"
                ></p>
              </template>
            </p>
            <p v-else-if="e.text">{{ e.text }}</p>
          </div>
        </div>
        <div v-else-if="b.type === 'section'">
          <div v-if="b.text">
            <MarkdownRenderer
              v-if="b.text.type === 'mrkdwn'"
              :src="b.text.text"
            />
            <p v-else class="block__text">
              {{ b.text.text }}
            </p>
          </div>
        </div>
        <div v-else-if="b.type === 'image'">
          <img
            v-if="b.image_url"
            :src="b.image_url"
            :alt="b.alt_text"
            :height="b.image_height"
            :width="b.image_width"
          />
        </div>
      </div>
    </div>
    <div v-if="message.subtype === 'channel_join'">
      <p>
        <strong>{{ shortName }}</strong> has joined the channel.
      </p>
    </div>
    <div v-if="message.attachments" class="attachments">
      <div
        v-for="(a, index) in message.attachments"
        class="attachments__item"
        :key="index"
      >
        <div v-if="a.fields" class="attachments__fields">
          <div
            v-for="(field, index2) in a.fields"
            class="field"
            :class="{ 'field--short': field.short }"
            :key="index2"
          >
            <div class="field__title">{{ parseForBee(field.title) }}</div>
            <div v-if="isStringCode(field.value)" class="field__value">
              <span class="jsonString">{{ field.value.slice(1, -1) }}</span>
            </div>
            <div
              v-else-if="isStringLinksArray(field.value)"
              class="field__value field__value--links"
            >
              <a
                v-for="(link, index) in handleStringArray(field.value)"
                :href="link.target"
                target="_blank"
                rel="noopener noreferer"
              >
                {{ link.label }}
              </a>
            </div>
            <div v-else class="field__value">
              {{ field.value }}
            </div>
          </div>
        </div>
        <div v-else-if="a.blocks" class="attachments__blocks">
          <div v-for="(block, index2) in a.blocks" class="block" :key="index2">
            <div v-if="block.text">
              <MarkdownRenderer
                v-if="block.text.type === 'mrkdwn'"
                :src="block.text.text"
              />
              <p v-else class="block__text">
                {{ block.text.text }}
              </p>
            </div>
            <div v-else-if="block.elements">
              <div v-for="(el, index3) in block.elements" :key="index3">
                <MarkdownRenderer v-if="el.type === 'mrkdwn'" :src="el.text" />
                <p v-else class="block__text">
                  {{ el.text }}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="attachments__fallback">
          {{ a.fallback }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";
import type { SlackMessage, SlackUser } from "@/types/executions";

import MarkdownRenderer from "@/components/_ui/MarkdownRenderer.vue";

const props = defineProps<{
  message: SlackMessage;
  channel: string;
  channelIndex: number;
  user: SlackUser;
  thread?: number;
}>();
const { message, channel, channelIndex, user, thread } = toRefs(props);

const prefixedChannel = computed<string>(() => {
  if (channel.value.startsWith("#")) {
    return channel.value;
  } else {
    return `#${channel.value}`;
  }
});

const longName = computed<string>(() => {
  if (user.value.display_name) {
    return `${user.value.display_name} (${user.value.real_name})`;
  } else {
    return user.value.real_name;
  }
});

const shortName = computed<string>(() => {
  if (user.value.display_name) {
    return user.value.display_name;
  } else {
    return user.value.real_name;
  }
});

const colors: Array<[string, string]> = [
  ["#2f2d79", "#fff"], // Deep Space Rodeo
  ["#9a2381", "#fff"], // Katy Berry
  ["#62cfeb", "#000"], // Tropical Turquoise
  ["#7cd956", "#000"], // Koopa Green Shell
  ["#6f41f5", "#fff"], // Violent Violet
  ["#edde4b", "#000"], // Yellow Buzzing
  ["#eb4cc6", "#fff"], // Glamour Pink
  ["#ef8146", "#000"], // Temptatious Tangerine
];

const channelColor = computed<[string, string]>(() => {
  const index = channelIndex.value % 8;
  return colors[index];
});

const threadColor = computed<[string, string]>(() => {
  if (thread === undefined || thread.value === undefined) {
    return ["", ""];
  } else {
    const index = thread.value % 8;
    return colors[7 - index];
  }
});

function parseForBee(s: string): string {
  if (s.startsWith(":bee:")) {
    return `🐝 ${s.slice(5)}`;
  } else {
    return s;
  }
}

function isStringCode(s: string): boolean {
  if (s.startsWith("`") && s.endsWith("`")) {
    return true;
  } else {
    return false;
  }
}

function isStringLinksArray(s: string): boolean {
  const items: string[] = s.split(" | ");
  let result: boolean = true;
  items.every((item) => {
    if (item.startsWith("<http") && item.endsWith(">")) {
      return true;
    } else {
      result = false;
      return false;
    }
  });
  return result;
}

function handleStringArray(s: string): { target: string; label: string }[] {
  const links: { target: string; label: string }[] = [];
  const splitArray: string[] = s.split(" | ");
  splitArray.forEach((s) => {
    const elements = s.slice(1, -1).split("|");
    links.push({ target: elements[0], label: elements[1] });
  });
  return links;
}
</script>

<style lang="scss" scoped>
.timelineSlackMessage {
  .author {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: 0.6rem;

    font-size: 1.6rem;
    font-weight: 400;

    &__icon {
      height: 3rem;

      border-radius: var(--border-radius-s);
    }

    &__name {
      font-weight: 700;
    }
  }

  .info {
    position: absolute;
    top: var(--space-small);
    right: var(--space-small);

    display: flex;
    gap: 0.6rem;

    .thread,
    .channel {
      padding: 0 0.6rem;

      border-radius: 2.4rem;
      border-width: 0.2rem;
      border-style: solid;

      font-size: 1.2rem;
      font-weight: 500;
    }

    .thread {
      background-color: transparent;

      text-transform: uppercase;
    }
  }

  .blocks {
    &__block {
      img {
        display: block;
        height: auto;
        max-width: 100%;
        margin-bottom: var(--space-small);
      }
    }
  }

  .attachments {
    &__fields {
      .field + .field {
        margin-top: var(--space-small);
      }
      .field {
        &__title {
          color: var(--text-color-dim);
          font-size: 1.2rem;
          text-transform: uppercase;
        }

        &__value {
          &--links {
            display: flex;
            flex-wrap: wrap;
            gap: var(--space-medium);
          }
        }
      }
    }
  }
}
</style>
