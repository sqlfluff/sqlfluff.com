# dbt 2 announcement: publication checks

This is a post-release announcement draft, not a statement of current availability.
Keep the article's `draft: true` and campaign's `status = "draft"` until review is
complete. The provisional article date is 1 December 2026 at 09:00 UTC. Confirm
the actual publication date when the post is published.

## Dependencies and installation

- Confirm both source PRs are merged and their changes have shipped:
  [dbt-labs/dbt#16870](https://github.com/dbt-labs/dbt/pull/16870) and
  [sqlfluff/sqlfluff#8854](https://github.com/sqlfluff/sqlfluff/pull/8854).
- Confirm `sqlfluff-templater-dbt2` is published on PyPI and identify the matching
  SQLFluff version and Python/platform requirements.
- Replace the broad `dbt-core>=2,<3` example with the verified minimum
  trace-capable release (or explicit tested versions). A stock release reporting
  version 2.0.8 does not establish that it contains the proposed trace API.
- Run the article's install/configuration/CLI sequence in a fresh environment
  against those published packages. This has not been done: the current evidence
  uses a locally compiled PR wheel and source-built plugin packages.
- Confirm the linked release notes and final integration documentation and add
  stable release/documentation links before publication.

## Measurements and limits

- Measurements date: 7 November 2026. Same SQLFluff revision on both sides:
  `6b387685567e23167ea25a94226a5219e7471c3a`.
- Native producer: dbt `b09632e1967c93be062253b010b657c98c8e5204`, locally built
  Windows release wheel, reported version 2.0.8. Baseline: dbt Core 1.12.6 with
  dbt-duckdb 1.11.1. Python DuckDB 1.5.4 matches the native driver's declared
  version; dbt_utils is 1.3.3.
- Seven measured runs per runtime/workload/artifact condition: 168 invocations,
  3,164 individual file lints. The evidence includes exact revisions, dependency
  lists, commands, input generators, raw results, per-file phase timings and
  correctness/audit records. Machine-specific benchmark-root paths are redacted
  as `<BENCHMARK_DIR>` in the public bundle.
- The 100 final models produced equivalent query results and identical full lint
  diagnostic objects across both runtimes and all repetitions. The five ordinary
  RF02 findings on incremental models were included equally on both sides.
- Retain the disclosure about excluded loop/capture variants. The benchmarked
  consumer produced 120 extra LT02 diagnostics across ten original variants,
  including duplicate fixes. A smaller loop reproducer is included in the
  evidence. Ten compatible inline-loop variants replaced them for timing.
- Verify the current status of that source-layout issue. Update present-tense
  compatibility guidance as necessary, while preserving the historical benchmark
  exclusion. If release changes materially affect performance, rerun before
  presenting the figures as release measurements.
- These are end-to-end CLI lint timings, not dbt compile-only timings or `fix`
  benchmarks. No operating-system cache flush, multiworker or other-warehouse
  comparison was performed. Unsaved-buffer and broader adapter support should be
  checked against the final released implementation.

## Editorial review

- Confirm title, provisional date, byline and contributor acknowledgements.
- Review proposed social copy with the article; do not post before the production
  article and both runtime/plugin releases are available.
- Review the Netlify preview on desktop and a narrow screen in both themes.
- Use this PR as the story/source record; no separate issue or changes to the two
  implementation PRs are part of this announcement work.
