---
title: 'SQLFluff 4.5: 21–35% less lint time in single-process fixture tests'
description: A release-to-release comparison finds 21–35% lower median lint times with one process on three public fixture samples. See the results, method and limits.
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

## Comparing complete releases

On 5 November, we compared **SQLFluff 4.4.0 and 4.5.0** on identical public SQL
fixtures. With one process, median total lint time fell by **21% for the ANSI
sample, 33% for Snowflake and 35% for T-SQL**, rounded to whole percentages.
With four workers, the reductions were 6%, 20% and 18%, respectively.

![Median CLI lint times for SQLFluff 4.4.0 and 4.5.0, using one process and four workers on ANSI, Snowflake and T-SQL fixture samples.](performance.png)

Each row below measures a batch of 24 files. Times include CLI startup, linting
and output; lower is better.

| Fixture sample | Processes | 4.4.0 median | 4.5.0 median | Less time |
| --- | ---: | ---: | ---: | ---: |
| ANSI | 1 | 2.59 s | 2.06 s | 21% |
| Snowflake | 1 | 4.96 s | 3.35 s | 33% |
| T-SQL | 1 | 3.58 s | 2.32 s | 35% |
| ANSI | 4 | 2.99 s | 2.81 s | 6% |
| Snowflake | 4 | 3.25 s | 2.60 s | 20% |
| T-SQL | 4 | 2.74 s | 2.25 s | 18% |

### How we measured

- **72 unique files:** 24 each from the ANSI, Snowflake and T-SQL fixtures in
  the 4.4.0 tag. We selected nonempty files up to 20,000 bytes at evenly spaced
  ranks after sorting by size and path. Selection was fixed before timing.
- **Five measured runs per release per scenario**, following one warm-up.
  Three dialect samples and two process settings make six scenarios:
  **60 measured runs and 12 warm-ups**, with warm-ups excluded from the results.
- **Identical environments:** Python 3.13.15, the Python parser, raw templater,
  default rules and matching dependency versions. Runs used an Intel Core
  i5-12400F desktop with Windows 11. No Rust engine or external templater plugin
  was installed.
- Each observation used a fresh CLI process and the same explicit configuration.
  Release order alternated across pairs. Filesystem caches were warm. We timed
  `lint` with JSON output and timing collection enabled equally in both releases.
- All selected files were processed without lexing, parsing or templating errors.
  Violation counts, codes and source locations matched between releases;
  some diagnostic wording changed.

These are **small fixture benchmarks on one desktop**, where other applications
were running. We report medians and retain every observation, including timing
outliers, in the downloadable data. The ANSI four-worker gain is small relative
to the observed variation and needs a quieter rerun before drawing a firm
conclusion. Fixture samples do not establish a speedup for a typical project,
or show that one dialect benefits more than another in general.

[Download the summary and full timing ranges](summary.csv),
[the chart as SVG](performance.svg), or
[the complete data and reproduction bundle](benchmark-evidence.zip).
The bundle includes the exact SQL inputs, checksums, configuration, dependency
pins, individual timings and a runner. We have not yet measured a real project,
Rust, dbt/Jinja rendering, autofix throughput or CI/Linux performance in this
release-to-release comparison.

## Where should the difference be most noticeable?

The clearest improvements in this experiment were the **single-process
Snowflake and T-SQL samples**: roughly 1.6 and 1.3 seconds saved per 24-file
batch. The ANSI single-process sample saved about half a second. These are
observations about the selected queries, rather than predictions based on a
dialect name.

The implementation gives us reasons to expect benefits in other workloads too.
The following are expectations to test on your project, rather than additional
measurements from this experiment:

- **Queries that keep layout rules busy.** Wide SELECT lists, many CTEs, long
  chains of statements and numerous layout violations can trigger repeated
  searches and reflow work. Removing that repetition should matter most when
  those rules account for a substantial part of the run.
- **Repeated checks across many files.** Reductions in per-file setup costs can
  accumulate across a larger lint run. Teams running the same checks frequently
  in local development or CI have more opportunities to save time.
- **Parallel runs with substantial work per batch.** Sending less data between
  processes can reduce coordination overhead. The earlier worker-process PR
  measured that on hundreds of files; our small batches do not establish the
  same benefit at project scale.

### Where might it be less visible?

- **A few tiny files.** Startup and process creation can account for much of the
  elapsed time. Four workers took longer than one process on our ANSI sample
  in both releases. More workers are not automatically better for small batches.
- **Workflows dominated by other steps.** If dbt/SQLMesh project loading,
  rendering, dependencies or other CI jobs take most of the time, faster layout
  checks affect a smaller share of the total wait. Our raw-templater results do
  not quantify those workflows.
- **Configurations doing little of the affected work.** If you disable the
  relevant layout rules, lint only a handful of changed files, or spend most of
  the run parsing rather than applying those rules, expect a different balance
  of gains. This release also includes parser changes, but we have not isolated
  their contribution here.
- **Very short runs on a busy machine.** A small absolute saving can be hard to
  distinguish from scheduling and background activity. Compare repeated runs
  on your actual workload before choosing a process count or making a claim.

## Evidence from the contributing changes

The underlying PRs provide complementary measurements on larger workloads:

- **Reusing work between layout rules:** on a project of 565 T-SQL files, mostly
  dbt models, a parallel `fix` run fell from **25.3 seconds to 20.7 seconds**
  (18% less time). See [PR #8804](https://github.com/sqlfluff/sqlfluff/pull/8804).
- **Sending less data between processes:** on a project of 567 T-SQL files,
  a parallel `fix` run fell from **34.7 seconds to 27.2 seconds** (22% less
  time). See [PR #8769](https://github.com/sqlfluff/sqlfluff/pull/8769).

Those PR measurements used Python 3.14, the Rust parser and eight workers.
They compare individual changes against their own baselines, rather than
release tags. They were not rerun as part of our fixture comparison, and their
percentages should not be added to each other or to the results above.

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
