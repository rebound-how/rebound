<template>
    <ul class="tableList">
      <li class="tableList__row tableList__row--header">
        <div class="tableList__cell">Type</div>
        <div class="tableList__cell">Events</div>
        <div class="tableList__cell">Context</div>
      </li>
      <template v-for="channel in activeChannels">
        <li v-if="channel.type==='email'" class="tableList__row">
            <div class="tableList__cell">Email</div>
            <div v-if="eventTypes !== undefined" class="tableList__cell">{{ eventTypes }}</div>
            <div v-else class="tableList__cell">-</div>
            <div v-if="channel.addresses !== undefined" class="tableList__cell">{{ channel.addresses.value }}</div>
        </li>
        <li v-else-if="channel.type==='webhook'" class="tableList__row">
            <div class="tableList__cell">WebHook</div>
            <div v-if="eventTypes !== undefined" class="tableList__cell">{{ eventTypes }}</div>
            <div v-else class="tableList__cell">-</div>
            <div v-if="channel.url !== undefined" class="tableList__cell">{{ channel.url.value }} </div>
        </li>
      </template>
    </ul>
</template>

<script setup lang="ts">
import { toRefs, computed } from "vue";

import type { Environment, Secret, Var } from "@/types/environments";

const props = defineProps<{
    settings: Environment;
}>();

const { settings } = toRefs(props);

const activeChannels = computed<[{
    type: string,
    addresses?: Var,
    url?: Var,
    token?: Secret,
}]>(() => {
    const channels = [];

    if (withEmail.value) {
        channels.push({
            type: "email",
            addresses: emailAddresses.value
        });
    }

    if (withWebHook.value) {
        channels.push({
            type: "webhook",
            url: webhookUrl.value,
            token: webhookToken.value
        });
    }

    return channels;
})

const withEmail = computed<boolean>(() => {
    return settings.value.envvars.find((v) => v.var_name === "RELIABLY_NOTIFICATION_USE_EMAIL") !== undefined;
});

const eventTypes = computed<string>(() => {
    const v = settings.value.envvars.find((v) => v.var_name === "RELIABLY_NOTIFICATION_EVENT_TYPES");
    if (v === undefined) {
        return "-";
    }

    const value = v.value;

    if (value == "plan-phases") {
        return "Plan Phases"
    }

    return "-";
});

const emailAddresses = computed<Var | undefined>(() => {
    return settings.value.envvars.find((v) => v.var_name === "RELIABLY_NOTIFICATION_TO_ADDRESSES");
});

const withWebHook = computed<boolean>(() => {
    return settings.value.envvars.find((v) => v.var_name === "RELIABLY_NOTIFICATION_USE_WEBHOOK") !== undefined;
});

const webhookUrl = computed<Var | undefined>(() => {
    return settings.value.envvars.find((v) => v.var_name === "RELIABLY_NOTIFICATION_WEBHOOK_URL");
});

const webhookToken = computed<Secret | undefined>(() => {
    return settings.value.secrets.find((v) => v.var_name === "RELIABLY_NOTIFICATION_WEBHOOK_BEARER_TOKEN");
});

</script>
