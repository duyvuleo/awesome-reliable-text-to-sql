# Organization and Awesome-list practices

The collection is designed for three common tasks: finding a useful paper, deciding which resource to try, and understanding whether a benchmark measures the intended capability.

## Choices

- **A short entry point with deeper indexes.** The root README gives starting papers and reading routes. Full annotations live in topic-grouped paper, system, and dataset pages. This keeps a growing collection navigable without dropping useful summaries.
- **Original annotations.** Each paper gets a concise explanation of its contribution and boundary. A title or promotional slogan alone does not tell readers why it belongs.
- **Tables for comparison.** Papers use one table per topic with year, paper/venue, summary, and code/data columns. System and dataset tables pair purpose or protocol with availability and access conditions. Expandable notes retain provenance without widening the main comparison.
- **One canonical record.** JSON catalogs generate the visible lists. The same paper can have several tags while retaining one stable identity and source record.
- **Separate papers from artifacts.** Resource entries state what is visible, what remains unavailable, and which licenses or access conditions apply. Paper-only benchmark descriptions can be useful when clearly labeled.
- **A comparison guide rather than one leaderboard.** Interaction protocols and correctness criteria vary, so the guide helps readers choose an evaluation before comparing results.
- **A benchmark selection matrix.** Two linked tables apply those distinctions to the cataloged datasets, with explicit unknowns, source locators and access conditions. Comparison records are maintained separately from artifact descriptions and validated together.
- **Dated curation with corrections.** The search method, material updates, and unresolved public leads are inspectable. New publications, released artifacts, and corrected metadata all count as useful maintenance.
- **Concrete walkthroughs.** Original synthetic SQLite examples make key distinctions executable without a model endpoint. Scripted dialogue is labeled clearly and kept separate from benchmark results.
- **Consistent visual identity.** Light/dark README banners and a matching social card use the same question-to-action motif. The artwork contains no changing counts; badges link to actual validation and license information.

## Repository layout

```text
README.md                  Starting papers, routes, and recent additions
papers/README.md           Annotated literature by topic
systems/README.md          Systems and evaluation tools
datasets/README.md         Data and benchmark protocols
data/                     Canonical paper/resource records and metadata
examples/                 Original synthetic SQLite walkthroughs
assets/                   Original banners and social-preview artwork
docs/evaluation.md        Questions for interpreting benchmark results
docs/benchmark-matrix.md  Task coverage, evaluation protocols, and data access
docs/search-method.md     Inclusion rules, sources, and coverage limits
docs/search-log/          Dated public-source research notes
scripts/                  Renderer, validator, link checker, and tests
.github/                  Validation workflow and contribution templates
CONTRIBUTING.md            Contribution process
CHANGELOG.md               Material additions and corrections
```

## Sources for these practices

The [Awesome manifesto](https://github.com/sindresorhus/awesome/blob/main/awesome.md) and [list guidelines](https://github.com/sindresorhus/awesome/blob/main/pull_request_template.md) motivate focused curation, useful descriptions, navigation, contribution guidance, and maintenance. The central index has its own submission requirements; this repository does not claim acceptance there.

[Awesome Selfhosted Data](https://github.com/awesome-selfhosted/awesome-selfhosted-data) illustrates maintaining structured records behind generated views. [Awesome Text2SQL](https://github.com/eosphoros-ai/Awesome-Text2SQL) and the [NL2SQL Handbook](https://github.com/HKUSTDial/NL2SQL_Handbook) provide broader discovery paths; this collection concentrates on ambiguity and answerability. The [Awesome AI Co-Scientist companion](https://github.com/duyvuleo/awesome-ai-co-scientist) provides a consistent annotated-list format.

Useful later extensions include filtered browsing over the same JSON catalog, versioned resource snapshots, and independently contributed reproduction notes. These should extend verified content rather than turn publication counts or popularity into a quality ranking.
