---
name: seo
description: Use when the question is how a website or a code change affects organic search — crawling, indexing, JavaScript rendering, pagination, faceted navigation, structured data, Core Web Vitals.
---

# Technical SEO for web developers

Help developers make pages discoverable, renderable, understandable, and useful to search engines and people. Treat SEO as a set of observable technical and content outcomes, not a promise of rankings or traffic.

## Frame the request

Establish which search engines, countries and languages matter; which page types or URL patterns are in scope; and what result the request targets. Separate these outcomes because they need different evidence:

- Crawling: can a crawler discover and fetch the URL?
- Rendering: what content, links, and metadata does it receive before and after JavaScript runs?
- Indexing: is the URL eligible, canonicalized, and selected for an index?
- Search appearance: is valid structured data eligible for a supported rich result?
- Performance: how does the real page behave for users?

If the ask says only “improve SEO,” inspect the current implementation and return evidence, risks, and the missing business decision. Do not invent a ranking target or promise that a code change will improve positions.

## Investigate the actual page

Inspect representative URLs from each affected page type, including relevant pagination, filter, locale, and product-variant cases. Trace the behavior through the actual boundary that owns it: server response and headers, frontend rendering and links, product/review data, routing, or deployment configuration.

Collect evidence appropriate to the issue:

- HTTP status, redirects, response HTML, canonical URL, robots directives, and sitemap inclusion.
- Initial HTML versus rendered DOM for important text, product links, metadata, and structured data.
- Whether navigation uses real crawlable links and whether the target URLs are useful and indexable.
- Search Console or the target engine's webmaster data when available: crawl/index status, queries, impressions, clicks, and affected URL samples.
- Field performance data by page type; use lab tools to diagnose, not as a substitute for real-user measurements.

State which facts you verified and which are hypotheses. Prefer a small sample that covers distinct templates and edge cases over claiming that one URL proves the whole site.

## Apply the relevant engineering rules

- Server-side or pre-rendering can make important content available in the first HTML response and avoid waiting for a rendering queue. It is a useful option, not a universal requirement. Check the actual rendered page and the search engines in scope.
- For pagination and infinite scroll, make later products discoverable through crawlable URLs and links. Do not assume a crawler will click a button or trigger a user action. A sitemap or product feed can help discovery but does not replace useful site navigation.
- Faceted filters can create a huge URL space. Decide deliberately which filter URLs should be indexable, canonicalized, or excluded from crawling; never apply a blanket rule without checking product requirements and existing URL behavior.
- Structured data must describe the page and content users can see. Product rich results are intended for a page about one product or variants of that product, not a category listing of unrelated items. Review markup must refer to a specific item and the corresponding review or aggregate must be visible.
- Preserve rating meaning. A share of customers recommending a product is not automatically an average star rating. Do not convert it to a different scale or mark it up as `AggregateRating` unless the data, label, item identity, and visible page support that representation.
- Measure user performance with current Core Web Vitals guidance and field data. Check current metric definitions and thresholds in the source instead of copying numbers into this skill.

## Recommend and verify

Give a developer a concrete result: affected URL patterns and code/data owner; verified problem; smallest useful change; user and search impact; trade-offs; and how to validate it. For indexing policy changes, explain which URLs become or cease to be eligible before changing canonical, `noindex`, robots, redirects, or sitemap behavior.

Validate the live or test URL with the relevant engine tools. For Google, use URL Inspection to inspect index status and rendered output, and Rich Results Test for supported structured data. A valid schema or successful render means eligible/visible to the tool; it does not guarantee indexing, a rich result, ranking, or traffic. For performance, compare field measurements over a suitable period and use Lighthouse/DevTools as diagnostics.

Read [SEO sources](references/seo-sources.md) when selecting the right guidance or explaining a finding. Engine behavior changes; use current official documentation for requirements and label any guidance that applies only to one search engine.
