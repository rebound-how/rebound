<template>
  <form class="form">
    <div class="inputWrapper">
      <label for="newValue"
        >Enter a new value for {{ type }}
        <span class="jsonString jsonString--envvar">{{
          displayedName
        }}</span></label
      >
      <textarea
        v-if="isSecretPath"
        id="newValue"
        name="newValue"
        :placeholder="`Paste new file content`"
        v-model="newValue"
      />
      <input
        v-else
        type="text"
        id="newValue"
        name="newValue"
        :placeholder="`New ${type} value`"
        v-model="newValue"
      />
    </div>
    <div class="inputWrapper">
      <button @click.prevent="cancel" class="button">Cancel</button>
      <button
        @click.prevent="proceed"
        class="button button--creative"
        :disabled="newValue === ''"
      >
        Save
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from "vue";
import type { Secret, Var } from "@/types/environments";
import { updateEnvironmentSecretVar } from "@/stores/environments";

const props = defineProps<{
  target: Secret | Var;
  type: "secret" | "variable";
  env: string;
}>();
const { target, type, env } = toRefs(props);

const newValue = ref<string>("");
const isSecretPath = computed<boolean>(() => {
  if (type.value === "secret" && (target.value as Secret).path !== undefined) {
    return true;
  } else {
    return false;
  }
});

const displayedName = computed<string>(() => {
  if (isSecretPath.value) {
    return (target.value as Secret).path!;
  } else {
    return target.value.var_name!;
  }
});

const emit = defineEmits<{
  (e: "close"): void;
  (e: "refresh-environment"): void;
}>();
const cancel = () => {
  emit("close");
};

const proceed = async () => {
  let payload: Secret | Var | null = null;
  if (type.value === "secret") {
    if (isSecretPath.value) {
      payload = {
        key: (target.value as Secret).key,
        path: (target.value as Secret).path,
        value: newValue.value,
      };
    } else {
      payload = {
        key: (target.value as Secret).key,
        var_name: (target.value as Secret).var_name,
        value: newValue.value,
      };
    }
  } else {
    payload = {
      var_name: (target.value as Var).var_name,
      value: newValue.value,
    };
  }
  let s: boolean = await updateEnvironmentSecretVar(
    payload,
    type.value,
    env.value
  );
  if (s) {
    emit("refresh-environment");
    emit("close");
  } else {
    emit("close");
  }
};
</script>

<style lang="scss" scoped>
.button + .button {
  margin-left: var(--space-small);
}
</style>
