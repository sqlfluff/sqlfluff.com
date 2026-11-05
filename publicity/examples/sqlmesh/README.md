# SQLMesh templater worked example

This is the runnable project accompanying the SQLMesh Updates article.
Use Python 3.13 and Git in a separate virtual environment.

The plugin's PyPI endpoint returned 404 on 5 November 2026. `requirements.txt`
installs the plugin from SQLFluff's 4.5.0 Git tag; that plugin's metadata pins
the core SQLFluff package to 4.2.2. Do not install into an existing project
environment or override the dependency pin.

From this directory:

```sh
python -m venv .venv
```

Activate with `source .venv/bin/activate` on macOS/Linux or
`.venv\Scripts\Activate.ps1` in Windows PowerShell, then run:

```sh
python -m pip install -r requirements.txt
sqlfluff --version
sqlfluff lint models/orders.sql
sqlfluff fix models/orders.sql
sqlfluff lint models/orders.sql
```

The first lint reports four CP01 violations on lines 9 and 10 and exits 1.
The fix uppercases FROM, VALUES, AS and WHERE. The final lint passes and exits 0.
The MODEL header and @VAR('minimum_amount') expression remain unchanged.
Only CP01 is enabled, so a passing result means this keyword policy passes;
it does not imply every SQLFluff rule was checked.

The model uses inline rows and an in-memory DuckDB gateway. No credentials,
SQLMesh plan or warehouse dataset are needed. `sqlfluff render models/orders.sql`
shows the SQL query with the variable replaced by 100. If executed, it returns
one row: order_id 2, amount 150.

Validated on Windows with Python 3.13.5, SQLFluff and the plugin 4.2.2,
SQLMesh 0.235.4, SQLGlot 30.8.0 and DuckDB 1.5.6. Lint positions, the fix,
rendered query result and an unchanged second fix were checked.

Maintainers: rebuild the downloadable ZIP from these five source files only
(README.md, requirements.txt, config.py, .sqlfluff and models/orders.sql).
Exclude .venv, logs, caches, Python bytecode and any SQLMesh project state.
