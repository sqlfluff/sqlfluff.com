---
title: 'SQLFluff 2.0: Rules with names that make sense'
description: Meaningful rule names and grouped codes replace the old Lxxx identifiers, making SQLFluff configuration easier to read, maintain and discuss.
date: 2023-03-14T09:45:27Z
draft: true
authors: [alanmcruickshank]
---

*Retrospective announcement, added to the Updates archive. The date above is the
original release date; this article describes the changes introduced in 2.0.0.*

What does `L010` check? Unless you've memorised SQLFluff's rules, the code
doesn't help you answer that question. Nor does it tell you how that rule relates
to `L014` or `L030`. Reading a configuration file meant repeatedly looking up
numbers before you could understand the style it was trying to enforce.

That was poor user experience. An undifferentiated list of `Lxxx` identifiers
was also out of step with the meaningful names and categories familiar from
other linting tools. We wanted rules to be easier to discover, discuss and
configure, without asking users to learn a numbering system first.

**SQLFluff 2.0 gives rules descriptive names and codes grouped by purpose.**
The associated configuration changes are the main reason this is a major
release: existing projects need to update how they refer to and configure rules.

## Names for people, codes with context

The old `L010` becomes `CP01`, named `capitalisation.keywords`. The code is
still short enough for terminal output or a review comment, but its prefix now
tells you the category. The full name tells you what the rule is about.

Related checks sit together: `CP02` is `capitalisation.identifiers` and `CP03`
is `capitalisation.functions`. The same approach applies to aliasing (`AL`),
layout (`LT`), references (`RF`) and the other rule families.

That gives a team useful vocabulary. "Configure `capitalisation.keywords`" is
easier to reason about than "change `L010`", especially for someone encountering
the configuration for the first time.

## Configuration that explains itself

Rule-specific configuration sections now use the rule's **name**, rather than
its old code. For example, this 1.x configuration:

```ini
[sqlfluff:rules:L010]
capitalisation_policy = upper
```

becomes:

```ini
[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = upper
```

The intent is visible in the file itself. Importantly, the old section name
isn't just an alternative spelling: in 2.0, unrecognised rule configuration
sections raise warnings and their settings are ignored. Use the full rule name
here, rather than replacing `L010` with `CP01` in the section heading.

Rule *selection* is more flexible. In `rules` and `exclude_rules`, you can use
names, grouped codes or group names. For example, to select the capitalisation
checks, replace:

```ini
[sqlfluff]
rules = L010, L014, L030, L040, L063
```

with:

```ini
[sqlfluff]
rules = capitalisation
```

In 2.0 that group selects `CP01` through `CP05`. A group expresses an ongoing
policy, so future rules added to it may also be selected when you upgrade. Use
individual names or codes when you want an explicit list.

Legacy codes remain supported as aliases for selecting rules. However, they
can obscure the meaning of your config, particularly where several old rules
have been combined. We recommend moving to the new names and groups rather
than relying on those aliases.

## Rule code migration table

The table maps legacy codes to the grouped codes introduced in 2.0. It is
organised by the new rule families so related changes are easy to find.
For rule names, options and behaviour in the version you're using, consult the
[current rules reference](https://docs.sqlfluff.com/en/stable/reference/rules/).
Run `sqlfluff rules` to inspect the rules available in your installed version.

| Rule family | Previous code(s) | 2.0 code |
| --- | --- | --- |
| Aliasing | `L011` | `AL01` |
| Aliasing | `L012` | `AL02` |
| Aliasing | `L013` | `AL03` |
| Aliasing | `L020` | `AL04` |
| Aliasing | `L025` | `AL05` |
| Aliasing | `L066` | `AL06` |
| Aliasing | `L031` | `AL07` |
| Ambiguous | `L021` | `AM01` |
| Ambiguous | `L033` | `AM02` |
| Ambiguous | `L037` | `AM03` |
| Ambiguous | `L044` | `AM04` |
| Ambiguous | `L051` | `AM05` |
| Ambiguous | `L054` | `AM06` |
| Ambiguous | `L068` | `AM07` |
| Capitalisation | `L010` | `CP01` |
| Capitalisation | `L014` | `CP02` |
| Capitalisation | `L030` | `CP03` |
| Capitalisation | `L040` | `CP04` |
| Capitalisation | `L063` | `CP05` |
| Convention | `L061` | `CV01` |
| Convention | `L060` | `CV02` |
| Convention | `L038` | `CV03` |
| Convention | `L047` | `CV04` |
| Convention | `L049` | `CV05` |
| Convention | `L052` | `CV06` |
| Convention | `L053` | `CV07` |
| Convention | `L055` | `CV08` |
| Convention | `L062` | `CV09` |
| Convention | `L064` | `CV10` |
| Convention | `L067` | `CV11` |
| Jinja | `L046` | `JJ01` |
| Layout | `L001`, `L005`, `L006`, `L008`, `L023`, `L024`, `L039`, `L048`, `L071` | `LT01` |
| Layout | `L002`, `L003`, `L004` | `LT02` |
| Layout | `L007` | `LT03` |
| Layout | `L019` | `LT04` |
| Layout | `L016` | `LT05` |
| Layout | `L017` | `LT06` |
| Layout | `L018` | `LT07` |
| Layout | `L022` | `LT08` |
| Layout | `L036` | `LT09` |
| Layout | `L041` | `LT10` |
| Layout | `L065` | `LT11` |
| Layout | `L009` | `LT12` |
| Layout | `L050` | `LT13` |
| References | `L026` | `RF01` |
| References | `L027` | `RF02` |
| References | `L028` | `RF03` |
| References | `L029` | `RF04` |
| References | `L057` | `RF05` |
| References | `L059` | `RF06` |
| Structure | `L035` | `ST01` |
| Structure | `L043` | `ST02` |
| Structure | `L045` | `ST03` |
| Structure | `L058` | `ST04` |
| Structure | `L042` | `ST05` |
| Structure | `L034` | `ST06` |
| Structure | `L032` | `ST07` |
| Structure | `L015` | `ST08` |
| T-SQL | `L056` | `TQ01` |

### Why the layout mappings aren't all one-to-one

The layout work also consolidated checks that had grown separately around
different pieces of SQL. Nine spacing rules now map to `LT01`, while three
indentation rules map to `LT02`. This lets one consistent layout configuration
describe how SQL should look, instead of scattering related settings across
several checks.

For example, selecting the legacy `L005` now selects `LT01`, which checks much
more than spacing around commas. Review the resulting scope instead of treating
every alias as an exact replacement. The
[layout configuration guide](https://docs.sqlfluff.com/en/stable/configuration/layout)
explains the available controls and their current behaviour.

## Updating an existing project

Start with your configuration file and remove settings that merely repeat the
defaults. Then update rule selections in `rules` or `exclude_rules`, and rename
rule-specific sections to use full names. Check in-file configuration directives
for old references too.

Pay particular attention to layout settings and the many-to-one mappings above.
Lint a representative set of files, read any configuration warnings, and review
the changes before applying fixes across the project. This is a chance to make
your configuration smaller and clearer, not simply exchange one list of codes
for another.

See the [2.0 migration guide](https://docs.sqlfluff.com/en/stable/reference/release-notes#upgrading-from-1-x-to-2-0)
and [rule configuration documentation](https://docs.sqlfluff.com/en/stable/configuration/rules)
for the detailed upgrade steps. For everything else included in the release,
including contributor credits, see the
[2.0.0 changelog](https://github.com/sqlfluff/sqlfluff/releases/tag/2.0.0).
