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
| `source_depth` | `primary-record` for abstract/metadata inspection, or `targeted-full-text` when relevant paper sections were inspected. Neither means reproduced. |
| `added_on` | First inclusion date; retain it when revising an existing entry. Recent additions sort by this date, then publication year and title. |
| `checked_on` | Date of substantive source verification in `YYYY-MM-DD` format. |
| `artifact_status` | Optional detail about release or inspection limits. |

## Resources

`resources.json` separately describes systems, evaluation tools, and datasets or benchmark designs. Headline counts count records, including explicitly labeled paper-only designs; they do not imply that every entry is runnable or downloadable. Fields are `id`, `name`, `kind` (`system`, `tool`, or `dataset`), `paper_ids`, `url`, `description`, `protocol`, `availability`, `license_note`, `evidence`, and `checked_on`.

The `protocol` field states what the resource supports and any important evaluation limit. `availability` distinguishes visible code/data, access restrictions, documentation-only entries, and unverified downloads. `license_note` reports the checked terms or explicitly leaves them unverified; a paper's license does not determine the dataset's license.

`meta.json` stores collection metadata. Its `updated` field changes for material catalog revisions, not merely because a scheduled search ran. A dated search log may record a search with no qualifying additions.
