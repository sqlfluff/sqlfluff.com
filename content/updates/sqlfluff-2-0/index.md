---
title: 'SQLFluff 2.0: A new foundation for consistent SQL'
description: Rebuilt layout handling, clearer rule names and a dedicated formatting command make it easier to express your team's SQL style.
date: 2023-03-14T09:45:27Z
draft: true
authors: [alanmcruickshank]
---

*Retrospective announcement, added to the Updates archive. The date above is the
original release date; this article describes the changes introduced in 2.0.0.*

Consistent SQL is easier to maintain when your tools can express the style your
team wants. SQLFluff 2.0 brings a new foundation for that work: rewritten layout
and whitespace handling, a clearer organisation of linting rules, and a command
dedicated to formatting.

## Rules with names you can recognise

Earlier SQLFluff versions identified rules with codes such as `L001` and `L008`.
In 2.0, rules are organised into groups, with codes such as `AL01` for aliasing
and `LT01` for layout. Each rule also has a descriptive name, such as
`aliasing.table` or `aliasing.column`.

Those names make configuration easier to read. A section that configures column
aliases, for example, can say what it means:

```ini
[sqlfluff:rules:aliasing.column]
aliasing = explicit
```

Rule configuration sections now use these names rather than rule codes. The
change is more than a renaming exercise: some old rules have been combined.
Several previously separate spacing checks now live together in `LT01`.

## A fresh approach to layout

The layout and whitespace rules have been rewritten, along with the way layout
is configured. This gives related checks a common foundation for working with
spacing, indentation and line breaks.

For an existing project, the important step is to review the resulting style
changes deliberately. Update the configuration, lint a representative selection
of files, and inspect proposed fixes before applying them across the repository.

## A command for formatting

2.0 also introduces `sqlfluff format`. It applies a selected set of formatting
rules, providing a focused way to tidy SQL without enabling every available
autofix rule.

For example, in an environment running SQLFluff 2.0:

```sh
sqlfluff format models/ --dialect postgres
```

The command changes files, so review the diff as you would with other formatters.
Use your project's actual SQL dialect and configuration.

## More dialect support, and an upgrade to plan

Databricks becomes a distinct dialect in this release, rather than an alias for
SparkSQL. There are also parser performance improvements and dialect updates
across much of SQLFluff's supported SQL.

This is a major release with breaking configuration changes. When migrating
from 1.x, review rule selections, rule configuration sections and layout settings
together. The dbt templater also drops support for dbt versions older than 1.1.

Thank you to everyone who contributed code, examples, testing and feedback
during the 2.0 release cycle. The
[original release announcement](https://github.com/sqlfluff/sqlfluff/releases/tag/2.0.0)
includes the complete change list, contributor credits and migration references.

## Find out more

- [SQLFluff 2.0.0 release notes](https://github.com/sqlfluff/sqlfluff/releases/tag/2.0.0)
- [The 2.0 migration guide contribution](https://github.com/sqlfluff/sqlfluff/pull/4498)
- [Introducing the format command](https://github.com/sqlfluff/sqlfluff/pull/4473)

For a new installation today, use the [current documentation](https://docs.sqlfluff.com/)
to choose an appropriate supported version.
