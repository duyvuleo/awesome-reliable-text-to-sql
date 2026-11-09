# Catalog format

The UTF-8 JSON files are the source of truth. Generated Markdown is committed for convenient browsing. Only the Python standard library is needed to maintain the collection.

## Papers

`papers.json` is a list of records with these fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable lowercase identifier used for links. |
| `title`, `year`, `publication_status` | Verified bibliographic identity; prefer the published year when a venue is verified. |
| `primary_url` | Public paper or proceedings record. |
| `code_url`, `dataset_url` | Verified artifact or project links, or `null` when not established. Null does not mean no artifact exists. |
| `category` | One navigation group: `ambiguity`, `answerability`, `interaction`, `context`, or `verification`. |
| `topics` | Overlapping descriptive tags. Categories are navigation aids, not a claim of exclusive scientific classification. |
| `scope` | `core` for direct treatment of the focus; `adjacent` for explicitly relevant supporting work. |
| `summary` | An original concise explanation of the contribution and its boundary. |
| `evidence` | Public sources supporting the metadata and description. |
| `source_depth` | Metadata retained in JSON and omitted from paper tables: `primary-record` for abstract/metadata inspection, `targeted-full-text` for selected sections, or `full-text-reviewed` for a completed article reading supported by a reading record. None means reproduced. |
| `reading_notes_url` | Optional link to generated detailed notes covering methods, evaluation, findings and limits. |
| `added_on` | First inclusion date; retain it when revising an existing entry. Recent additions sort by this date, then publication year and title. |
| `checked_on` | Date of substantive source verification in `YYYY-MM-DD` format. |
| `artifact_status` | Optional detail about release or inspection limits. |

## Resources

`resources.json` separately describes systems, evaluation tools, and datasets or benchmark designs. Headline counts count records, including explicitly labeled paper-only designs; they do not imply that every entry is runnable or downloadable. Fields are `id`, `name`, `kind` (`system`, `tool`, or `dataset`), `paper_ids`, `url`, `description`, `protocol`, `availability`, `license_note`, `evidence`, and `checked_on`.

The `protocol` field states what the resource supports and any important evaluation limit. `availability` distinguishes visible code/data, access restrictions, documentation-only entries, and unverified downloads. `license_note` reports the checked terms or explicitly leaves them unverified; a paper's license does not determine the dataset's license.

`meta.json` stores collection metadata. Its `updated` field changes for material catalog revisions, not merely because a scheduled search ran. A dated search log may record a search with no qualifying additions.

## Paper reading notes

`paper-reviews.json` contains original annotations keyed by `paper_id`. Each record identifies the exact public `source_url`, `version`, `reviewed_on` date, actual `coverage`, and any `unread` material. Its status is `full-text-reviewed`, `partial`, or `unavailable`. A completed reading must have no unread substantive material and must include located claim checks; a downloaded file alone does not establish completion.

The `problem`, `method`, `evaluation`, `findings`, `limitations`, and `relevance` fields form the detailed note. Each item in `claims` examines a claim or possible inference using `evidence`, a `locator` and a `disposition`; these are paraphrased assessments, not quotations attributed to the authors. Optional `additional_sources` supply labeled public links to separately inspected supplements or artifact evidence. These readings are not independent experimental reproductions. The renderer produces `papers/reading-notes.md` and individual notes under `papers/notes/`; retrieval files and third-party papers are not published.

## Benchmark comparisons

`benchmarks.json` contains one comparison record per dataset/benchmark resource and generates `docs/benchmark-matrix.md`. Keep comparison fields supported by public primary sources; do not infer them from a project name or from the presence of conversational data.

| Field | Meaning |
| --- | --- |
| `resource_id`, `label` | Reference to an existing dataset resource and a concise display name. |
| `relevance` | `direct` for ambiguity/answerability or clarification tasks; `adjacent` for supporting context or workflow evaluation. |
| `ambiguity`, `unanswerability` | Objects with `status` (`yes`, `not_targeted`, `not_reported`) and a qualifying `detail`. Unknown is not a negative label. |
| `clarification` | `mode` (`generated`, `supplied`, `mixed`, `not_targeted`, `not_reported`) and a protocol-specific `detail`. |
| `interaction` | `mode` (`static`, `recorded`, `simulated`, `not_reported`) and a `detail` identifying runtime user feedback, offline history, or environment interaction. |
| `domain`, `evaluation` | Publicly supported domain and task/metric family; do not copy performance scores across protocols. |
| `data_access` | `public_artifacts`, `author_download`, `release_unverified`, or `not_reported`. Public artifacts do not establish that every dependency is unrestricted or executable. |
| `evidence` | Objects with public `url`, inspected-section `locator`, and `supports` listing the comparison fields covered. Every field requires provenance. |
| `checked_on` | Date of comparison verification, no later than `meta.updated`. |

Availability descriptions and license notes are rendered directly from `resources.json` to prevent divergent copies. When a new dataset resource is added, include a comparison record with explicit unknowns for unchecked fields. Validate the records and regenerate both the indexes and the matrix.
