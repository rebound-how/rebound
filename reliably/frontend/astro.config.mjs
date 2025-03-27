import { defineConfig } from "astro/config";

import vue from "@astrojs/vue";
import mdx from '@astrojs/mdx';
import icon from "astro-icon";

// https://astro.build/config
export default defineConfig({
  integrations: [vue(), mdx(), icon()],
  legacy: {
    astroFlavoredMarkdown: true,
  },
  markdown: {
    shikiConfig: {
      // Choose from Shiki's built-in themes (or add your own)
      // https://github.com/shikijs/shiki/blob/main/docs/themes.md
      theme: "min-light",
      // Add custom languages
      // Note: Shiki has countless langs built-in, including .astro!
      // https://github.com/shikijs/shiki/blob/main/docs/languages.md
      langs: ["yaml", "json"],
      // Enable word wrap to prevent horizontal scrolling
      wrap: true,
    },
  },
  vite: {
    ssr: {
      external: ["svgo"],
    },
    //build: {
    //  minify: false,
    //}
  },
});
