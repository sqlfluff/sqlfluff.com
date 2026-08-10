![SQLFluff](https://raw.githubusercontent.com/sqlfluff/sqlfluff/main/images/sqlfluff-wide.png)

# [sqlfluff.com](http://www.sqlfluff.com/)

Website for [SQLFluff](http://www.sqlfluff.com/).

The shared visual system for the main site, documentation, and statistics site is
described in [DESIGN_PLAN.md](DESIGN_PLAN.md).

* Built with [Hugo](https://gohugo.io/).
* Uses the shared design package vendored as a Git submodule at
  [`vendor/sqlfluff-design`](https://github.com/sqlfluff/sqlfluff-design). Other
  consumers should follow its
  [integration guide](https://github.com/sqlfluff/sqlfluff-design/blob/main/INTEGRATION.md).
* Deployed with [Netlify](https://www.netlify.com/). We're also signed up to
  an *Open Source* plan with Netlify, which requires us to credit them in the
  site footer.
* Favicons generated with <https://favicon.io/>.

## Contributions

This repository is public so that hosting is free. Write access is however
locked down to a small number of people. Contributions are still very welcome.
Please raise issues and PRs for anything you normally would.

## Usage

You'll need to install `hugo` locally. See <https://gohugo.io/installation/>.

Clone with `git clone --recurse-submodules`, or after cloning run
`git submodule update --init` to fetch the shared design assets.

After installation, run `hugo server` for local development.

## Copyright and License

* [Hugo](https://gohugo.io/) is released under the
  [Apache License](https://gohugo.io/about/license/).
