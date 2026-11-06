---
title: 'SQLFluff 3.0: Better feedback, lower memory overhead'
description: Richer lint diagnostics, improvements for larger projects and new Vertica support arrive in SQLFluff 3.0.
date: 2024-03-12T19:41:43Z
draft: true
authors: [alanmcruickshank]
---

*Retrospective announcement, added to the Updates archive. The date above is the
original release date; this article describes the changes introduced in 3.0.0.*

SQLFluff's results often travel beyond the terminal: into code review, editor
integrations and the automation that checks a team's SQL. SQLFluff 3.0 makes those
results more useful, alongside work to reduce memory overhead on larger projects.

## More context for each linting issue

The serialised output from `sqlfluff lint`, and the corresponding API methods,
now includes more information about the span of an issue, initial proposed fixes
and statistics previously available through CSV export.

For integration authors, that provides more context for presenting a violation
and its possible correction. It also means consumers of the output need an
update: `line_no` and `line_pos` become `start_line_no` and `start_line_pos`,
distinguishing the start position from the new end-position fields.

If a script reads SQLFluff's JSON output, check those field names as part of the
upgrade. The GitHub annotation formats also change their default annotation
level from `notice` to `warning` for linting errors.

## Less memory overhead when fixing projects

3.0 changes the normal `sqlfluff fix` workflow so fixes are applied without the
old confirmation step. The previous `--force` behaviour becomes the default,
enabling reductions in memory overhead when processing larger projects.

That is a useful operational improvement, but also a behaviour change to account
for when upgrading. Run fixes in a working tree where you can inspect and review
the changes. The `--force` option itself is deprecated in this release.

## A more resilient plugin workflow

Plugins are loaded progressively, with improved error handling. If a plugin
cannot load, SQLFluff reports the problem and attempts to continue rather than
immediately stopping all work.

This makes failures easier to diagnose. It does not remove the need for a plugin
your configuration depends on: check the reported error and confirm that the
intended templater and rules are available.

## Welcome, Vertica

3.0 introduces a Vertica dialect, alongside improvements across existing
dialects. It also adds `AL09`, a rule for avoiding a column alias that simply
repeats the column's own name, and adjusts aliasing behaviour for Oracle and
`VALUES` clauses.

There is a smaller convention change to review too: `convention.not_equals`
defaults to requiring a consistent style, rather than the previous default.

## Upgrading from 2.x

The release drops Python 3.7 support. Check your Python environment, scripts that
consume lint output, and automated fix commands before changing the version used
by your project. The deprecated `--disable_progress_bar` spelling is removed;
use `--disable-progress-bar` instead.

Thank you to the community for its patience during the release cycle, and to
the 27 first-time contributors included in this release.

## Find out more

- [SQLFluff 3.0.0 release notes and contributor credits](https://github.com/sqlfluff/sqlfluff/releases/tag/3.0.0)
- [Reducing memory overhead in the fix command](https://github.com/sqlfluff/sqlfluff/pull/5653)
- [Progressive plugin loading](https://github.com/sqlfluff/sqlfluff/pull/5661)
- [Adding the Vertica dialect](https://github.com/sqlfluff/sqlfluff/pull/5640)

For a new installation today, start with the
[current documentation](https://docs.sqlfluff.com/). This article records the
3.0 release rather than recommending an older version for a new project.
