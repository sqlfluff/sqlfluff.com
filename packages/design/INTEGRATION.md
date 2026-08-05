# Consumer integration

This guide is the implementation contract for consuming SQLFluff Design from a
pinned `sqlfluff.com` Git submodule. It is intentionally framework-neutral: each
application keeps its own templates and copies the shared static assets into its
build output.

## 1. Pin the source

Add this repository at a stable vendor path and commit the resulting gitlink:

```sh
git submodule add https://github.com/sqlfluff/sqlfluff.com.git vendor/sqlfluff.com
git submodule update --init vendor/sqlfluff.com
```

CI should fail clearly when the submodule is absent. Do not initialise unrelated
or nested submodules.

## 2. Copy the assets

Copy only the package's public directory into the consumer's static/public output.
For a project whose static directory is `public/`:

```sh
test -d vendor/sqlfluff.com/packages/design/static/sqlfluff-design
rsync -a --delete \
  vendor/sqlfluff.com/packages/design/static/sqlfluff-design/ \
  public/sqlfluff-design/
```

Run this as the consumer's `design:sync` step before local development and before
the production build. The deployed assets must be available at
`/sqlfluff-design/`; no application should fetch them from another SQLFluff site
at runtime.

## 3. Load the foundations

Include a theme-colour meta tag, then load the synchronous theme bootstrap before
the stylesheets. Load application/framework adapters last:

```html
<meta name="theme-color" content="#f7f8f8">
<script src="/sqlfluff-design/js/theme.js"></script>
<link rel="stylesheet" href="/sqlfluff-design/css/tokens.css">
<link rel="stylesheet" href="/sqlfluff-design/css/base.css">
<link rel="stylesheet" href="/sqlfluff-design/css/components.css">
<link rel="stylesheet" href="/assets/application-adapter.css">
```

Do not add `defer` to `theme.js`: its first pass sets `data-theme` before paint.
The script defers control and navigation event handlers until the DOM is ready.

### Brand assets and metadata

The package supplies reusable SQLFluff artwork and icons. A consumer can reference
the shared favicons directly:

```html
<link rel="icon" href="/sqlfluff-design/img/favicon.ico" sizes="any">
<link rel="icon" href="/sqlfluff-design/img/favicon-32x32.png"
  sizes="32x32" type="image/png">
<link rel="icon" href="/sqlfluff-design/img/favicon-16x16.png"
  sizes="16x16" type="image/png">
<link rel="apple-touch-icon"
  href="/sqlfluff-design/img/apple-touch-icon.png">
```

The document title, description, canonical URL, social metadata, theme-colour tag,
and web manifest remain application-owned. A manifest may point at the packaged
`android-chrome-192x192.png` and `android-chrome-512x512.png` assets, but must use
the consuming application's own name, URLs, and deployment path.

## 4. Provide semantic chrome

Templates remain consumer-owned, but shared component styles and JavaScript expect
the following stable classes and data attributes.

### Header and navigation

```html
<a class="sqlfluff-skip-link" href="#main-content">Skip to content</a>
<header class="sqlfluff-site-header" data-sqlfluff-nav>
  <div class="sqlfluff-container sqlfluff-header-inner">
    <a class="sqlfluff-brand" href="/" aria-label="SQLFluff home">
      <img src="/sqlfluff-design/img/sqlfluff-wide.png" alt="">
    </a>
    <button class="sqlfluff-nav-toggle" type="button" aria-expanded="false"
      aria-controls="sqlfluff-global-nav" data-sqlfluff-nav-toggle>
      <span class="sqlfluff-visually-hidden">Open navigation</span>
      <span></span><span></span><span></span>
    </button>
    <nav id="sqlfluff-global-nav" class="sqlfluff-nav"
      aria-label="Global navigation" data-sqlfluff-nav-menu>
      <a href="/" aria-current="page">Product</a>
      <a href="https://docs.sqlfluff.com">Docs</a>
      <a href="https://github.com/sqlfluff/sqlfluff">GitHub</a>
      <!-- Theme control goes here. -->
    </nav>
  </div>
</header>
<main id="main-content" class="sqlfluff-main"></main>
```

Set `aria-current="page"` only on the active destination. Labels, destinations,
ordering, and temporary visibility are consumer configuration, not package data.

### Theme control

```html
<div class="sqlfluff-theme-control">
  <span id="sqlfluff-theme-label" class="sqlfluff-visually-hidden">Colour theme</span>
  <div class="sqlfluff-theme-switcher" role="group"
    aria-labelledby="sqlfluff-theme-label">
    <button type="button" data-sqlfluff-theme-value="auto"
      aria-label="Use system theme" title="System theme" aria-pressed="false">
      <span class="sqlfluff-theme-icon sqlfluff-theme-icon-system" aria-hidden="true"></span>
    </button>
    <button type="button" data-sqlfluff-theme-value="light"
      aria-label="Use light theme" title="Light theme" aria-pressed="false">
      <span class="sqlfluff-theme-icon sqlfluff-theme-icon-light" aria-hidden="true"></span>
    </button>
    <button type="button" data-sqlfluff-theme-value="dark"
      aria-label="Use dark theme" title="Dark theme" aria-pressed="false">
      <span class="sqlfluff-theme-icon sqlfluff-theme-icon-dark" aria-hidden="true"></span>
    </button>
  </div>
</div>
```

The script stores `sqlfluff-theme=auto|light|dark`. On `sqlfluff.com` and its
subdomains it writes `Domain=sqlfluff.com; Path=/; SameSite=Lax; Secure` with a
one-year lifetime. Other hosts receive a host-only cookie, with `Secure` on HTTPS.
It sets `data-theme` and `data-theme-preference` on `<html>` and follows operating
system changes while the preference is `auto`.

### Buttons and social links

Use `sqlfluff-button` for a neutral command and add `sqlfluff-button-primary` for
the page's primary command. Button grouping and alignment are application layout.

Social links use semantic list markup. Repeat the item for configured destinations:

```html
<ul class="sqlfluff-social-links" aria-label="SQLFluff community links">
  <li>
    <a href="https://github.com/sqlfluff" aria-label="GitHub" title="GitHub">
      <span class="sqlfluff-social-icon sqlfluff-social-icon-github" aria-hidden="true"></span>
    </a>
  </li>
</ul>
```

Available social suffixes are `github`, `docker`, `python`, `twitter`, `bluesky`,
`linkedin`, `slack`, and `stackoverflow`.

### Footer and terminal

The shared footer expects `sqlfluff-site-footer`, a `sqlfluff-container`, an
optional `sqlfluff-footer-grid`, link groups using `sqlfluff-footer-links`, and a
legal block using `sqlfluff-footer-legal` with one paragraph per line. Footer text
and destinations remain consumer-owned.

```html
<footer class="sqlfluff-site-footer">
  <div class="sqlfluff-container">
    <div class="sqlfluff-footer-grid">
      <div>
        <p class="sqlfluff-footer-title">SQLFluff</p>
        <p class="sqlfluff-footer-copy">The SQL linter for humans.</p>
      </div>
      <nav class="sqlfluff-footer-links" aria-label="Project links">
        <a href="https://docs.sqlfluff.com">Documentation</a>
        <a href="https://github.com/sqlfluff/sqlfluff">GitHub source</a>
      </nav>
      <nav class="sqlfluff-footer-links" aria-label="Community links">
        <a href="https://github.com/sqlfluff">GitHub</a>
      </nav>
    </div>
    <div class="sqlfluff-footer-legal">
      <p>Organisation and registration details</p>
      <p>Registered address</p>
      <p>Site management and hosting credits</p>
    </div>
  </div>
</footer>
```

For terminal examples use `sqlfluff-terminal`, an optional
`sqlfluff-terminal-header`, and a `pre > code` body. Syntax accents are available
through `sqlfluff-code-yellow`, `sqlfluff-code-red`, `sqlfluff-code-blue`, and
`sqlfluff-code-muted`.

## 5. Use semantic tokens

Use shared custom properties instead of copying their current values:

- Typography: `--sqlfluff-font-sans`, `--sqlfluff-font-mono`.
- Surfaces: `--sqlfluff-color-canvas`, `--sqlfluff-color-surface`,
  `--sqlfluff-color-surface-muted`.
- Text and borders: `--sqlfluff-color-text`, `--sqlfluff-color-text-muted`,
  `--sqlfluff-color-border`, `--sqlfluff-color-border-strong`.
- Interaction: `--sqlfluff-color-accent`, `--sqlfluff-color-accent-hover`,
  `--sqlfluff-color-accent-soft`, `--sqlfluff-color-accent-contrast`,
  `--sqlfluff-color-focus`.
- Code: `--sqlfluff-color-code-*`.
- Layout: `--sqlfluff-content-width`, `--sqlfluff-reading-width`,
  `--sqlfluff-header-height`, `--sqlfluff-radius-*`, `--sqlfluff-shadow-sm`.

The package switches these values through `html[data-theme="dark"]`. Adapters
should consume the semantic role and must not maintain their own parallel palette.

## 6. Keep adapters narrow

An application adapter may:

- map framework navigation, sidebars, tables, code blocks, and search onto shared
  tokens;
- implement layouts that exist only in that application; and
- compensate for necessary framework selector specificity.

It should not redefine the shared palette, typography, header, theme switcher, or
footer. Promote a rule into the package only after it represents the same component
in at least two applications.

All shared custom properties use the `--sqlfluff-` prefix and shared classes use
`sqlfluff-`. Treat the vendored directory as read-only.

## 7. Update the pinned design

Update the submodule deliberately, review the package diff, and commit only the new
gitlink in the consumer:

```sh
git -C vendor/sqlfluff.com fetch origin
git -C vendor/sqlfluff.com checkout <reviewed-commit-or-design-tag>
git add vendor/sqlfluff.com
```

Run `design:sync`, the consumer build, and visual checks before merging. This keeps
historical deployments reproducible and lets each application adopt changes on its
own schedule.

## Verification checklist

- The three CSS files, theme script, fonts, wordmark, and referenced icons return
  `200` from the deployed origin.
- Light, dark, and automatic preferences work before and after navigation.
- The preference follows the user between production SQLFluff subdomains.
- The active navigation link is correct and the mobile menu opens, closes, and
  responds to Escape.
- Skip links and visible keyboard focus remain usable.
- Header, footer, framework content, and long text do not overlap at representative
  desktop and mobile widths.
- Reduced-motion users do not receive unnecessary animation.
- Consumer-owned links are checked for the production or beta environment in use.
