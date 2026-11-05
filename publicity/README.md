# Publishing SQLFluff updates

The website is the durable home for announcements and feature spotlights.
Documentation explains how features work; release notes record the complete set
of changes. Link articles to the relevant technical sources and social posts
back to the article. Not every release or merged PR needs an article.

## Draft an article

1. Record the story idea and source PRs/releases in a GitHub issue.
2. Use `hugo new content --kind updates updates/<slug>` to create a draft page bundle.
3. Write a short description, a useful opening, a checked example where relevant,
   availability and limitations, and links supporting the claims.
4. Put optional images beside `index.md`. Use `image: social-card.png` and
   `image_alt: 'Description of the card'` for a landscape social preview.
   Without an image, metadata uses the existing avatar and a summary card.
5. Add proposed channel copy to `publicity/campaigns/<slug>.toml`.
6. Open one PR containing the article, assets and social copy.

Keep URLs stable and omit dates from slugs. `date` is the article's publication
date, not the release date of a feature it discusses. Describe older features
honestly as spotlights. Optional `authors` is a list of attribution names.
Set `lastmod` only for substantive changes after publication.

An AI assistant should inspect the source implementation, tests and release
notes before drafting. Distinguish published functionality from unmerged work.
Report measurements with their baseline, workload and environment. Do not add
percentages from separate benchmarks or present rule-only measurements as
end-to-end results. Keep unresolved editorial questions in this directory,
outside the public article body.

## Review and publish

- Check the article's claims, configuration examples, links and contributor
  credits. Review the separate social copy as part of the same PR.
- Review the Netlify preview on a narrow screen and desktop, in both themes.
  Draft banners and noindex metadata are expected in previews. They are public
  previews, not access-controlled storage for embargoed information.
- When ready to publish, set the intended publication date and `draft: false`.
  A future date requires a new build after that time; initially merge when ready.
- Merge, wait for the production deploy, and verify the article's live URL.
- Publish approved channel text and record each resulting URL below its campaign.

Campaign files are review material, not executable publication instructions.
No workflow currently reads them and nothing posts automatically. A future
publisher should verify the production deployment, deduplicate by campaign ID
and channel, record success/failure independently, and retry only failed channels.
An article correction must not automatically trigger another announcement.
LinkedIn and X remain manual initially.

## Verification

Use Hugo 0.125.4, matching `netlify.toml`, with the design submodule initialized:

```sh
hugo --gc --minify
hugo --buildDrafts --destination preview-public
hugo server --buildDrafts
```

Check `/updates/`, `/updates/index.xml`, article pages and the homepage. Production
must omit draft URLs from HTML, feeds and the sitemap. Preview builds should use
their preview base URL and `HUGO_PARAMS_NOINDEX=true`. Pagination is ten articles
per page; the homepage shows up to three; the feed contains the latest twenty.
Keep any generated `preview-public/` output outside Git.

## Initial drafts: checks before publication

### Performance in 4.5.0

- Current reference release: [4.5.0, 30 October 2026](https://github.com/sqlfluff/sqlfluff/releases/tag/4.5.0).
- The article now includes a 4.4.0-to-4.5.0 CLI lint benchmark on 72 public
  fixtures: five measured runs per release/scenario, with raw results and a
  reproduction bundle in the article page bundle. The headline leads with
  faster layout linting; the body scopes its 21–35% total-time reduction to
  single-process fixture tests, covering all release changes.
- Retain the variability caveat, especially for ANSI with four workers. A
  representative real-project comparison remains deferred.
- #8804 and #8769 are separately attributed PR measurements, not rerun
  benchmarks and not additional percentages to add to the fixture results.
- Confirm publication date, headline, credits and social wording.

### SQLMesh spotlight

- #7722 merged on 12 August 2026. The draft treats this as a spotlight on earlier
  work rather than a feature introduced by 4.5.0.
- The 4.5.0 tag contains the implementation and example configuration cited in
  the article. Source mapping limitations are described in the implementation.
- **Resolve distribution before publishing:** on 3 November 2026,
  `https://pypi.org/pypi/sqlfluff-templater-sqlmesh/json` returned HTTP 404.
  Repository package metadata still specifies plugin version 4.2.2 and a strict
  `sqlfluff==4.2.2` dependency. Confirm the intended supported installation path
  and compatible versions, then add a tested installation example or link to a
  maintained setup guide. Do not infer PyPI availability from a merged PR.
- Confirm initial release attribution and contributor credits before publication.

The two article dates are provisional. Publish the performance story first and
choose the SQLMesh spotlight's date after its setup guidance is ready.
