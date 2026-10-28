# Building the Text-to-SQL explorer

[Live explorer](https://duyvuleo.github.io/awesome-reliable-text-to-sql/) · [Reader guide](explorer.md)

The interface adapts the CC0 [AI Co-Scientist explorer](https://github.com/duyvuleo/awesome-ai-co-scientist/blob/main/docs/explorer-development.md). It uses the same static theme-cloud and reading-table architecture. The graph uses the explorer’s light/dark palette with the reference’s outer-topic/inner-work SVG geometry, fixed zoom baseline, keyboard interaction and hover emphasis from [Agents That Learn](https://duyvuleo.github.io/awesome-agents-that-learn/), while retaining multi-theme selection. Labels now default to Automatic, with collision-free nearby placement and focus-based connections in large multi-theme overviews. The graph is rendered with native SVG in [graph.mjs](../site/graph.mjs), with keyboard-focusable nodes, hover inspection, pan/zoom and label placement. It uses fixed desktop/mobile view boxes so automatic canvas fitting cannot shrink the map. There is no bundler, backend, model API, analytics service, remote font or runtime CDN dependency.

## Source and generated files

| Source | Role |
| --- | --- |
| [Canonical JSON](../data/README.md) | Papers, resources, benchmark comparisons and verification dates. |
| [Theme vocabulary](../data/explorer-taxonomy.json) | Explicit labels, aliases and excluded administrative tags. Original tags remain unchanged. |
| [Data adapter](../scripts/explorer_data.py) | Preserves original records and constructs work groups and explicit resource cross-references. |
| [Renderer](../scripts/render.py) | Generates Markdown and `site/data.json`; `--check` detects stale outputs. |
| [Selection model](../site/model.mjs) | Pure filtering, graph, deterministic ring layout, URL-state and export functions. |
| [SVG graph](../site/graph.mjs) | Draws the topic map, places labels, and handles keyboard, pointer and zoom interactions. |
| [Interface](../site/app.mjs) | DOM rendering, benchmark inspection, graph interaction and downloads. |
| [Styles](../site/styles.css) | Responsive layout and automatic light/dark appearance. |
| [Pages workflow](../.github/workflows/pages.yml) | Validates and uploads only `site/`, then deploys to GitHub Pages. |

## Identity and evidence

Each paper starts a work group. A resource with exactly one `paper_ids` reference joins that paper's group. Resources with zero or multiple references remain independent; multiple references remain navigation links in the inspector. Titles, shared repositories, topical overlap and evidence citations are never merge keys. This keeps RTS/RTS++ and SpotIt/SpotIt+ distinct while linking their shared tools.

The payload preserves each source object under `original`, adds display fields and canonical catalog links, and includes the benchmark comparison records unchanged. No release date or resource addition date is invented. Resources inherit paper themes and research areas only for discovery. The theme vocabulary excludes the administrative `benchmark` tag from the cloud.

A single member must satisfy resource/year/code-link filters together. Search spans all group members. Theme filters support any/all matching, and repeated theme URL parameters preserve multiple selections. Only theme edges are rendered; old `mode=catalog` links normalize to the theme graph. Unsupported URL states are normalized, and selections outside the filtered result are cleared. The oldest-first order keeps undated works last. Source depth is retained only in original JSON metadata and is not displayed.

## Build and verify

From the repository root:

```bash
python3 scripts/render.py
python3 scripts/validate.py
python3 scripts/render.py --check
python3 -m unittest discover -s scripts -p 'test_*.py'
node --test tests/explorer.test.mjs
node --check site/app.mjs
python3 -m http.server 8769 --bind 127.0.0.1 --directory site
```

Open the local server at `127.0.0.1:8769`; use HTTP so the JSON fetch works. Edit canonical records, the adapter or the interface, not generated `site/data.json`. Daily catalog regeneration also updates the explorer.

Python tests check record conservation, explicit grouping, undated handling, source preservation and deterministic generation. JavaScript tests check combined filters, URL round trips (including legacy label preferences), empty states, graph endpoints, neighborhood semantics, presentation policies, collision refusal, and exports. Browser checks should cover theme selection, combined filters, empty results, details and dismissal, benchmark evidence, JSON export, and narrow-screen overflow. Automated checks do not establish accessibility conformance or scientific correctness.

GitHub Pages publishes through Actions. Deployment grants only the deployment job `pages: write` and `id-token: write`; build jobs read the repository and Pages configuration. Pull-request validation never deploys. Only the static `site/` directory enters the deployment artifact.
