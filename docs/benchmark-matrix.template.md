# Benchmark selection matrix

[Overview](../README.md) · [Dataset and access details](../datasets/README.md) · [Evaluation guide](evaluation.md)

Compare **{{BENCHMARK_COUNT}} dataset and benchmark entries** by the question you want to test. The two tables below cover [task coverage](#task-coverage) and [evaluation and access](#evaluation-and-access). Names link to the detailed resource index; expandable sources identify the public evidence used for each comparison.

## Choose a starting point

| If you want to evaluate… | Consider… | Check before using it |
| --- | --- | --- |
| Recovery of several valid SQL interpretations | [AmbiQT](#ambiqt-data), [AMBROSIA](#ambrosia-data) | Interpretation coverage differs from selecting the actual user's intent. |
| Detection of problematic or unanswerable requests | [TriageSQL](#triagesql-data), [MMSQL](#mmsql-data), [SCARE](#scare-data) | Classification labels, response tasks and candidate-SQL inputs differ. |
| SQL answering with an abstention option | [TrustSQL](#trustsql-data), [EHRSQL](#ehrsql-data), [EHRSQL 2024](#ehrsql-2024-data) | Record the error penalty, answer coverage and database access conditions. |
| Healthcare ambiguity and unanswerability | [SCARE](#scare-data), [EHRSQL](#ehrsql-data), [EHRSQL 2024](#ehrsql-2024-data) | SCARE explicitly labels both; the EHRSQL benchmarks target answerability and reliable SQL answering. |
| SQL after receiving clarification | [PRACTIQ](#practiq-data), [CLARITY](#clarity-data), [CLAMBSQL](#clambsql-data) | Supplied clarification evaluates a different step from choosing what to ask. |
| An agent that conducts clarification | [ABISS](#abiss-data), [ARCS](#arcs-data), [BIRD-Interact](#bird-interact-data), [TIDE-Bench](#tide-bench-data) | Pin the user simulator, interaction budget, protocol and available release. |
| Continued interaction as requests or database state change | [DySQL-Bench](#dysql-data), [BIRD-Interact](#bird-interact-data), [TIDE-Bench](#tide-bench-data) | Request revisions, SQL writes and clarification dependencies are different test conditions. |
| Business context or larger SQL workflows | [EntSQL](#entsql-data), [Spider 2.0](#spider2-data), [LiveSQLBench](#livesqlbench-data) | These adjacent tasks do not establish ambiguity detection or unanswerability coverage. |

These are starting options, not rankings. Match the task and access conditions to your experiment before comparing reported results.

## Healthcare benchmarks

**For explicit coverage of both ambiguity and unanswerability, start with [SCARE](#scare-data).** It jointly classifies question answerability and verifies/corrects a supplied SQL candidate over MIMIC-III, MIMIC-IV and eICU. This is a post-hoc task rather than a live clarification dialogue. [Primary source](https://proceedings.mlr.press/v297/lee26b.html).

[EHRSQL](#ehrsql-data) includes held-out unanswerable questions over MIMIC-III/eICU, while [EHRSQL 2024](#ehrsql-2024-data) evaluates reliable answering and abstention using MIMIC-IV demo. A separate ambiguity-resolution task is not established in the checked sources for these two entries. Use their rows below for the precise coverage and access notes. [EHRSQL paper](https://arxiv.org/abs/2301.07695) · [EHRSQL 2024 task](https://github.com/glee4810/ehrsql-2024).

Public question/SQL annotations do not grant access to every underlying EHR database. Check the linked resource's version, license and access conditions before running an experiment. Benchmark correctness is distinct from clinical validity or deployment readiness.

## How to read the matrix

- **Yes** means an explicit task, category or protocol is described in the checked sources. It does not mean a model has solved it.
- **Not targeted** describes the recorded benchmark task, rather than asserting the dataset can never contain such a case.
- **Not reported** means the feature was not established in the checked sources. It must not be treated as a confirmed absence.
- **Supplied clarification** is annotated feedback or conversation history available to the evaluated model. **Generated clarification** is elicited by the agent at evaluation time. **Mixed** means the source defines different tasks or protocols; read the row's qualification.
- **Recorded** includes offline generated conversations as well as human dialogue. **Simulated** means a user responds during the evaluation. **Static** can still involve database/tool execution; it does not imply user dialogue.
- **Public artifacts** means visible task files or an official download link was checked. It does not establish execution, reproduction, or unrestricted access to every required database. **Release unverified** includes paper-described benchmarks and placeholders.

## Task coverage

{{COVERAGE_TABLE}}

## Evaluation and access

The evaluation column identifies the task or metric family, not a comparable score. Expand access details for download qualifications, licensing and upstream dependencies. Access descriptions come from the same canonical records as the [dataset index](../datasets/README.md).

{{PROTOCOL_TABLE}}

## Verification boundaries

Comparison fields are checked against public papers and official artifact pages. The latest recorded comparison check is **{{UPDATED}}**; each row retains its own source locators and check date in [benchmarks.json](../data/benchmarks.json). Labels summarize the particular setting described by those sources; they do not merge all versions of a project into a single capability claim. Missing information stays explicit.

The matrix includes the dataset/benchmark entries already cataloged here. It is not an exhaustive list of every evaluation setting in the literature. Scientific claims, download status, licenses and implementation reproducibility are separate checks. No linked experiments were executed for this matrix.

To suggest a correction, identify the benchmark and comparison field and include a public primary source through the [correction form](https://github.com/duyvuleo/awesome-reliable-text-to-sql/issues/new?template=correction.yml).
