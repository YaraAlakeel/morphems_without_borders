# Alignment Data

This folder contains gold morpheme-segmented alignment files and the pipeline used to extract them.

## Pre-extracted files

| File | Description |
|------|-------------|
| `atb3_segmented_offsets.txt` | ATB3 gold morpheme byte-offsets |
| `bolt_segmented_offsets.txt` | BOLT gold morpheme byte-offsets |

These files are ready to use with `morpheme-eval`. No extraction step is needed unless you want to:
- **Run a tokenizer** on the original (unsegmented) source text to produce your own predicted offsets for evaluation.
- View the original UTF-8 segmentation before offset conversion.
- Understand how the gold data was extracted from the raw ATB/BOLT files.
- Regenerate the data from scratch for reproducibility.


## Re-extracting from raw data (optional)

### Prerequisites

Install the optional `data-extraction` dependency:

```bash
pip install .[data-extraction]
```

This installs [`camel-tools`](https://pypi.org/project/camel-tools/), which provides the `camel_transliterate` CLI used for Buckwalter → UTF-8 conversion.

You also need access to the raw LDC data:
- **ATB3**: `atb3_v3_2_LDC2010T08` → `data/integrated/`
- **BOLT**: `bolt_arz_tbnk-cts_LDC2021T12` → `data/integrated/`

### Usage

```bash
python data/alignment/extract_alignment_data.py \
  --input_dir <path_to_integrated_files> \
  --output_dir data/alignment \
  --corpus_name atb3 \
  --strip_ids
```

### Arguments

| Argument | Description |
|----------|-------------|
| `--input_dir` | Path to ATB/BOLT integrated data directory (contains `.txt` files) |
| `--output_dir` | Path to write output files |
| `--corpus_name` | Prefix for output filenames (e.g., `atb3` or `bolt`). Default: `atb3` |
| `--strip_ids` | Remove CHUNK IDs from output (required for `morpheme-eval`) |

### Pipeline steps

1. **Parse & transliterate** — Parse ATB/BOLT integrated files, extract morpheme segments, batch-convert Buckwalter to UTF-8 via `camel_transliterate`.
2. **Normalize لام التعريف** — Normalize `ل+ال` to `ل+ل` in segmented output.
3. **Generate offsets** — Compute byte-level morpheme boundary offsets.

 > Note: In the treebank, words beginning with `لل` (e.g., `للمدرسة`) are segmented as `ل+ال+مدرسة`, but the `ا` is only part of the treebank segmentation. A tokenizer processing the same word will not introduce this extra `ا`, so we normalize `ل+ال` to `ل+ل` to ensure consistency between the gold segmentation and tokenizer output.

### Outputs

| File | Description |
|------|-------------|
| `<corpus>_source.txt` | Original Arabic surface forms |
| `<corpus>_segmented_utf8.txt` | Morpheme-segmented words in UTF-8 |
| `<corpus>_segmented_offsets.txt` | Byte-level morpheme boundary offsets |
