## Intrinsic alignment metrics

This folder contains the evaluation code for tokenizer-morphology alignment.

> **Gold data:** Pre-extracted gold segmentation files are in [`data/alignment/`](../../data/alignment/).
> To re-extract them from raw ATB/BOLT files, see [`data/alignment/README.md`](../../data/alignment/README.md).

### What is in this folder
| File | Purpose | Outputs |
|---|---|---|
| `cli.py` | CLI entry point | `morpheme-eval` command |
| `token_totals.py` | Corpus totals | `total_sentences`, `total_words`, `total ground truth tokens`, `total predicted tokens` |
| `fertility.py` | Fertility | `fertility_score` |
| `Morphem_F1.py` | Morpheme span PRF1 | `morpheme_precision`, `morpheme_recall`, `morpheme_F1` |
| `Morpheme_boundary_F1.py` | Boundary PRF1 | `boundary_precision`, `boundary_recall`, `boundary_F1` |
| `morpheme_coverage_rate.py` | Morpheme coverage rate | `morpheme_coverage_rate` |
| `io_utils.py` | Span file parser | one sentence/line, `[...]` per word, `(start,end)` per span |


### CLI usage
From the repo root:

```bash
morpheme-eval --help
```
Compute all intrinsic metrics:

```bash
morpheme-eval --gold GOLD.txt --pred PRED1.txt --metrics all
```

Compute a single metric:

```bash
morpheme-eval --gold GOLD.txt --pred PRED1.txt --metrics token_totals
morpheme-eval --gold GOLD.txt --pred PRED1.txt --metrics fertility
morpheme-eval --gold GOLD.txt --pred PRED1.txt --metrics morpheme_f1
morpheme-eval --gold GOLD.txt --pred PRED1.txt --metrics boundary_f1
morpheme-eval --gold GOLD.txt --pred PRED1.txt --metrics coverage_rate
```

Write JSONL output (one record per pred file):

```bash
morpheme-eval --gold GOLD.txt --pred PRED1.txt PRED2.txt --metrics all --output results.jsonl
```


## Equations

We quantify how closely tokenizer outputs align with Arabic morphological structure using complementary metrics:

$$
\begin{aligned}
&\textbf{Notation.}\;\; W:\text{ set of words. For each } w\in W: \\
&T(w):\text{ predicted token sequence} \\
&G(w):\text{ gold morpheme segmentation} \\
&B(w):\text{ set of gold morpheme-internal boundary positions} \\
&\hat{B}(w):\text{ set of predicted morpheme-internal boundary positions} \\
&M(w):\text{ set of gold morpheme spans} \\
&\hat{M}(w):\text{ set of predicted morpheme spans}
\end{aligned}
$$


### Fertility
Average number of predicted tokens per word:

$$
\mathrm{Fert} = \frac{1}{|W|}\sum_{w \in W} |T(w)|
$$

### Morpheme boundary precision/recall/F1
Measures alignment between predicted and gold morpheme-internal boundary positions:

$$
\mathrm{BRecall}=\frac{\sum_w |B(w)\cap \hat{B}(w)|}{\sum_w |B(w)|},\quad
\mathrm{BPrecision}=\frac{\sum_w |B(w)\cap \hat{B}(w)|}{\sum_w |\hat{B}(w)|}
$$

### Morpheme F1 (span-level; stricter)
Counts a morpheme as correct only when its full span matches (both start and end boundaries):

$$
\mathrm{MorphemeF1} = \frac{1}{|W|}\sum_{w \in W}\frac{2|M(w)\cap \hat{M}(w)|}{|M(w)| + |\hat{M}(w)|}
$$

### Morpheme Coverage Rate (MCR)
Proportion of gold morphemes preserved intact inside a predicted token span:

$$
\mathrm{MCR}=\frac{1}{|W|}\sum_{w \in W}\frac{|\{m\in M(w): \exists \hat{m}\in \hat{M}(w), m\subseteq \hat{m}\}|}{|M(w)|}
$$


