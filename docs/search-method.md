# Search method and coverage

[Back to the collection](../README.md)

The initial search was conducted on **22 October 2026**. It combined broad keyword searches, targeted searches for named systems and benchmarks, citation chaining, and inspection of author artifact pages. The aim is broad, continually improving coverage of the defined topic, not a claim of exhaustive indexing or a formal systematic-review protocol.

## Sources

Primary sources include ACL Anthology, arXiv, ACM and IEEE publication records, PVLDB, OpenProceedings, PMLR, official conference proceedings, and author-maintained project pages. GitHub and Hugging Face help establish artifact availability. General search engines and existing awesome lists provide discovery leads; secondary summaries are not used as evidence for catalog claims.

## Query families

| Family | Representative queries |
| --- | --- |
| Ambiguity | `("text-to-SQL" OR NL2SQL) (ambiguity OR ambiguous OR underspecification OR disambiguation)` |
| Answerability | `("text-to-SQL" OR NL2SQL) (unanswerable OR answerability OR refusal OR abstention)` |
| Interaction | `("text-to-SQL" OR NL2SQL) (clarification OR interactive OR conversational OR "intent drift")` |
| Reliability | `"text-to-SQL" ("selective prediction" OR calibration OR confidence OR uncertainty)` |
| Evaluation | `"text-to-SQL" ("SQL equivalence" OR "test suites" OR "formal verification" OR "benchmark quality")` |
| Artifacts | Exact paper/system title with `code`, `dataset`, `GitHub`, or `Hugging Face` |
| Recent updates | The above terms with recent dates, followed by publication-date checks on the primary record |

Query syntax is adapted to each service; the table describes concept combinations rather than assuming every search engine interprets Boolean syntax identically. The [dated logs](search-log/README.md) retain actual search strings, verified sources, and unresolved leads.

## Inclusion and exclusion

Include a work when it directly addresses ambiguity, underspecification, answerability, clarification, or abstention in natural-language database querying. Include adjacent work only when its contribution helps evaluate or implement those capabilities, with a clear relevance statement. Historical interaction systems are included alongside current agents to preserve useful technical context.

Exclude generic SQL-generation or agent papers without a specific connection to the scope, promotional claims without inspectable technical evidence, and nonpublic materials. Commercial documentation may qualify as an explicitly labeled system resource when it documents a relevant capability; it is not equivalent to a peer-reviewed evaluation.

## Verification and deduplication

For each selected work, inspect the primary title, date, publication status, and abstract; inspect full-text sections when needed for a specific claim. Verify official artifact links independently where possible. Use stable IDs, normalize title and paper identifiers, and reconcile preprint and proceedings versions. Identically named resources are kept separate when their sources identify different projects.

The catalog records inspection depth. A primary-record check supports a concise description of the stated task and contribution. It does not imply an audit of every experimental claim. Targeted full-text inspection likewise does not mean reproduction. Quantitative claims requiring detailed validation are generally omitted from the short summaries.

## Limits

Search indexing is incomplete and delayed, terminology varies, some proceedings are difficult to access, and repository contents can change after inspection. English-language searches may underrepresent other literature. Citation chaining is targeted, not a complete bibliometric crawl. A future daily search can discover an older missing paper as well as a new release.

Public repositories that are gated, empty, archived, or incomplete remain labeled accordingly. An HTTP error does not prove an artifact is absent. Access conditions and licenses should be rechecked before reuse. Suggestions and corrections are welcome through [contributions](../CONTRIBUTING.md).
