<template>
  <button
    class="ctc-button button button--small"
    :class="{ copied: displayCopyConfirmation }"
    @click="copyToClipboard"
  >
    <IconClipboard />
    {{ label }} <span class="screen-reader-text">to clipboard</span>
  </button>
</template>

<script lang="ts">
// First import this component at the begining of your markdown file.
// import CopyToClipboard from '~/components/MarkdownCopyToClipboard.vue'
//
// Then, insert this component _after_ the code block you want it to copy.
// You MUST let an empty line between the component and the code block.
// Like this:
// ```console
// reliably slo init
// ```
// <CopyToClipboard />
//

import IconClipboard from '~/assets/images/icons/clipboard.svg';

export default {
  components: {
    IconClipboard,
  },
  data() {
    return {
      label: "Copy",
      displayCopyConfirmation: false,
    }
  },
  methods: {
    async copyToClipboard(event) {
      const target = event.currentTarget.previousSibling;
      if (target != null) {
        this.selectText(target);
        document.execCommand('copy');
        target.blur();
        this.displayCopyConfirmation = true;
        this.label = "Copied!";
        await new Promise( (resolve) => {
          setTimeout(() => {
            this.displayCopyConfirmation = false;
            this.label = "Copy";
          }, 2000);
        });
      }
    },
    selectText(element) {
      // var text = document.getElementById(element);
      var range;
      var selection;
  
      if (document.body.createTextRange) { //ms
        range = document.body.createTextRange();
        range.moveToElementText(element);
        range.select();
      } else if (window.getSelection) { //all others
        selection = window.getSelection();        
        range = document.createRange();
        range.selectNodeContents(element);
        selection.removeAllRanges();
        selection.addRange(range);
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.ctc-button {
  position: absolute;
  margin-top: 1em;
  margin-left: 50%;
  transform: translate(-50%, -1em);

  // display: block;
  // height: 2em;
  // width: 2em;

  background-color: var(--yellow-500);
  // border: 2px solid red;
  opacity: 0;
  cursor: pointer;

  color: var(--body-color);
  text-shadow: none;

  transition: all .2s ease-in-out;

  svg {
    height: 1em;
    
    vertical-align: -.1rem;
  }

  &.copied {
    background-color: var(--blue-300);
  }
}
</style>

<style lang="scss">
pre:hover + .ctc-button,
.ctc-button:hover {
  opacity: 1;

  transform: translate(-50%, calc(-1em - 75%));
}
</style>
