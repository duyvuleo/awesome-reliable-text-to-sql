# Contributing

Thank you for helping maintain a focused and useful collection.

1. Check whether the paper or resource already appears in `data/papers.json` or `data/resources.json`.
2. Supply a public primary source: proceedings, DOI landing page, arXiv record, author project page, or official repository. Search snippets and third-party summaries can help discovery but are insufficient evidence for an entry.
3. Explain how the work addresses ambiguity, underspecification, answerability, clarification, abstention, or a directly relevant evaluation problem in Text-to-SQL.
4. Write a concise original summary of the task and mechanism, followed by its evaluation scope or practical boundary. Do not copy abstracts or promotional claims. Label preprints and adjacent work explicitly.
5. Check the actual artifact before asserting that code or data is released. A repository link alone does not establish a working implementation or downloadable dataset. Record restrictions, placeholders, and archived repositories.
6. For dataset/benchmark additions, also update `data/benchmarks.json` with source-supported comparison fields and explicit unknowns. See [the benchmark matrix](docs/benchmark-matrix.md).
7. Update the dated search log and changelog for material additions or corrections, then run the checks below.

```bash
python3 scripts/render.py
python3 scripts/validate.py
python3 scripts/render.py --check
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Edit canonical JSON and the README template rather than generated indexes. See [the data format](data/README.md). Keep citations next to claims, use stable identifiers, and merge publication/preprint versions of the same work unless they are materially distinct studies.

Only publicly available, independently checkable information is eligible. Do not submit confidential material, nonpublic drafts, credentials, private correspondence, or restricted datasets. A public list entry does not grant permission to redistribute its linked materials.

AI-assisted suggestions are welcome when the contributor verifies sources and reviews the resulting text. The maintainer may request evidence, narrow claims, or remove an entry that does not meet the scope. Corrections and newly available artifacts are as useful as new papers.
