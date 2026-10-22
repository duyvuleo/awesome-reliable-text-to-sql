<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img alt="Reliable Text-to-SQL: a research collection on ambiguity, clarification, and unanswerability" src="assets/banner-light.svg" width="1280" height="360">
</picture>

# Awesome Reliable Text-to-SQL

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Validation](https://github.com/duyvuleo/awesome-reliable-text-to-sql/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/duyvuleo/awesome-reliable-text-to-sql/actions/workflows/checks.yml)
[![License: CC0](https://img.shields.io/badge/license-CC0%201.0-315da7)](LICENSE)

> Curated papers, systems, and datasets for Text-to-SQL that can recognize ambiguity, ask useful questions, and decline unsupported requests.

Natural-language questions do not always determine one SQL query, and a database cannot answer every request. This collection focuses on how NL2SQL agents detect these situations, resolve them through interaction or additional evidence, and evaluate when to answer or abstain.

[Browse papers](papers/README.md) · [Compare benchmarks](docs/benchmark-matrix.md) · [Try the examples](examples/README.md) · [Contribute](CONTRIBUTING.md)

**{{PAPER_COUNT}} annotated papers · {{SYSTEM_COUNT}} systems and tools · {{DATASET_COUNT}} dataset/benchmark entries**

Updated **{{UPDATED}}**. Each paper includes a concise summary, publication status, public sources, and a verification date. Core work and adjacent methods are marked separately. Resource counts include clearly labeled benchmark designs whose artifacts are not yet verified released.

## Contents

- [Start here](#start-here)
- [Healthcare benchmarks](#healthcare-benchmarks)
- [Choose a reading route](#choose-a-reading-route)
- [Worked examples](examples/README.md)
- [Papers](papers/README.md)
- [Systems and tools](systems/README.md)
- [Datasets and benchmarks](datasets/README.md)
- [Benchmark selection matrix](docs/benchmark-matrix.md)
- [Evaluation guide](docs/evaluation.md)
- [Recent additions](#recent-additions)
- [Search method and coverage](docs/search-method.md)
- [Contributing](CONTRIBUTING.md)
- [Related collections](#related-collections)

## Start here

{{START_HERE}}

## Healthcare benchmarks

**SCARE explicitly covers both ambiguous and unanswerable healthcare questions.** EHRSQL and its 2024 shared task provide complementary settings for answerability and reliable SQL answering.

| Benchmark | Ambiguity | Unanswerability | Clinical setting and task |
| --- | --- | --- | --- |
| **[SCARE](https://proceedings.mlr.press/v297/lee26b.html)** · [Data](datasets/README.md#scare-data) | **Explicit class** | **Explicit class** | MIMIC-III, MIMIC-IV and eICU; classify questions as answerable, ambiguous or unanswerable, and verify/correct candidate SQL. |
| [EHRSQL](https://arxiv.org/abs/2301.07695) · [Data](datasets/README.md#ehrsql-data) | Separate ambiguity-resolution task not verified | **Included** | MIMIC-III and eICU; hospital questions, temporal reasoning, SQL generation and held-out unanswerable questions. |
| [EHRSQL 2024](https://aclanthology.org/2024.clinicalnlp-1.62/) · [Data](datasets/README.md#ehrsql-2024-data) | Separate ambiguity-resolution task not verified | **Included** | MIMIC-IV demo; reliable SQL answering with an abstention option and penalties for incorrect answers. |

Use the [healthcare route in the benchmark matrix](docs/benchmark-matrix.md#healthcare-benchmarks) to compare protocols and access conditions. These are static benchmark tasks; their coverage does not establish live clinical clarification or deployment readiness.

## Choose a reading route

| Your question | Where to start |
| --- | --- |
| Can a request have several valid interpretations? | [Ambiguity and disambiguation](papers/README.md#ambiguity) |
| When should the system decline to generate SQL? | [Answerability and abstention](papers/README.md#answerability) |
| What should an agent ask, and when should it stop asking? | [Clarification and interaction](papers/README.md#interaction) |
| What changes when context spans documents, databases, or turns? | [Context and grounding](papers/README.md#context) |
| How do we test confidence and distinguish queries that happen to agree? | [Verification and uncertainty](papers/README.md#verification) |
| What can I actually run or download? | [Systems](systems/README.md) and [datasets](datasets/README.md), with availability notes |
| Which benchmark fits my experiment? | [Benchmark selection matrix](docs/benchmark-matrix.md) |
| Which healthcare benchmarks cover ambiguity or unanswerability? | [Healthcare benchmarks](#healthcare-benchmarks) |
| How do ambiguity, unsupported information, and an empty answer differ? | [Three runnable SQLite walkthroughs](examples/README.md) |

## Scope

We include work that directly studies ambiguity, underspecification, answerability, clarification, or abstention in natural-language querying of relational databases. We also include selected verification, uncertainty, and contextual-grounding methods when their relevance to those problems is explicit. Generic SQL-generation systems and broad agent frameworks belong in the related collections unless they provide a concrete capability relevant to this scope.

An ambiguous request, an unsupported request, a model error, and a valid query returning no rows are different cases. Likewise, a publication, an announced repository, released artifacts, and independently reproduced results are different kinds of evidence. The annotations preserve these distinctions; inclusion is not a deployment endorsement.

## Recent additions

{{RECENT}}

See the [changelog](CHANGELOG.md) for material changes and the [dated search records](docs/search-log/README.md) for coverage and unresolved leads. This is a living curated collection, not a claim of complete literature coverage.

## Contributing

Suggest a resource or correction through an [issue](https://github.com/duyvuleo/awesome-reliable-text-to-sql/issues/new/choose) or pull request. Include a primary source and explain the connection to ambiguity or unanswerability. See [CONTRIBUTING.md](CONTRIBUTING.md) for the entry format and checks.

The canonical records are [papers.json](data/papers.json) and [resources.json](data/resources.json). The indexes are generated, so contributors only need to maintain one record per work.

## Related collections

- [Awesome Text2SQL](https://github.com/eosphoros-ai/Awesome-Text2SQL) — Broader Text-to-SQL papers, benchmarks, and tooling.
- [NL2SQL Handbook](https://github.com/HKUSTDial/NL2SQL_Handbook) — A broader research and engineering reference.
- [Awesome AI Co-Scientist](https://github.com/duyvuleo/awesome-ai-co-scientist) — A companion annotated collection for agentic scientific discovery.
- [Awesome](https://github.com/sindresorhus/awesome) — Community guidance for curated lists. The badge identifies the list format; it does not assert inclusion in the central index.

## License

Original annotations, catalog records, and maintenance code in this repository are dedicated under [CC0 1.0](LICENSE). Linked papers, software, and datasets retain their own licenses and access conditions. No third-party papers or datasets are redistributed here.
