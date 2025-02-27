<template>
  <div class="tags" :class="{ form: formWrap }">
    <div class="inputWrapper">
      <label for="tags" :class="{ 'screen-reader-text': hideLabel }"
        >Tags</label
      >
      <p v-if="importMode" class="inputWrapper__help">
        This experiment does not provide tags.
      </p>
      <p class="inputWrapper__help">
        Tags provide a way of categorizing experiments. You can provide a
        comma-separated list of tags.
      </p>
      <input
        type="text"
        name="tags"
        id="tags"
        placeholder="kubernetes, openfaas, cloudnative..."
        v-model="tags"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed, watch, onMounted } from "vue";

const props = defineProps<{
  modelValue: string[];
  importMode?: boolean;
  formWrap?: boolean;
  hideLabel?: boolean;
}>();
const { modelValue, importMode, formWrap } = toRefs(props);

const emit = defineEmits(["update:modelValue"]);

const tags = ref<string>("");

const tagsArr = computed<string[]>(() => {
  let arr: string[] = [];
  if (tags.value !== "") {
    arr = tags.value.split(",").map((element) => element.trim());
  }
  return arr;
});

function handlePresetTags() {
  let str = "";
  modelValue.value.forEach((t: string) => {
    str += `${t}, `;
  });
  str = str.slice(0, -2);
  tags.value = str;
}

// Emit to parent when there's a change
watch(tagsArr, async () => {
  emit("update:modelValue", tagsArr.value);
});

onMounted(() => {
  handlePresetTags();
});
</script>

<style lang="scss" scoped>
.tags {
  margin-top: var(--space-small);
  margin-bottom: var(--space-small);
}
</style>
