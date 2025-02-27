<template>
  <form class="form">
    <template v-if="type === 'variable'">
      <div class="inputWrapper">
        <label for="varName">Name</label>
        <input type="text" id="varName" name="varName" v-model="varName" />
      </div>
      <div class="inputWrapper">
        <label for="varName">Value</label>
        <input type="text" id="varValue" name="varValue" v-model="varValue" />
      </div>
    </template>
    <template v-else-if="type === 'secret'">
      <div class="inputWrapper">
        <label :for="secretType">Type</label>
        <select v-model="secretType" :id="secretType" :name="secretType">
          <option value="var">Variable</option>
          <option value="path">Path</option>
        </select>
      </div>
      <div v-if="secretType === 'var'" class="inputWrapper">
        <label for="secretName">Name</label>
        <input
          type="text"
          id="secretName"
          name="secretName"
          v-model="secretNamePath"
        />
      </div>
      <div v-if="secretType === 'path'" class="inputWrapper">
        <label for="secretPath">Path</label>
        <input
          type="text"
          id="secretPath"
          name="secretPath"
          v-model="secretNamePath"
        />
      </div>
      <div v-if="secretType === 'var'" class="inputWrapper">
        <label for="secretVarValue">Value</label>
        <input
          type="text"
          id="secretVarValue"
          name="secretVarValue"
          v-model="secretValue"
        />
      </div>
      <div v-else-if="secretType === 'path'" class="inputWrapper">
        <label for="secretPathValue">Value</label>
        <textarea
          id="secretPathValue"
          name="secretPathValue"
          placeholder="Paste file content"
          v-model="secretValue"
        />
      </div>
    </template>
    <div class="inputWrapper">
      <button @click.prevent="cancel" class="button">Cancel</button>
      <button
        @click.prevent="proceed"
        class="button button--creative"
        :disabled="varValue === '' && secretValue === ''"
      >
        Save
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { toRefs, ref } from "vue";
import { generateKey } from "@/utils/strings";
import type { Secret, Var } from "@/types/environments";
import {
  updateEnvironmentSecretVar,
  fetchEnvironment,
} from "@/stores/environments";

const props = defineProps<{
  type: "secret" | "variable";
  env: string;
}>();
const { type, env } = toRefs(props);

const emit = defineEmits<{
  (e: "close"): void;
  (e: "refresh-environment"): void;
}>();
const cancel = () => {
  emit("close");
};

const varName = ref<string>("");
const varValue = ref<string>("");

const secretType = ref<"var" | "path">("var");
const secretNamePath = ref<string>("");
const secretValue = ref<string>("");

const proceed = async () => {
  let payload: Secret | Var | null = null;
  if (type.value === "secret") {
    if (secretType.value === "var") {
      payload = {
        key: generateKey(32),
        var_name: secretNamePath.value.trim(),
        value: secretValue.value,
      };
    } else {
      payload = {
        key: generateKey(32),
        path: secretNamePath.value.trim(),
        value: secretValue.value,
      };
    }
  } else {
    payload = {
      var_name: varName.value.trim(),
      value: varValue.value,
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
