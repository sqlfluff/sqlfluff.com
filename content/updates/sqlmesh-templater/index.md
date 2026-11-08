---
title: 'A SQLMesh templater for SQLFluff'
description: Bring SQLFluff linting to SQLMesh model SQL with a templater that understands model headers and macros.
date: 2026-11-03T08:00:00Z
draft: true
authors: [alanmcruickshank]
---

If your team uses SQLMesh, there's a SQLFluff integration worth a closer look:
the SQLMesh templater.

The [initial integration](https://github.com/sqlfluff/sqlfluff/pull/7722)
merged in August. It's part of the SQLFluff repository as a separate plugin,
[`sqlfluff-templater-sqlmesh`](https://pypi.org/project/sqlfluff-templater-sqlmesh/),
now available on PyPI, bringing SQLMesh projects into SQLFluff's linting workflow.

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

## Worked example: lint a SQLMesh model

Let's check a small model that filters orders using a SQLMesh variable, then
fix its keyword casing. Everything runs locally with DuckDB: you don't need
warehouse credentials, an existing dataset or a SQLMesh plan.

Create the small project below by copying each block into the named file.
For more model styles, explore the [SQLMesh test fixtures](https://github.com/sqlfluff/sqlfluff/tree/4.5.0/plugins/sqlfluff-templater-sqlmesh/test/fixtures/sqlmesh)
and the [templater test suite](https://github.com/sqlfluff/sqlfluff/tree/4.5.0/plugins/sqlfluff-templater-sqlmesh/test).

### 1. Install in a separate environment

For this walkthrough, use Python 3.13. The plugin is available directly from
PyPI; no Git checkout is needed. Version **4.5.0** installs the matching
**SQLFluff 4.5.0** core package. Use a separate environment rather than changing
an existing project's SQLFluff version.

Create the project directories and a virtual environment:

```sh
mkdir sqlmesh-example
cd sqlmesh-example
mkdir models
python -m venv .venv
```

On macOS or Linux, run `source .venv/bin/activate`. On Windows PowerShell, run
`.venv\Scripts\Activate.ps1`. Run the remaining commands in that environment,
from the `sqlmesh-example` directory.

Save this as `requirements.txt`:

```text
sqlfluff-templater-sqlmesh==4.5.0
sqlmesh==0.235.4
duckdb==1.5.6
```

Then install and check the SQLFluff version:

```sh
python -m pip install -r requirements.txt
sqlfluff --version
```

The expected core version for this example is `4.5.0`. For an existing SQLMesh
environment, the package to install is `sqlfluff-templater-sqlmesh`; keep the
plugin and SQLFluff versions compatible when updating your dependencies.

### 2. Configure SQLMesh and SQLFluff

Create `config.py` in the project root:

```python
from sqlmesh import Config

config = Config(
    model_defaults={"dialect": "duckdb"},
    default_gateway="local",
    gateways={"local": {"connection": {"type": "duckdb", "database": ":memory:"}}},
    variables={"minimum_amount": 100},
)
```

The `minimum_amount` variable will be used in the model's filter. The in-memory
DuckDB gateway keeps this example independent of an external database.

Next, create `.sqlfluff` alongside `config.py`:

```ini
[sqlfluff]
templater = sqlmesh
dialect = duckdb
rules = CP01

[sqlfluff:templater:sqlmesh]
project_dir = .

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = upper
```

For this example, we enable only `CP01` and explicitly require uppercase SQL
keywords. That keeps the result focused on one check. In your own project, use
your actual dialect and enable the rules your team wants to enforce.

The complete project will look like this:

```text
sqlmesh-example/
  .sqlfluff
  config.py
  requirements.txt
  models/
    orders.sql
```

### 3. Add a model with a real SQLMesh macro

Create `models/orders.sql`, deliberately leaving several query keywords lowercase:

```sql
MODEL (
    name demo.orders,
    kind FULL
);

SELECT
    order_id,
    amount
from (values (1, 25), (2, 150)) as orders(order_id, amount)
where amount >= @VAR('minimum_amount');
```

The query defines its input rows inline, so it has no dependency on another
model or table. `@VAR('minimum_amount')` reads the value `100` from the SQLMesh
configuration. If executed, the query would keep order `2`, with amount `150`.

SQLFluff handles the `MODEL` header separately and substitutes the inline macro
for linting. The surrounding SQL remains mapped to the original file, so the
keyword diagnostics can point to the lines you edit.

### 4. Lint, fix and check again

Run:

```sh
sqlfluff lint models/orders.sql
```

The result includes four `CP01` violations, at the original source positions:

```text
L:   9 | P:   1 | CP01 | Keywords must be upper case. [capitalisation.keywords]
L:   9 | P:   7 | CP01 | Keywords must be upper case. [capitalisation.keywords]
L:   9 | P:  33 | CP01 | Keywords must be upper case. [capitalisation.keywords]
L:  10 | P:   1 | CP01 | Keywords must be upper case. [capitalisation.keywords]
```

These refer to `from`, `values`, `as` and `where`. A lint run with violations
returns exit status `1`; that's expected at this step.

Now apply the fixes to this disposable example and lint it again:

```sh
sqlfluff fix models/orders.sql
sqlfluff lint models/orders.sql
```

The model should now contain:

```sql
MODEL (
    name demo.orders,
    kind FULL
);

SELECT
    order_id,
    amount
FROM (VALUES (1, 25), (2, 150)) AS orders(order_id, amount)
WHERE amount >= @VAR('minimum_amount');
```

The final lint run should pass with exit status `0`. The `MODEL` header and
`@VAR('minimum_amount')` expression stay in the source file: the rendered value
is used to analyse the query, not written back over the macro.

## Start with a representative set of models

Coverage depends on how a model uses templating. Plain query bodies and macros
that resolve to inline expressions can preserve useful source mappings.
More complex rendering, including structural macros and Jinja model bodies,
can fall back to a coarser mapping. Violations in templated regions are
suppressed by default, so a clean lint result doesn't necessarily mean every
part of a heavily templated model was checked.

Once the example works, try `sqlfluff lint models/` on a mix of your project's
model styles. Review the diagnostics and inspect any proposed fixes before
adopting them across the project.

If you encounter a case the templater doesn't handle well, please
[open an issue](https://github.com/sqlfluff/sqlfluff/issues) with a minimal
example, your SQLFluff and SQLMesh versions, and the relevant configuration.
Examples from real projects help improve the integration.

## Find out more

- [SQLMesh templater on PyPI](https://pypi.org/project/sqlfluff-templater-sqlmesh/)
- [Initial SQLMesh templater contribution: #7722](https://github.com/sqlfluff/sqlfluff/pull/7722)
- [SQLMesh templater implementation in SQLFluff 4.5.0](https://github.com/sqlfluff/sqlfluff/blob/4.5.0/plugins/sqlfluff-templater-sqlmesh/sqlfluff_templater_sqlmesh/templater.py)
- [SQLFluff documentation](https://docs.sqlfluff.com/)
