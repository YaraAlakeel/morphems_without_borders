# Morphems Without Borders: Evaluating Root–Pattern Morphology in Arabic Tokenizers and LLMs

This repository contains the official evaluation code for **Morphems Without Borders**, a study of how LLMs and their tokenization schemes represent and generate **Arabic root–pattern morphology**. 
We evaluate (i) tokenizer–morphology alignment against gold segmentation and (ii) model performance on productive root–pattern generation using a newly introduced benchmark. 

**What’s included?**
- **Intrinsic (alignment):** fertility, boundary F1, morpheme F1, and morpheme coverage rate computed from span-based gold/pred segmentations.
- **Extrinsic (productivity):** newly curated benchmark dataset and a prompt-based productivity evaluation utilities.

> Paper link: **link**

---

## Repository structure

- `morpheme_metrics/`: installable Python package
  - `morpheme_metrics/alignment/`: intrinsic alignment metrics
  - `morpheme_metrics/productivity/`: productivity evaluation utilities
- `data/`: 
  - `data/alignment/`: gold segmentation files (ATB3, BOLT).
  - `data/productivity/`: manually curated benchmark for productivity experiments
- `runners/`: scripts to run models and produce predictions 


---

## Quickstart 

From the repo root run:


Option A : `venv` + `pip`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .

morpheme-eval --help
```
Option B : `uv`

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install .

morpheme-eval --help
```

### Intrinsic (alignment):

Run all intrinsic alignment evaluation:
```bash
morpheme-eval \
  --gold data/alignment/atb3_segmented_offsets.txt \
  --pred data/alignment/atb3_gpt4_offsets.txt \
  --metrics all

```
Save results to a file:
```bash
morpheme-eval \
  --gold data/alignment/atb3_segmented_offsets.txt \
  --pred data/alignment/atb3_gpt4_offsets.txt \
  --metrics all \
  --output output/results.jsonl

```
**Notes** : 
 * All intrinsic metrics read character-level offsets  files 
 * Gold and pred files must be aligned line-by-line (same number of lines, same order, same number of words).
 * For more details about the intrinsic alignment evaluation, see [`morpheme_metrics/alignment/README.md`](morpheme_metrics/alignment/README.md).


### Extrinsic (productivity):

The productivity section (`morpheme_metrics/productivity/`) contains evaluation logic (templates, normalization, scoring). Model execution code should live in `runners/`, which should:
1) load the productivity dataset,
2) run a model to generate outputs,
3) write outputs to disk,
4) call productivity scoring utilities.

See [`morpheme_metrics/productivity/README.md`](morpheme_metrics/productivity/README.md).

---

## Citation

If you use this code, please cite:

```bibtex
% TODO: add BibTeX
```

