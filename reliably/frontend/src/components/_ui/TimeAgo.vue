<template>
  <time v-if="timeString !== ''" :datetime="timeString" :title="humanReadable">
    {{ timeAgo }}
  </time>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import timezone from "dayjs/plugin/timezone";

const props = defineProps<{
  timestamp: string | Date | number | undefined;
  epoch?: boolean;
}>();
const { timestamp, epoch } = toRefs(props);

const timeString = computed<string>(() => {
  if (timestamp.value !== undefined) {
    if (typeof timestamp.value === "string") {
      return timestamp.value;
    } else if (typeof timestamp.value === "number") {
      return dayjs.unix(timestamp.value).toString();
    } else {
      return timestamp.value.toDateString();
    }
  } else {
    return "";
  }
});

const timeAgo = computed<string>(() => {
  dayjs.extend(relativeTime);
  if (epoch && typeof timestamp.value === "number") {
    return dayjs.unix(timestamp.value).fromNow();
  } else {
    return dayjs(timestamp.value).fromNow();
  }
});

const humanReadable = computed<string>(() => {
  dayjs.extend(timezone);
  const browserZone = dayjs.tz.guess();
  if (epoch && typeof timestamp.value === "number") {
    return `${dayjs
      .unix(timestamp.value)
      .format("D MMMM YYYY, H:mm:ss")} - ${browserZone}`;
  } else {
    return `${dayjs(timestamp.value).format(
      "D MMMM YYYY, H:mm:ss"
    )} - ${browserZone}`;
  }
});
</script>
