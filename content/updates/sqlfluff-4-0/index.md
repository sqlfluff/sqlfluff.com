---
title: 'SQLFluff 4.0: Beginning the Move to Rust'
description: Why we're introducing Rust implementations of SQLFluff's lexer and parser, and how we're approaching the transition.
date: 2026-01-15T20:58:11Z
authors: [alanmcruickshank]
---

SQLFluff 4.0 marks the beginning of moving some of the work inside SQLFluff
from Python to Rust. The first routines are the lexer and parser, which turn
SQL text into the structure used by the linting rules. In this release, the
Rust implementations are optional and experimental.

The reason for starting this work is performance. As SQL projects grow,
the time spent checking them becomes more noticeable: in a pre-commit hook,
while iterating on a model, or across a whole project in CI. We want SQLFluff
to remain practical to use as those workloads get larger.

> NOTE: Rust is still an _optional_ dependency in 4.0, but we anticipate that with 5.0
> in future, it will become the default.

## Why start with the lexer and parser?

Before a linting rule can inspect a file, SQLFluff needs to recognise its tokens
and work out how they fit together. That involves repeated matching and walking
through the query. On large or complex files, the cost of that work matters.

Python has made it possible for the community to build SQLFluff's dialects,
rules and integrations. We want to retain that flexibility while moving some
of the repeated processing into compiled routines. Rust gives us a way to do
that within the existing Python package, so users can continue to work through
the same commands and configuration.

Changing the language of these routines is only part of the work. The Rust
parser uses a different internal approach to matching the grammar, so it also
needs testing and tuning in its own right. Rewriting a routine doesn't, on its
own, establish how much faster a complete lint run will be.

## Keeping dialect development in Python

An important part of this approach is that the Rust parser's grammar tables are
generated from the Python grammar definitions. Adding support for a SQL
construct should not mean maintaining a separate definition of its syntax in
each language.

There is still maintenance work involved: changes to the parser's matching logic
need to be reflected in both implementations. Keeping the grammar definitions
shared reduces duplication, but it doesn't remove the need to compare behaviour
and investigate differences.

This lets us introduce Rust in stages while continuing to develop the dialects,
linting rules and integrations in Python.

## What to expect from 4.0

4.0 is the first public beta of this work. The release notes report gains on
larger files and projects, but there is also overhead in moving data between
Python and Rust. For a small individual file, that overhead can make the Rust
implementation slightly slower.

The aim at this stage is to make the implementation available for testing and
establish a basis for further optimisation. The benefit will depend on the
workload, and improvements to parsing will not remove time spent elsewhere, such
as rendering templates or evaluating linting rules.

Rust support is opt-in, so an ordinary installation continues to use Python.
For an isolated environment exploring the original release, install:

```sh
python -m pip install 'sqlfluff[rs]==4.0.0'
```

Try it in development before adopting it in production. Use representative
files, compare diagnostics and proposed fixes, and keep the configuration and
process settings the same when measuring timings. Differences in behaviour are
useful feedback, alongside performance results.

For an installation today, follow the [current documentation](https://docs.sqlfluff.com/)
for supported versions and installation options. The command above records the
4.0 launch.

A particular thank you to [keraion](https://github.com/keraion), who led the Rust
implementation effort, and to everyone who tested and reviewed the integration.

The [4.0.0 release notes](https://github.com/sqlfluff/sqlfluff/releases/tag/4.0.0)
cover the other changes, including the updated dbt support requirements.

## Find out more

- [SQLFluff 4.0.0 release notes and contributor credits](https://github.com/sqlfluff/sqlfluff/releases/tag/4.0.0)
- [The initial Rust lexer implementation](https://github.com/sqlfluff/sqlfluff/pull/7132)
- [The initial Rust parser implementation](https://github.com/sqlfluff/sqlfluff/pull/7342)
