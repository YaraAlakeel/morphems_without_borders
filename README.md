# Morphems Without Borders: Evaluating Root–Pattern Morphology in Arabic Tokenizers and LLMs

This repository contains the official evaluation code for **Morphems Without Borders**, a study of how LLMs and their tokenization schemes represent and generate **Arabic root–pattern morphology**. 
We evaluate (i) tokenizer–morphology alignment against gold segmentation and (ii) model performance on productive root–pattern generation using a newly introduced benchmark. 

**What’s included?**
- **Intrinsic (alignment):** fertility, boundary F1, morpheme F1, and morpheme coverage rate computed from span-based gold/pred segmentations.
- **Extrinsic (productivity):** newly curated benchmark dataset and a prompt-based productivity evaluation utilities.

> Paper link: **https://arxiv.org/abs/2603.15773**

---

## Repository structure

- `morpheme_metrics/`: installable Python package
  - `morpheme_metrics/alignment/`: intrinsic alignment metrics (CLI: `morpheme-eval`)
  - `morpheme_metrics/productivity/`: productivity evaluation utilities (Python library)
- `data/`: 
  - `data/alignment/`: gold and predicted segmentation offset files (ATB3, BOLT) and data extraction pipeline.
    - `data/alignment/pred/`: predicted segmentation offsets from evaluated tokenizers.
  - `data/productivity/`: manually curated benchmark for productivity experiments 


---

## Quickstart 

From the repo root run:


Option A : `venv` + `pip`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
```
Option B : `uv`

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install . 
```

> **Note**: If you encounter an error related to hardlinking during installation, use the following command instead:
> ```powershell
> uv pip install . --link-mode=copy
> ```

To also install the **data extraction** dependencies (needed only if you want to re-extract alignment data from raw ATB/BOLT files):

```powershell
pip install .[data-extraction]
```
>  For re-extracting alignment data from raw ATB/BOLT files, see [`data/alignment/README.md`](data/alignment/README.md).

### Intrinsic (alignment) — CLI

The alignment metrics are exposed via the `morpheme-eval` command-line tool:

```powershell
morpheme-eval --help
```

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


### Extrinsic (productivity) — Python Library

The productivity utilities are used as a Python library (no CLI). Evaluate how well LLMs generalize Arabic morphological patterns by generating words from roots and templates:

```python
from morpheme_metrics.productivity import (
    build_prompt_with_optional_oneshot,
    extract_prediction,
    normalize_ar_for_compare
)

# 1. Build a prompt for the LLM
prompt = build_prompt_with_optional_oneshot(
    root="ك.ت.ب",
    template="فاعل",
    base_form="كاتب",
    lang="ara",
    use_oneshot=True
)

# 2. Send to your LLM and get response
model_output = your_model.generate(prompt)

# 3. Extract prediction and compare with gold
pred = extract_prediction(model_output, gold="كاتب")
is_correct = normalize_ar_for_compare(pred) == normalize_ar_for_compare("كاتب")
```

For full documentation and dataset format, see [`morpheme_metrics/productivity/README.md`](morpheme_metrics/productivity/README.md).

---

## Citation

If you use this code, please cite:

```bibtex
% TODO: add BibTeX
```

