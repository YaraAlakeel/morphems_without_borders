# Morphological Productivity 

This module contains evaluation logic for morphological productivity experiments
based on prompt-driven language model generation.

The goal is to measure how well language models can generalize Arabic morphological patterns
by generating words from roots and templates.

---

## Installation

The productivity module is part of the `morpheme_metrics` package:

```bash
pip install -e .
```

---

## File Structure

```
productivity/
├── __init__.py     # Package exports
├── prompts.py      # Prompt templates and builders
├── utils.py        # Text normalization, Arabic cleanup, prediction extraction
└── README.md
```

---

## Quick Start

### 1. Building Prompts

```python
from morpheme_metrics.productivity import build_prompt_with_optional_oneshot, PATTERN_SHOT

# Basic morphological generation (root-pattern → word)
prompt = build_prompt_with_optional_oneshot(
    root="ك.ت.ب",
    template="فاعل",
    base_form="كاتب",
    lang="ara",           # "ara" for Arabic, "eng" for English
    use_oneshot=True      # Include one-shot example
)
print(prompt)

# With affixes (affix build)
prompt = build_prompt_with_optional_oneshot(
    root="ك.ت.ب",
    template="فاعل",
    base_form="كاتب",
    prefix="ال",
    suffix="ون",
    lang="ara",
    use_morpheme=True     # Enable affix application mode
)
print(prompt)
```

### 2. Processing Model Outputs

```python
from morpheme_metrics.productivity import extract_prediction, normalize_ar_for_compare

# Extract Arabic word from model output
model_output = "<think>some reasoning</think>الكاتبون"
prediction = extract_prediction(model_output, gold="الكاتبون")
# Returns: "الكاتبون"

# Normalize for comparison
normalized = normalize_ar_for_compare("الكَاتِبُون")  # Removes diacritics
```

### 3. Full Evaluation Workflow

```python
import json
from morpheme_metrics.productivity import (
    build_prompt_with_optional_oneshot,
    extract_prediction,
    normalize_ar_for_compare
)

# Load dataset
with open("data/productivity/productivity_dataset.json", encoding="utf-8") as f:
    data = json.load(f)

# Evaluate on real roots
correct = 0
total = 0

for example in data["real_roots"]:
    # Build prompt
    prompt = build_prompt_with_optional_oneshot(
        root=example["root"],
        template=example["template"],
        base_form=example["base_form"],
        prefix=example.get("prefix", ""),
        suffix=example.get("suffix", ""),
        lang="ara",
        use_morpheme=example["has_affix"]
    )
    
    # Get model prediction (replace with your model call)
    model_output = your_model.generate(prompt)
    
    # Extract and compare
    pred = extract_prediction(model_output, gold=example["full_form"])
    if normalize_ar_for_compare(pred) == normalize_ar_for_compare(example["full_form"]):
        correct += 1
    total += 1

print(f"Accuracy: {correct/total:.2%}")
```

---

## Dataset Format

Two dataset files are provided in `data/productivity/`:

| File | Description |
|------|-------------|
| `productivity_dataset.json` | Used in our experiments |
| `productivity_dataset_with_sentences.json` | Same data + `example_sentence` and `sentence_source` fields |

> **Note:** The `_with_sentences` variant contains example sentences for each entry. These sentences were **not used in our research** but are provided for downstream use.

The productivity dataset (`data/productivity/productivity_dataset.json`) contains:

```json
{
  "corpus_stats": { ... },
  "real_roots": [
    {
      "root": "ط.ل.ب",
      "template": "فعال",
      "base_form": "طلاب",
      "prefix": "ال",
      "suffix": "",
      "full_form": "الطلاب",
      "has_affix": true,
      "root_category": "high_frequency"
    }
  ],
  "nonce_roots": [ ... ]
}
```

---

## Prompt Modes

| Mode | Description |
|------|-------------|
| `use_morpheme=False` | Root + template → generate base word |
| `use_morpheme=True` | Base form + affixes → generate final form |

---

## API Reference

### `prompts.py`
- `build_prompt_with_optional_oneshot(root, template, *, base_form, prefix="", suffix="", lang="ara", use_oneshot=False, use_morpheme=False)` - Main prompt builder
- `PATTERN_SHOT` - One-shot examples dictionary (root: زرع)
- `temperature` - Default generation temperature (0.6)

### `utils.py`
- `extract_prediction(text, gold=None)` - Extract Arabic word from model output
- `normalize_ar_for_compare(s)` - Normalize Arabic for comparison
- `clean_ar_text(s)` - Remove diacritics, tags, zero-width chars
- `normalize_root(root)` - Clean root string (remove dots/spaces)
- `remove_arabic_diacritics_regex(s)` - Remove Arabic diacritics
- `remove_punct(s)` - Remove punctuation

