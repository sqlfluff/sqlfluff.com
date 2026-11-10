---
title: 'SQLFluff 2.0: Reorganisation of Linting Rules'
description: 2.0 brings breaking changes to rule codes and classification. This update dives into why we chose to change and what the new setup is.
date: 2023-03-14T09:45:27Z
authors: [alanmcruickshank]
---

Until now, SQLFluff's rules have been added fairly organically, as members of
the community implemented the checks they needed. Each new rule received the
next available `Lxxx` code. That meant the rules were effectively in
chronological order: the number reflected when a rule was added, rather than
what it checked.

That was a reasonable way to start, but it became less useful as the project
grew. Related rules could be quite far apart in the list, and understanding a
configuration file often meant looking up several codes before you could work
out what it was doing. It also differed from the named rules and categories
used by other linting tools.

By 2.0, the set of rules had stabilised enough for us to identify useful
groupings. We've reorganised them around those groups and given each rule a
name. This changes how rules are referenced in configuration, which is the main
reason for making it a major release.

## Rule names and grouped codes

The old `L010` becomes `CP01`, named `capitalisation.keywords`. The code is
still short enough for terminal output or a review comment, while the prefix
identifies the group. The name describes what the rule checks.

Related checks sit together: `CP02` is `capitalisation.identifiers` and `CP03`
is `capitalisation.functions`. The same approach applies to aliasing (`AL`),
layout (`LT`), references (`RF`) and the other rule families.

The intention is to make it easier to refer to a rule without needing to
remember its number. It also gives us a more consistent way to organise the
configuration for related checks.

## Changes to configuration

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

The setting itself hasn't changed in this example; only the section heading
has. In 2.0, unrecognised rule configuration sections raise warnings and their
settings are ignored. This means you need to use the full rule name here, rather
than simply replacing `L010` with `CP01` in the heading.

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

Legacy codes remain supported as aliases for selecting rules, so these
references don't all need to change immediately. However, some old rules have
been combined, so an alias may now select a broader set of checks. It's worth
reviewing those references as part of the upgrade.

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

For example, `L005` checked for spaces before commas, `L008` checked for a
single space after them, and `L006` checked spacing around operators. These are
now all handled by `LT01` (`layout.spacing`). The associated configuration is
organised by the type of SQL element: `[sqlfluff:layout:type:comma]` can specify
`spacing_before = touch`, meaning no space before a comma, while the same layout
configuration system describes spacing around operators and other elements.
This separates the choice of which checks to run from the description of the
layout they should enforce, rather than requiring a separate rule and set of
options for each spacing convention.

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
the changes before applying fixes across the project. Where several settings
express the same intention, consider whether a group or a shared layout setting
would make that easier to maintain.

See the [2.0 migration guide](https://docs.sqlfluff.com/en/stable/reference/release-notes#upgrading-from-1-x-to-2-0)
and [rule configuration documentation](https://docs.sqlfluff.com/en/stable/configuration/rules)
for the detailed upgrade steps. For everything else included in the release,
including contributor credits, see the
[2.0.0 changelog](https://github.com/sqlfluff/sqlfluff/releases/tag/2.0.0).
