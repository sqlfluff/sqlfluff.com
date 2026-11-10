---
title: 'SQLFluff 3.0: Points to Spans'
description: Changes to the lint output format and the default behaviour of sqlfluff fix require updates to existing integrations and workflows, but enable showing linting areas as a range of characters, not just a point.
date: 2024-03-12T19:41:43Z
authors: [alanmcruickshank]
---

SQLFluff is used both as a command-line tool and as a component inside other
applications. For an editor or code review integration, knowing where an issue
starts is useful, but it isn't enough to show which part of the SQL is affected.
The application needs the span of the issue so it can underline the relevant
text or highlight the affected area.

Before 3.0, lint results reported a point position. This release extends that
output to describe a range, and renames the existing position fields to make
clear which end of the range they represent. That change isn't backward
compatible for applications reading those fields, which is a reason for making
this a major release. It gives integrations a more useful basis for presenting
SQLFluff's findings as they develop.

There are other compatibility changes too, including the default behaviour of
`sqlfluff fix` and the end of Python 3.7 support. The output change is particularly
relevant if you're using SQLFluff to power an application.

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

For example, suppose the configured style requires uppercase keywords and the
source contains:

```sql
select 1 FROM foo;
```

Before 3.0, the relevant part of the violation record identified the start of
`select`:

```json
{
  "code": "CP01",
  "line_no": 1,
  "line_pos": 1
}
```

In 3.0, the corresponding fields describe the whole keyword:

```json
{
  "code": "CP01",
  "start_line_no": 1,
  "start_line_pos": 1,
  "end_line_no": 1,
  "end_line_pos": 7,
  "start_file_pos": 0,
  "end_file_pos": 6
}
```

These are excerpts from a single violation record; descriptions, fix details
and the surrounding response structure have been omitted. Line and column
positions start at 1, while file offsets start at 0. The end position is
exclusive: column 7 is immediately after the six characters in `select`.

An application can therefore mark the affected text directly:

```text
select 1 FROM foo;
^^^^^^
```

With only the old point position, an editor had to infer how much text to mark,
perhaps by finding the word at the cursor. The span allows it to underline the
whole keyword, shade a larger expression or show a range across multiple lines
when the reported issue covers one. These diagnostic markings can sit alongside
the editor's normal syntax colouring.

The example uses plain, untemplated SQL where the source range is known.
Integrations should still handle records without end-position fields: 3.0
only supplies a full span where it can accurately map the location to source.

Code that reads `line_no` or `line_pos` needs to switch to the new start fields.
Applications can then use the end fields when available to display a range,
falling back to the start position otherwise.

There is also a change when linting standard input without finding violations.
Previously the serialised response was an empty list. In 3.0 it contains a file
record with statistics and an empty violations list. Integrations should check
the violations for that file, rather than assuming any file record means a
linting failure.

If a script reads SQLFluff's JSON output, check those field names as part of the
upgrade. The GitHub annotation formats also change their default annotation
level from `notice` to `warning` for linting errors.

## Fixes are applied without confirmation

`sqlfluff fix` now applies fixes without asking for confirmation, making the
previous `--force` behaviour the default. This allows fixes to be applied as
files are processed, rather than retaining results while waiting for
confirmation, reducing memory overhead on larger projects.

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
