// Full Astro Configuration API Documentation:
// https://docs.astro.build/reference/configuration-reference

// @type-check enabled!
// VSCode and other TypeScript-enabled text editors will provide auto-completion,
// helpful tooltips, and warnings if your exported object is invalid.
// You can disable this by removing "@ts-check" and `@type` comments below.

import sitemap from "@astrojs/sitemap";
import vue from "@astrojs/vue";
import mdx from "@astrojs/mdx";

// @ts-check
export default /** @type {import('astro').AstroUserConfig} */ ({
  site: "https://reliably.com",
  integrations: [
    sitemap({
      filter: (page) => !page.startsWith("https://reliably.com/docs-next"),
    }),
    vue(),
    mdx(),
  ],

  // buildOptions: {
  //   site: "https://reliably.com",
  //   sitemap: true,
  // },

  // Comment out "renderers: []" to enable Astro's default component support.
  // renderers: ["@astrojs/renderer-vue"],
  vite: {
    plugins: [],
    ssr: {
      external: ["svgo"],
    },
  },
  markdown: {
    syntaxHighlight: "prism",
  },
});
