# Datasets and benchmarks

[Back to the overview](../README.md)

Choose a dataset with the [benchmark selection matrix](../docs/benchmark-matrix.md).

Availability and licenses are source-specific. A linked paper, project, or dataset is not evidence of independent replication.

## Contents

- [All datasets and benchmarks](#all-datasets-and-benchmarks)
- [Healthcare benchmarks](#healthcare-benchmarks)

{{DATASET_CONTENTS}}

## All datasets and benchmarks

Groups use the publication year of the most recent linked paper, newest first. These are not dataset release dates. Resources without a linked paper appear in their own group. Names remain alphabetized within each year.

{{DATASET_TABLE}}

## Healthcare benchmarks

**SCARE explicitly covers both ambiguous and unanswerable healthcare questions.** EHRSQL and its 2024 shared task provide complementary settings for answerability and reliable SQL answering.

| Benchmark | Ambiguity | Unanswerability | Clinical setting and task |
| --- | --- | --- | --- |
| **[SCARE](https://proceedings.mlr.press/v297/lee26b.html)** · [Data](README.md#scare-data) | **Explicit class** | **Explicit class** | MIMIC-III, MIMIC-IV and eICU; classify questions as answerable, ambiguous or unanswerable, and verify/correct candidate SQL. |
| [EHRSQL](https://arxiv.org/abs/2301.07695) · [Data](README.md#ehrsql-data) | Separate ambiguity-resolution task not verified | **Included** | MIMIC-III and eICU; hospital questions, temporal reasoning, SQL generation and held-out unanswerable questions. |
| [EHRSQL 2024](https://aclanthology.org/2024.clinicalnlp-1.62/) · [Data](README.md#ehrsql-2024-data) | Separate ambiguity-resolution task not verified | **Included** | MIMIC-IV demo; reliable SQL answering with an abstention option and penalties for incorrect answers. |

Use the [healthcare route in the benchmark matrix](../docs/benchmark-matrix.md#healthcare-benchmarks) to compare protocols and access conditions. These are static benchmark tasks; their coverage does not establish live clinical clarification or deployment readiness.
