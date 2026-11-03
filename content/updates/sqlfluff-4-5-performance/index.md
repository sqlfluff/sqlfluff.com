---
title: 'Less waiting for SQLFluff: performance improvements in 4.5'
description: SQLFluff 4.5.0 cuts repeated work in layout rules, reduces per-file overhead and makes parallel runs more efficient.
date: 2026-11-03T09:00:00Z
draft: true
---

Linting should help you keep moving. Whether you're checking a change before a
commit or running SQLFluff across a project in CI, time spent waiting adds up.

[SQLFluff 4.5.0](https://github.com/sqlfluff/sqlfluff/releases/tag/4.5.0), released
on 30 October, includes a series of improvements to make that work faster.
They tackle repeated searches in layout rules, work shared between rules, the
cost of setting up each file, and communication between worker processes.

## Doing less work on the same SQL

Several layout rules previously searched the same parts of a query repeatedly.
That became particularly expensive for wide SELECT lists, long chains of CTEs
and files containing many statements or violations.

The changes replace those repeated searches with direct lookups and cached
positions. Related work also lets layout rules reuse the representation of an
unchanged file, instead of rebuilding it separately for each rule.

These changes benefit the Python implementation. The release also improves the
optional Rust engine, including allocation overhead and regex caching. You don't
need to switch engines to benefit from the Python-side improvements.

## What the measurements show

The contributing PRs include before-and-after measurements. Two examples show
where the time savings come from:

- **Reusing work between layout rules:** on a project of 565 T-SQL files, mostly
  dbt models, a parallel `fix` run fell from **25.3 seconds to 20.7 seconds**
  (18% less time). The corresponding `lint` run fell from 24.5 to 20.6 seconds.
  See [PR #8804](https://github.com/sqlfluff/sqlfluff/pull/8804).
- **Sending less data between processes:** on a project of 567 T-SQL files,
  a parallel `fix` run fell from **34.7 seconds to 27.2 seconds** (22% less
  time). See [PR #8769](https://github.com/sqlfluff/sqlfluff/pull/8769).

Both examples used Python 3.14, the Rust parser and eight worker processes.
They measure individual changes against their respective baselines, rather
than the complete 4.5.0 release against the previous release. The percentages
shouldn't be added together. Your results will depend on your SQL, rules,
templater, hardware and process settings.

There are also large reductions in individual rule timings on deliberately
large test queries. Those tests help identify scaling problems; a single
rule's speedup isn't a prediction for the runtime of an entire project.

## Try it on your project

Upgrade SQLFluff using your project's normal dependency management process.
For a standalone pip installation:

```sh
python -m pip install --upgrade sqlfluff
sqlfluff --version
sqlfluff lint path/to/your/sql
```

If SQLFluff runs through pre-commit, update the hook revision to `4.5.0`.
If you use a templater plugin, check its compatible SQLFluff version before
upgrading the environment.

To compare timings, keep the files, configuration, Python version, parser and
process count the same. Run each version more than once. A representative
project is more useful than a single unusually large query.

## More in this release

4.5.0 also brings clearer parse diagnostics, new layout options, and expanded
dialect support, including a substantial set of Databricks and SparkSQL changes.
The [release notes](https://github.com/sqlfluff/sqlfluff/releases/tag/4.5.0)
have the full details and contributor credits.

Thank you to [Josh Markovic](https://github.com/joshmarkovic),
[keraion](https://github.com/keraion), and everyone who helped implement,
test and review the performance work.

## Find out more

- [SQLFluff documentation](https://docs.sqlfluff.com/)
- [Avoiding repeated work in layout rules: #8743](https://github.com/sqlfluff/sqlfluff/pull/8743)
- [Reusing whole-file reflow sequences: #8804](https://github.com/sqlfluff/sqlfluff/pull/8804)
- [Reducing worker-process communication: #8769](https://github.com/sqlfluff/sqlfluff/pull/8769)
- [Reducing per-file setup costs: #8909](https://github.com/sqlfluff/sqlfluff/pull/8909)
