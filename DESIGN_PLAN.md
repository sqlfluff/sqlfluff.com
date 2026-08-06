# Shared Design Plan

## Goal

Give `sqlfluff.com`, the new VitePress documentation, and the project statistics
site one coherent visual system. The legacy Sphinx documentation is outside this
work and will remain unchanged until it is replaced.

## Design ownership

This repository is the source of truth for the shared design system. The
internal, repository-local package under `packages/design/` contains:

- design tokens for colour, typography, spacing, borders, and themes;
- shared CSS for global chrome and reusable visual components;
- font configuration, logos, and icons; and
- a short contract describing common header, navigation, and footer structure.

The package will not be published to a package registry. Repository commits and
optional `design-v*` tags will version it.

Framework-specific templates will remain with their applications. The shared
package should own visual primitives, while Hugo, VitePress, and Observable keep
small local adapters for their own layouts and behaviour.

## Main site

The main site remains a Hugo site deployed by Netlify, but no longer uses Gokarna.
Small, project-owned Hugo layouts and partials now provide the site structure.
They use the shared package where appropriate and keep marketing-only structures
and styles in this repository.

## Documentation and statistics

The SQLFluff and SQLFluff Datacoves repositories will each vendor this repository
as a Git submodule, for example at `vendor/sqlfluff.com`. Each consumer will:

- pin the submodule to a reviewed commit or `design-v*` tag;
- initialise only the direct submodule, not nested submodules;
- import or copy `packages/design/` during its build; and
- keep its VitePress or Observable adapter in the consuming repository.

Design updates will be explicit pull requests which advance the submodule pointer.
Each deployed site will bundle the selected design assets, so no site depends on
`sqlfluff.com` at runtime and historical documentation retains its pinned design.

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
- Treat the vendored directory as read-only. A consumer-owned `design:sync`
  step should validate that the submodule is present and copy only the required
  assets into that application's generated build directory.
- Bundle fonts and design assets into each site, use WOFF2 with
  `font-display: swap`, and make asset paths relative to the consuming site.
- Preserve visible focus states, skip links, reduced-motion preferences, and
  semantic landmarks in every local implementation of the shared chrome.
- Add lightweight visual regression checks at representative mobile and desktop
  widths in both themes, plus automated accessibility and broken-link checks.

## Delivery order

1. Establish the shared tokens, assets, chrome, and component styles.
2. Replace Gokarna on `sqlfluff.com` and validate the design there.
3. Add this repository as a submodule of the VitePress documentation and apply its
   local adapter.
4. Add the same submodule to the statistics project and apply its local adapter.
5. Verify navigation, light and dark themes, accessibility, and responsive layouts
   across all three sites before the documentation cutover.
