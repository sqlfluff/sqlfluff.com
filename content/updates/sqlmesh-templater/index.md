---
title: 'A SQLMesh templater for SQLFluff'
description: Bring SQLFluff linting to SQLMesh model SQL with a templater that understands model headers and macros.
date: 2026-11-03T08:00:00Z
draft: true
---

If your team uses SQLMesh, there's a SQLFluff integration worth a closer look:
the SQLMesh templater.

The [initial integration](https://github.com/sqlfluff/sqlfluff/pull/7722)
merged in August. It's part of the SQLFluff repository as a separate plugin,
`sqlfluff-templater-sqlmesh`, bringing SQLMesh projects into SQLFluff's linting
workflow.

## Why a dedicated templater matters

A SQLMesh model contains more than a SQL query. It can include a `MODEL` header
and macros that depend on the project. Treating the whole file as plain SQL
doesn't give the linter the context it needs.

The SQLMesh templater handles the model header separately from the query and
works with SQLMesh macros. Where it can preserve a direct relationship between
the query and your source file, SQLFluff can report lint violations at the
corresponding source positions.

That means you can bring SQLFluff's configurable SQL style checks to model SQL,
using the dialect and rules appropriate for your team.

## What configuration looks like

With a compatible version of the plugin installed in your SQLFluff environment,
select it in the project's `.sqlfluff` file. For a DuckDB project, the
configuration looks like this:

```ini
[sqlfluff]
templater = sqlmesh
dialect = duckdb

[sqlfluff:templater:sqlmesh]
project_dir = .
```

Run SQLFluff from the SQLMesh project root, using your project's actual dialect:

```sh
sqlfluff lint models/
```

The [plugin source and README](https://github.com/sqlfluff/sqlfluff/tree/4.5.0/plugins/sqlfluff-templater-sqlmesh)
and [example project configuration](https://github.com/sqlfluff/sqlfluff/blob/4.5.0/plugins/sqlfluff-templater-sqlmesh/test/fixtures/sqlmesh/.sqlfluff)
are useful starting points for exploring the integration.

## Start with a representative set of models

Coverage depends on how a model uses templating. Plain query bodies and macros
that resolve to inline expressions can preserve useful source mappings.
More complex rendering, including structural macros and Jinja model bodies,
can fall back to a coarser mapping. Violations in templated regions are
suppressed by default, so a clean lint result doesn't necessarily mean every
part of a heavily templated model was checked.

Try a mix of your project's model styles, review the diagnostics, and inspect
any proposed fixes before adopting them across the project.

If you encounter a case the templater doesn't handle well, please
[open an issue](https://github.com/sqlfluff/sqlfluff/issues) with a minimal
example, your SQLFluff and SQLMesh versions, and the relevant configuration.
Examples from real projects help improve the integration.

## Find out more

- [Initial SQLMesh templater contribution: #7722](https://github.com/sqlfluff/sqlfluff/pull/7722)
- [SQLMesh templater implementation in SQLFluff 4.5.0](https://github.com/sqlfluff/sqlfluff/blob/4.5.0/plugins/sqlfluff-templater-sqlmesh/sqlfluff_templater_sqlmesh/templater.py)
- [SQLFluff documentation](https://docs.sqlfluff.com/)
