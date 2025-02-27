<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 36 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="feather feather-arrow-right workflowArrow"
  >
    <line x1="5" y1="12" x2="31" y2="12"></line>
    <polyline points="24 5 31 12 24 19"></polyline>
  </svg>
</template>

<style lang="scss" scoped>
.workflowArrow {
  display: block;
  height: 1.8rem;
  margin-left: var(--workflow-arrow-spacing);

  color: var(--workflow-arrow-color);
}
</style>
