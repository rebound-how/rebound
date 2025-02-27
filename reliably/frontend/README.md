# Welcome to the Astro UI for Reliably

## Tools Stack

### Astro

We use [Astro](https://astro.build) as our site generator.

Astro being a static site generator, we use its [Astro Islands](https://docs.astro.build/en/concepts/islands/) concept to create interactive components that fetch (and display) data from an API when needed.

### Vue + TypeScript

These interactive components are written in [Vue 3](https://vuejs.org/guide/introduction.html) with [TypeScript](https://www.typescriptlang.org/docs/). The components are written using [Composition API](https://vuejs.org/guide/extras/composition-api-faq.html).

### Nanostores

We use [Nanostores](https://github.com/nanostores/nanostores) to share state between stores and also to move logic from components to stores. Stores are where we keep data, but also where we load data from the server.

### Sass

CSS styles are written using the [Sass framework](https://sass-lang.com/documentation/) and the SCSS syntax.

### uvu + fetch-mock

We use [uvu](https://github.com/lukeed/uvu) and [uvu/assert](https://github.com/lukeed/uvu/blob/master/docs/api.assert.md) to write and run tests.

Tests are written for the stores, where all the logic lies. Let's try and keep as many things tested as we can!

When we need to mock data, we use [fetch-mock](https://www.wheresrhys.co.uk/fetch-mock/). We try to keep mock data up to date on [MockAPI](https://mockapi.io/docs).

Here's a list of the currently available endpoints:

- https://62ff903e9350a1e548e1952e.mockapi.io/api/experiments
- https://62ff903e9350a1e548e1952e.mockapi.io/api/executions
- https://62ff903e9350a1e548e1952e.mockapi.io/api/experiments/1/executions
- https://62ff903e9350a1e548e1952e.mockapi.io/api/stats

### c8 + TypeScript Coverage Report

We use [c8](https://github.com/bcoe/c8) to report our tests coverage.

We use [TypeScript Coverage Report](https://github.com/alexcanessa/typescript-coverage-report) to ensure everything is typed.

## Commands

All commands are run from the root of the project, from a terminal:

| Command                 | Action                                       |
| :---------------------- | :------------------------------------------- |
| `npm install`           | Installs dependencies                        |
| `npm run dev`           | Starts local dev server at `localhost:3000`  |
| `npm run build`         | Build your production site to `./dist/`      |
| `npm run preview`       | Preview your build locally, before deploying |
| `npm run test:coverage` | Run tests and display coverage               |
| `npm run ts-coverage`   | Display TypeScript types coverage            |

## Building a custom front-end for on-prem customers

1. Check that the file named `customers/{customer-name}/.env.frontend` exists at the repository root level
2. `npm run init-customer --customer=customer-name`
3. `npm run build`
4. The frontend files are now available in the `dist` directory

If you want to run the development server for a specific customer:

1. Check that the file named `customers/{customer-name}/.env.frontend` exists at the repository root level
2. `npm run init-customer --customer=customer-name`
3. `npm run dev`

To reset to the values used for the Reliably SaaS frontend, `npm run init-customer --customer=reliably-saas`
