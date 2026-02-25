
#  `morpheme_metrics/productivity/README.md`

# Morphological Productivity 

This contains the evaluation logic for morphological productivity experiments
based on prompt-driven language model generation.

The goal of this is to provide **model-agnostic evaluation utilities** for
measuring how language models generalize morphological patterns.

---

## Scope

This includes reusable logic for:

- Prompt template construction
- Prompt formatting utilities
- Output normalization
- Productivity scoring functions



---

## Expected File Structure

The productivity module should contain files similar to:


productivity/
* `prompts.py`         : Prompt templates and builders
* `scoring.py`         : Productivity scoring functions
* `io.py`              : Input/output helpers (JSON schema handling)



---

## Typical Workflow

1. Load prompt dataset
2. Generate model outputs using an external runner
3. Normalize model outputs
4. Apply productivity scoring

