# SQLFluff Design

This internal package is the framework-neutral source of SQLFluff's shared web
styles, assets, and browser behaviour. It is consumed directly by this Hugo site
and is intended to be vendored into the documentation and statistics repositories
through a pinned Git submodule.

## Package contents

- `static/sqlfluff-design/css/tokens.css`: light and dark design tokens.
- `static/sqlfluff-design/css/base.css`: IBM Plex Sans, reset, typography, focus,
  skip-link, and reduced-motion foundations.
- `static/sqlfluff-design/css/components.css`: shared container, header,
  navigation, theme switcher, buttons, social links, terminal, and footer.
- `static/sqlfluff-design/js/theme.js`: theme preference and responsive navigation
  behaviour, delegated from the document so it also serves client-rendered
  applications, and exposing `window.sqlfluffTheme` for framework adapters.
- `static/sqlfluff-design/img/`: wordmarks, social image, favicons, and application
  icons.
- `static/sqlfluff-design/icons/`: shared interface and social icons.
- `static/sqlfluff-design/fonts/`: the self-hosted IBM Plex Sans webfonts and OFL.

## Ownership boundary

The package owns visual foundations and reusable chrome. Consuming applications
own framework templates, page content, navigation destinations and visibility,
active-route logic, metadata, manifests, and page-specific layouts and artwork.
For example, the SQLFluff homepage hero, feature grid, feature icons, and sponsor
layout remain in this Hugo application even though they use shared tokens,
buttons, and typography.

Framework-specific adapters must load after the shared styles and should not edit
vendored package files. New styles belong here only when at least two applications
need the same visual component or behaviour.

## Integration

See [INTEGRATION.md](INTEGRATION.md) for the submodule workflow, asset load order,
HTML contracts, theme cookie, adapter guidance, and verification checklist.

Repository commits, and optional `design-v*` tags once introduced, version the
package. Consumers advance their pinned submodule commit through an ordinary pull
request; no package registry or runtime dependency on `sqlfluff.com` is required.

## Licensing

IBM Plex Sans uses `font-display: swap` and retains its SIL Open Font License in
`static/sqlfluff-design/fonts/IBM-PLEX-OFL-1.1.txt`. Other asset licences and
attributions are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
