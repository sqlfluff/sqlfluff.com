---
title: 'SQLFluff 3.0: Changes to Lint Output and Fixing'
description: Changes to the lint output format and the default behaviour of sqlfluff fix require updates to existing integrations and workflows.
date: 2024-03-12T19:41:43Z
draft: true
authors: [alanmcruickshank]
---

*Retrospective announcement, added to the Updates archive. The date above is the
original release date; this article describes the changes introduced in 3.0.0.*

SQLFluff 3.0 changes the format of lint results and the default behaviour of
`sqlfluff fix`. These changes affect existing integrations and workflows, which
is why we're making this a major release.

If you consume SQLFluff's JSON or API results, you'll need to update references
to the position fields. If you run `sqlfluff fix` interactively, it will now
apply fixes without asking for confirmation. The release also drops support for
Python 3.7.

## Changes to the lint output format

The serialised output from `sqlfluff lint`, and the corresponding API methods,
now includes more information about the span of an issue, initial proposed fixes
and statistics previously available through CSV export.

To distinguish the start of a violation from its end, the existing position
fields have been renamed:

| Previous field | 3.0 field |
| --- | --- |
| `line_no` | `start_line_no` |
| `line_pos` | `start_line_pos` |

This gives integrations more information about where an issue occurs and how
it might be fixed, but code that reads the old field names needs to change.
Check scripts, editor integrations and CI tooling that consume the output.

There is also a change when linting standard input without finding violations.
Previously the serialised response was an empty list. In 3.0 it contains a file
record with statistics and an empty violations list. Integrations should check
the violations for that file, rather than assuming any file record means a
linting failure.

If a script reads SQLFluff's JSON output, check those field names as part of the
upgrade. The GitHub annotation formats also change their default annotation
level from `notice` to `warning` for linting errors.

## Fixes are applied without confirmation

3.0 changes the normal `sqlfluff fix` workflow so fixes are applied without the
old confirmation step. The previous `--force` behaviour becomes the default,
enabling reductions in memory overhead when processing larger projects.

Previously SQLFluff retained the results while waiting for confirmation. Making
the old `--force` behaviour the default allows it to apply fixes as it processes
files, reducing the amount it needs to keep in memory for a large project.

If you want the previous confirmation behaviour, use `sqlfluff fix --check`.
The `--force` option is deprecated because it is no longer needed. Review
interactive commands and automation as part of the upgrade, and run fixes in a
working tree where you can inspect the resulting changes.

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

There is a smaller convention change to review too: `convention.not_equal`
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
- [Current migration guidance for 3.x](https://docs.sqlfluff.com/en/stable/reference/release-notes#upgrading-to-3-x)
- [Reducing memory overhead in the fix command](https://github.com/sqlfluff/sqlfluff/pull/5653)
- [Progressive plugin loading](https://github.com/sqlfluff/sqlfluff/pull/5661)
- [Adding the Vertica dialect](https://github.com/sqlfluff/sqlfluff/pull/5640)

For a new installation today, start with the
[current documentation](https://docs.sqlfluff.com/). This article records the
3.0 release rather than recommending an older version for a new project.
