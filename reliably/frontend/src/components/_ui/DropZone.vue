<template>
  <div
    class="dropZone"
    :class="classObject"
    @drop.prevent="dropHandler"
    @dragover.prevent="dragOverHandler"
    @dragenter.prevent="dragEnterHandler"
    @dragleave.prevent="dragLeaveHandler"
  >
    <FilePlus />
    <slot></slot>
    <span>or</span>
    <div class="dropZone__browse">
      <label for="openFileBrowser">Click here to browse for a file</label>
      <input name="openFileBrowser" id="openFileBrowser" type="file" hidden />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, toRefs } from "vue";

import FilePlus from "@/components/svg/FilePlus.vue";

const props = defineProps<{
  status?: string;
}>();
const { status } = toRefs(props);

const emit = defineEmits(["files-dropped"]);

const isDropZoneActive = ref<boolean>(false);
const setActive = () => {
  isDropZoneActive.value = true;
};
const setInactive = () => {
  isDropZoneActive.value = false;
};

const classObject = computed(() => ({
  isActive: isDropZoneActive.value,
  hasFile: status !== undefined && status.value === "has-file",
  hasError: status !== undefined && status.value === "has-error",
}));

const dropHandler = (e: DragEvent) => {
  // Prevent default behavior (Prevent file from being opened)
  e.preventDefault();

  setInactive();
  if (e.dataTransfer !== null) {
    emit("files-dropped", e.dataTransfer);
  }
};

const dragOverHandler = (e: DragEvent) => {
  // Prevent default behavior (Prevent file from being opened)
  e.preventDefault();
  setActive();
};

const dragEnterHandler = (e: DragEvent) => {
  // Prevent default behavior (Prevent file from being opened)
  e.preventDefault();
  setActive();
};

const dragLeaveHandler = (e: DragEvent) => {
  // Prevent default behavior (Prevent file from being opened)
  e.preventDefault();
  setInactive();
};
</script>

<style lang="scss" scoped>
.dropZone {
  position: relative;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-small);
  flex-grow: 1;
  padding: var(--space-small);

  background-color: white;
  border: 0.1rem solid var(--form-input-border);
  border-radius: var(--border-radius-s);

  svg {
    height: 3.6rem;

    color: var(--grey-600);
  }

  &__browse {
    label {
      cursor: pointer;

      color: var(--pink-500);

      &:hover {
        text-decoration: underline;
      }
    }
  }

  &::before {
    content: "Release to drop file";

    position: absolute;
    top: -0.1rem;
    right: -0.1rem;
    bottom: -0.1rem;
    left: -0.1rem;
    z-index: 2;

    display: flex;
    align-items: center;
    justify-content: center;

    background-color: var(--blue-100);
    border: 0.2rem solid var(--blue-200);
    border-radius: var(--border-radius-s);
    opacity: 0;

    color: var(--blue-300);
    font-size: 2rem;
    font-weight: 500;

    pointer-events: none;
    transition: opacity 0.3s ease-in-out;
  }

  &.isActive {
    &::before {
      opacity: 1;
    }
  }

  &.hasFile {
    background-color: var(--green-100);
    border: 0.1rem solid var(--green-500);
    outline: 0.2rem solid var(--green-500);
    outline-offset: -0.3rem;

    svg {
      color: var(--green-400);
    }
  }

  &.hasError {
    background-color: var(--red-100);
    border: 0.1rem solid var(--red-500);
    outline: 0.2rem solid var(--red-500);
    outline-offset: -0.3rem;

    svg {
      color: var(--red-400);
    }
  }
}
</style>
