# SQLFluff Design

This internal package is the framework-neutral source of SQLFluff's shared web
styles, assets, and browser behaviour. It is consumed directly by this Hugo site
and is intended to be vendored into the documentation and statistics repositories
through a pinned Git submodule.

The package self-hosts IBM Plex Sans in the weights used by the shared components.
The font files use `font-display: swap` and retain their SIL Open Font License in
`static/sqlfluff-design/fonts/IBM-PLEX-OFL-1.1.txt`.

## Contract

Consumer builds should copy `static/sqlfluff-design/` into their public output and
load the assets in this order:

1. `css/tokens.css`
2. `css/base.css`
3. `css/components.css`
4. an application-owned adapter stylesheet, when required

Load `js/theme.js` in the document head before the stylesheets. It applies the
shared light, dark, or automatic theme before first paint, then initializes the
segmented theme control and responsive navigation after the DOM is ready.

`components.css` also provides the reusable social-link list. Consumers supply
the semantic list markup and select an icon with a `sqlfluff-social-icon-*`
class, keeping destinations and labels in application configuration.

Shared selectors and custom properties are prefixed with `sqlfluff-`. Consumers
should treat this directory as read-only and keep framework-specific templates and
overrides in their own repositories.
