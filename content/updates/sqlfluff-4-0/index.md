---
title: 'SQLFluff 4.0: Introducing Rust-powered parsing'
description: Optional Rust implementations of the lexer and parser open a new path for improving SQLFluff performance on larger files and projects.
date: 2026-01-15T20:58:11Z
draft: true
authors: [alanmcruickshank]
---

*Retrospective announcement, added to the Updates archive. The date above is the
original release date; this article describes the changes introduced in 4.0.0.*

SQLFluff 4.0 introduces an optional Rust implementation of its lexer and parser.
It is a new step in improving the time it takes to check SQL, particularly for
larger files and projects, while keeping SQLFluff's familiar linting workflow.

## Rust inside, the same workflow outside

Before SQLFluff can check a query, it needs to turn the source text into tokens
and then a structure its rules can inspect. The lexer and parser do that work.
4.0 brings Rust implementations of those stages into the project as an opt-in
alternative to the Python implementation.

You still use SQLFluff's commands, configuration and linting rules. The change
is in how part of the processing happens internally, rather than a separate tool
or a new SQL style to adopt.

## An opt-in first release

At launch, Rust support is beta and must be installed explicitly. For an isolated
environment exploring the original 4.0 release, the installation looks like:

```sh
python -m pip install 'sqlfluff[rs]==4.0.0'
```

The release recommends testing the Rust package in a development environment
before adopting it in production. Try representative files, compare diagnostics
and proposed fixes, and check how it behaves with your dialect and templater.

For a new installation today, follow the
[current documentation](https://docs.sqlfluff.com/) for supported versions and
installation options. The command above records the historical release.

## Where the performance benefit matters

The 4.0 release reports noticeable gains on larger files and projects. It also
notes a trade-off: on small individual files, moving data into Rust can cost
more than the processing saves, making those cases slightly slower.

That is why a representative workload matters. A quick check of one short query
doesn't tell you how a whole project will behave. Keep your SQL, configuration
and process settings consistent when comparing the two implementations.

The launch announcement does not establish a single percentage improvement
for every project, and this article makes no such claim.

## More in 4.0

Alongside Rust support, 4.0 adds the ability to require implicit indents,
includes fixes for `CV12` and `RF01`, and expands dialect support. For teams
using the dbt templater, it drops support for dbt 1.4 and older and includes
support for dbt 1.10.

A particular thank you to [keraion](https://github.com/keraion), who led the Rust
implementation effort, and to everyone who tested and reviewed the integration.

## Find out more

- [SQLFluff 4.0.0 release notes and contributor credits](https://github.com/sqlfluff/sqlfluff/releases/tag/4.0.0)
- [The initial Rust lexer implementation](https://github.com/sqlfluff/sqlfluff/pull/7132)
- [The initial Rust parser implementation](https://github.com/sqlfluff/sqlfluff/pull/7342)
