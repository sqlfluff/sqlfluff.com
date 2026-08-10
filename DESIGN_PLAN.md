# Shared Design Plan

## Goal

Give `sqlfluff.com`, the new VitePress documentation, and the project statistics
site one coherent visual system. The legacy Sphinx documentation is outside this
work and will remain unchanged until it is replaced.

## Design ownership

[`sqlfluff-design`](https://github.com/sqlfluff/sqlfluff-design) is the source of
truth for the shared design system, in its own repository rather than living
inside `sqlfluff.com`. It contains:

- design tokens for colour, typography, spacing, borders, and themes;
- shared CSS for global chrome and reusable visual components;
- font configuration, logos, and icons; and
- a short contract describing common header, navigation, and footer structure.

The package will not be published to a package registry. Repository commits and
`design-v*` tags version it. See its
[INTEGRATION.md](https://github.com/sqlfluff/sqlfluff-design/blob/main/INTEGRATION.md)
for the submodule and Git-dependency workflows.

Framework-specific templates will remain with their applications. The shared
package should own visual primitives, while Hugo, VitePress, and Observable keep
small local adapters for their own layouts and behaviour.

## Main site

The main site remains a Hugo site deployed by Netlify, but no longer uses Gokarna.
Small, project-owned Hugo layouts and partials now provide the site structure.
They use the shared package where appropriate and keep marketing-only structures
and styles in this repository.

This repository has no Node toolchain, so it vendors `sqlfluff-design` as a Git
submodule at `vendor/sqlfluff-design`, pinned to a `design-v*` tag, and points
Hugo's `staticDir` at the vendored assets directly. No build step copies them.

## Documentation and statistics

The SQLFluff and SQLFluff Datacoves repositories both already run a Node
toolchain (VitePress and Observable respectively), so each installs
`sqlfluff-design` as a pinned Git dependency, for example
`"@sqlfluff/design": "github:sqlfluff/sqlfluff-design#design-v0.1.0"`, rather
than vendoring it as a submodule. Because the package sits at the repository
root, this resolves with npm, pnpm, and Yarn alike. Each consumer will:

- pin the dependency to a reviewed `design-v*` tag or commit;
- copy the installed package's `static/sqlfluff-design/` directory into its own
  build output as a `design:sync` step; and
- keep its VitePress or Observable adapter in the consuming repository.

Design updates will be explicit pull requests which advance the pinned tag or
commit. Each deployed site will bundle the selected design assets, so no site
depends on `sqlfluff-design`, `sqlfluff.com`, or any other SQLFluff site at
runtime, and historical documentation retains its pinned design.

The existing deployment models remain independent: Hugo on Netlify for the main
site, VitePress with the versioned R2/Netlify pipeline for documentation, and
Observable with its data export and Netlify pipeline for statistics.

## Implementation conventions

- Prefix shared custom properties and classes with `--sqlfluff-` and
  `sqlfluff-` to avoid collisions with framework styles. Application adapters
  load after the shared CSS and own only framework-specific overrides.
- Include a small shared theme bootstrap script. It reads a `sqlfluff-theme`
  cookie with `light`, `dark`, or `auto`, applies the theme to the root element
  before first paint, and keeps `auto` synchronized with the operating system.
- On SQLFluff domains, write that preference with `Domain=sqlfluff.com`,
  `Path=/`, `SameSite=Lax`, `Secure`, and a one-year lifetime so it follows the
  user between the main, docs, and statistics subdomains. Local and preview
  environments use a host-only cookie without `Secure` when necessary.
- Keep global link destinations configurable at build time so beta sites can
  link to beta peers before cutover. Navigation labels, order, active state,
  and accessibility semantics should otherwise follow the shared contract.
- Treat the vendored or installed package directory as read-only. A
  consumer-owned `design:sync` step should validate that it is present and copy
  only the required assets into that application's generated build directory.
- Bundle fonts and design assets into each site, use WOFF2 with
  `font-display: swap`, and make asset paths relative to the consuming site.
- Preserve visible focus states, skip links, reduced-motion preferences, and
  semantic landmarks in every local implementation of the shared chrome.
- Add lightweight visual regression checks at representative mobile and desktop
  widths in both themes, plus automated accessibility and broken-link checks.

## Delivery order

1. Establish the shared tokens, assets, chrome, and component styles.
2. Replace Gokarna on `sqlfluff.com` and validate the design there.
3. Extract the package to the standalone `sqlfluff-design` repository and vendor
   it back into `sqlfluff.com` as a Git submodule.
4. Install `sqlfluff-design` as a Git dependency in the VitePress documentation
   and apply its local adapter.
5. Install the same dependency in the statistics project and apply its local
   adapter.
6. Verify navigation, light and dark themes, accessibility, and responsive layouts
   across all three sites before the documentation cutover.
