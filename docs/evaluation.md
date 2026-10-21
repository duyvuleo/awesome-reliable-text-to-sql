# Reading results across benchmarks

[Back to the collection](../README.md)

The following questions help decide whether an evaluation matches an intended use. This guide synthesizes the public sources linked below; it does not reproduce their experiments.

| Check | Why it matters | Representative reading |
| --- | --- | --- |
| Does the benchmark allow several SQL interpretations? | A single reference can reject another supported interpretation or hide a silent choice. | [AmbiQT](https://aclanthology.org/2023.emnlp-main.436/), [AMBROSIA](https://arxiv.org/abs/2406.19073) |
| Is a clarification supplied, selected, or generated interactively? | Completing SQL after receiving clarification tests a different capability from deciding what to ask. | [PRACTIQ](https://aclanthology.org/2025.naacl-long.13/), [ABISS](https://arxiv.org/abs/2607.23340) |
| Are unanswerable requests part of the test? | Accuracy on answerable examples does not measure whether unsupported requests are declined. | [TrustSQL](https://arxiv.org/abs/2403.15879), [EHRSQL 2024](https://aclanthology.org/2024.clinicalnlp-1.62/) |
| Who provides user feedback? | Scripted replies, language-model simulators, and people produce different evidence about interaction. | [CoSQL](https://aclanthology.org/D19-1204/), [BIRD-INTERACT](https://github.com/bird-bench/BIRD-Interact) |
| What are the costs of asking, answering incorrectly, and abstaining? | A system that answers fewer questions may appear more accurate while serving fewer users. | [TrustSQL](https://arxiv.org/abs/2403.15879), [RTS](https://arxiv.org/abs/2501.10858) |
| Which database instances determine SQL correctness? | Queries can agree on one database and disagree on another. | [Distilled test suites](https://aclanthology.org/2020.emnlp-main.29/), [SpotIt](https://arxiv.org/abs/2510.26840), [ParSEval](https://www.vldb.org/pvldb/vol18/p4750-miao.pdf) |
| Is confidence evaluated against independent correctness evidence? | Calibration and selective risk inherit limitations of their correctness labels. | [Certified Against Which Oracle?](https://arxiv.org/abs/2609.25938) |
| What is released, and what was actually tested? | A generation pipeline, its output dataset, and an evaluated system are separate artifacts. | [CLARITY public release](https://github.com/duyvuleo/clarity) |

For any quantitative comparison, record the benchmark version and split, database snapshot, accepted answers, model and prompt configuration, access to external context, interaction budget, user or simulator protocol, metric denominator, and evaluation oracle. Keep paper-reported results separate from independent reproductions. We omit a combined leaderboard because these conditions differ across the collection.

Useful measures include ambiguity detection and localization, recovery of valid interpretations, answerability classification, clarification usefulness, end-to-end task success, incorrect-answer rate, answer coverage, and interaction cost. Each measure addresses a different decision; none is a substitute for the others.
