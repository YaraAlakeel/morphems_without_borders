"""
ATB Alignment Data Extraction Pipeline
=======================================
Extracts morpheme-aligned data from Arabic Treebank (ATB) or BOLT integrated files.

Pipeline Steps:
    1. Parse ATB/BOLT integrated files → convert Buckwalter to UTF-8, apply normalization and filtering.
    2. Normalize لام التعريف ( ل+ل → ل+ال ) in segmented UTF-8 output.
    3. Generate byte-level offsets for each morpheme boundary.

Outputs (written to --output_dir):
    - <corpus>_source.txt                  : Original Arabic surface forms.
    - <corpus>_segmented_utf8.txt          : Morpheme-segmented words in UTF-8.
    - <corpus>_segmented_offsets.txt        : Byte-level morpheme boundary offsets.

Usage:
    python extract_alignment_data.py --input_dir <path_to_integrated_files> --output_dir <output_path> --corpus_name atb3
    (Add --strip_ids to remove CHUNK IDs from output files, if desired for downstream metrics code.)
Notes:
    - Requires `camel_transliterate` command-line tool for Buckwalter → UTF-8 conversion.
    - Designed for ATB/BOLT integrated files with specific formatting (s: and t: lines).
    - Normalization removes diacritics, tatweel, zero-width chars, and filters out non-Arabic tokens (numbers, punctuation, English).
"""

import os
import re
import argparse
import tempfile
import subprocess
from pathlib import Path


# ──────────────────────────────────────────────
# Regex Patterns
# ──────────────────────────────────────────────
_NUM_PATTERN = r"\d+(?:[./-]\d+)*"
_PUN_PATTERN = r'[:!\-"/*+.,?؟،()\[\]{}]+'
_ENG_PATTERN = r"[A-Za-z]+(?:[.\-',][A-Za-z]+)*\.?"
REMOVE_RE = re.compile(rf"(?:{_NUM_PATTERN}|{_ENG_PATTERN}|{_PUN_PATTERN})")
BAD_NUM_RE = re.compile(r"^[0-9][0-9.\-\/]*[0-9]$")
STRIP_PUN_RE = re.compile(r"^[\W_]+|[\W_]+$")
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
NULL_MORPH_RE = re.compile(r"\+?\(?\[?(null|نلل)\]?\)?")


# ──────────────────────────────────────────────
# Normalization Helpers
# ──────────────────────────────────────────────
def contains_arabic(text: str) -> bool:
    return bool(ARABIC_RE.search(text))


def remove_diacritics(text: str) -> str:
    return re.sub(r"[\u064B-\u0652\u0670]", "", text)


def remove_tatweel_and_zero_width(text: str) -> str:
    return re.sub(r"[\u0640\u200c\u200d]", "", text)


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return remove_tatweel_and_zero_width(remove_diacritics(text))


def clean_plus_markers(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\++", "+", text)
    text = re.sub(r"(^\+|\+$)", "", text)
    text = re.sub(r"\s*\+\s*", "+", text)
    return text


def normalize_and_filter(text: str) -> str:
    """Normalize text and remove non-Arabic tokens (numbers, punctuation, English)."""
    if not text:
        return ""
    text = normalize_text(text)
    stripped = STRIP_PUN_RE.sub("", text)
    if not stripped:
        return ""
    if REMOVE_RE.fullmatch(stripped) or BAD_NUM_RE.fullmatch(stripped):
        return ""
    return stripped


# ──────────────────────────────────────────────
# Step 1: Parse ATB/BOLT Integrated Files
# ──────────────────────────────────────────────
def parse_integrated_files(input_dir: str) -> dict:
    """
    Parse all .txt files in the ATB/BOLT integrated directory.

    Returns a dict mapping chunk_id → {original, segmented, segmented_utf8}
    where segmented_utf8 has None placeholders for Arabic words (filled later).
    """
    sentence_data = {}
    batch_morphs = []
    translit_mapping = []

    def store_chunk(chunk_id, s_nodes, t_nodes):
        original = [normalize_text(s["form"]) for s in s_nodes]
        segmented = []
        segmented_utf8 = []

        for i, s in enumerate(s_nodes):
            morphs = [
                NULL_MORPH_RE.sub("", t["bw"])
                for t in t_nodes
                if s["t_start"] <= t["index"] <= s["t_end"] and t["bw"]
            ]
            if not morphs:
                morphs = [s["form"]]

            segmented.append(normalize_text("+".join(morphs)))

            if contains_arabic(s["form"]):
                batch_morphs.append(morphs)
                translit_mapping.append((chunk_id, i, morphs))
                segmented_utf8.append(None)
            else:
                segmented_utf8.append(normalize_text("+".join(morphs)))

        sentence_data[chunk_id] = {
            "original": original,
            "segmented": segmented,
            "segmented_utf8": segmented_utf8,
        }

    def parse_single_file(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_s_nodes = []
        current_t_nodes = []
        chunk_id = None

        for line in lines:
            line = line.strip()
            if line.startswith("CHUNK:"):
                if chunk_id and current_s_nodes and current_t_nodes:
                    store_chunk(chunk_id, current_s_nodes, current_t_nodes)
                chunk_id = line
                current_s_nodes = []
                current_t_nodes = []
                continue

            if line.startswith("s:"):
                parts = line.split("\u00b7")
                if len(parts) >= 7:
                    current_s_nodes.append({
                        "form": parts[1].strip(),
                        "t_start": int(parts[5].strip()),
                        "t_end": int(parts[6].strip()),
                    })

            elif line.startswith("t:"):
                parts = line.split("\u00b7")
                if len(parts) >= 10:
                    current_t_nodes.append({
                        "bw": parts[4].strip(),
                        "index": len(current_t_nodes),
                    })

        if chunk_id and current_s_nodes and current_t_nodes:
            store_chunk(chunk_id, current_s_nodes, current_t_nodes)

    # Parse all files in the input directory
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".txt"):
            parse_single_file(os.path.join(input_dir, filename))

    # Batch transliterate all Arabic morphemes (Buckwalter → UTF-8)
    all_morphs_flat = [morph for group in batch_morphs for morph in group]

    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".txt") as tmp:
        tmp_input_path = tmp.name
        tmp.write("\n".join(all_morphs_flat))

    tmp_output_path = tmp_input_path.replace(".txt", "_out.txt")

    subprocess.run(
        ["camel_transliterate", "--scheme", "bw2ar", "-o", tmp_output_path, tmp_input_path],
        check=True,
    )

    with open(tmp_output_path, "r", encoding="utf-8") as f:
        all_transliterated = [normalize_text(line.strip()) for line in f]

    os.remove(tmp_input_path)
    os.remove(tmp_output_path)

    # Assign transliterated morphemes back to their positions
    idx = 0
    for chunk_id, word_idx, morphs in translit_mapping:
        utf8_morphs = all_transliterated[idx : idx + len(morphs)]
        idx += len(morphs)
        sentence_data[chunk_id]["segmented_utf8"][word_idx] = normalize_text("+".join(utf8_morphs))

    return sentence_data


def write_parsed_output(sentence_data: dict, output_dir: str, corpus_name: str, strip_ids: bool = False):
    """Write filtered source and segmented UTF-8 files."""
    source_path = os.path.join(output_dir, f"{corpus_name}_source.txt")
    seg_utf8_path = os.path.join(output_dir, f"{corpus_name}_segmented_utf8.txt")

    with open(source_path, "w", encoding="utf-8") as f_src, \
         open(seg_utf8_path, "w", encoding="utf-8") as f_seg:

        for chunk_id, data in sentence_data.items():
            filtered_source = []
            filtered_seg_utf8 = []

            for orig, seg_utf8 in zip(data["original"], data["segmented_utf8"]):
                norm_orig = normalize_and_filter(orig)
                norm_seg = clean_plus_markers(normalize_and_filter(seg_utf8))

                if norm_orig:
                    filtered_source.append(norm_orig)
                    filtered_seg_utf8.append(norm_seg)

            if filtered_source:
                src_line = ' '.join(filtered_source)
                seg_line = ' '.join(filtered_seg_utf8)
                if strip_ids:
                    f_src.write(f"{src_line}\n")
                    f_seg.write(f"{seg_line}\n")
                else:
                    f_src.write(f"{chunk_id}\t{src_line}\n")
                    f_seg.write(f"{chunk_id}\t{seg_line}\n")

    print(f"  -> {source_path}")
    print(f"  -> {seg_utf8_path}")


# ──────────────────────────────────────────────
# Step 2: Normalize لام التعريف  (ل+ال → ل+ل)
# ──────────────────────────────────────────────
def normalize_lam_al(line: str, strip_ids: bool = False) -> str:
    """Replace morpheme pattern ل+ال with ل+ل in a single line."""
    parts = line.strip().split("\t", 1)
    if len(parts) == 2:
        chunk_id, sentence = parts
    else:
        chunk_id, sentence = None, parts[0]

    words = sentence.split()
    normalized_words = [re.sub(r"\bل\+ال\b", "ل+ل", w) for w in words]
    result = " ".join(normalized_words)

    if strip_ids or chunk_id is None:
        return result
    return f"{chunk_id}\t{result}"


def apply_lam_normalization(output_dir: str, corpus_name: str, strip_ids: bool = False):
    """Read segmented UTF-8 file, normalize لام, overwrite in place."""
    seg_utf8_path = os.path.join(output_dir, f"{corpus_name}_segmented_utf8.txt")

    with open(seg_utf8_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(seg_utf8_path, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip():
                normalized = normalize_lam_al(line, strip_ids=strip_ids)
                f.write(normalized + "\n")

    print(f"  -> Normalized ل+ال → ل+ل in {seg_utf8_path}")


# ──────────────────────────────────────────────
# Step 3: Generate Byte-Level Morpheme Offsets
# ──────────────────────────────────────────────
def compute_offsets(line: str, strip_ids: bool = False) -> str | None:
    """Convert one segmented line → chunk_id + byte offsets per word."""
    parts = line.strip().split("\t")
    if len(parts) == 2:
        chunk_id, sentence = parts
    elif len(parts) == 1:
        chunk_id, sentence = None, parts[0]
    else:
        return None

    offsets_per_word = []

    for segmented_word in sentence.split():
        morphemes = segmented_word.split("+")
        cursor = 0
        spans = []
        for morph in morphemes:
            morph_bytes = morph.encode("utf-8")
            spans.append((cursor, cursor + len(morph_bytes)))
            cursor += len(morph_bytes)
        offsets_per_word.append(spans)

    offsets_str = ' '.join(str(spans) for spans in offsets_per_word)
    if strip_ids or chunk_id is None:
        return offsets_str
    return f"{chunk_id}\t{offsets_str}"


def generate_offsets(output_dir: str, corpus_name: str, strip_ids: bool = False):
    """Read segmented UTF-8 file and write byte-level offset file."""
    seg_utf8_path = os.path.join(output_dir, f"{corpus_name}_segmented_utf8.txt")
    offsets_path = os.path.join(output_dir, f"{corpus_name}_segmented_offsets.txt")

    with open(seg_utf8_path, "r", encoding="utf-8") as fin, \
         open(offsets_path, "w", encoding="utf-8") as fout:
        for line in fin:
            result = compute_offsets(line, strip_ids=strip_ids)
            if result:
                fout.write(result + "\n")

    print(f"  -> {offsets_path}")


# ──────────────────────────────────────────────
# Main Pipeline
# ──────────────────────────────────────────────
def run_pipeline(input_dir: str, output_dir: str, corpus_name: str, strip_ids: bool = False):
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("  ATB Alignment Data Extraction Pipeline")
    if strip_ids:
        print("  (IDs will be stripped from output)")
    print("=" * 60)

    # Step 1: Parse integrated files → source + segmented UTF-8
    print("\n[Step 1/3] Parsing integrated files and transliterating to UTF-8...")
    sentence_data = parse_integrated_files(input_dir)
    write_parsed_output(sentence_data, output_dir, corpus_name, strip_ids=strip_ids)

    # Step 2: Normalize لام التعريف (ل+ال → ل+ل)
    print("\n[Step 2/3] Normalizing لام التعريف (ل+ال → ل+ل)...")
    apply_lam_normalization(output_dir, corpus_name, strip_ids=strip_ids)

    # Step 3: Generate byte-level morpheme offsets
    print("\n[Step 3/3] Generating byte-level morpheme offsets...")
    generate_offsets(output_dir, corpus_name, strip_ids=strip_ids)

    print("\n" + "=" * 60)
    print("  Pipeline complete!")
    print(f"  Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract morpheme-aligned data from ATB/BOLT integrated files."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Path to ATB/BOLT integrated data directory (contains .txt files).",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Path to write output files.",
    )
    parser.add_argument(
        "--corpus_name",
        type=str,
        default="atb3",
        help="Corpus prefix for output filenames (e.g., 'atb3' or 'bolt'). Default: atb3",
    )
    parser.add_argument(
        "--strip_ids",
        action="store_true",
        help="Remove CHUNK IDs from output files (for downstream metrics code).",
    )
    args = parser.parse_args()

    run_pipeline(args.input_dir, args.output_dir, args.corpus_name, strip_ids=args.strip_ids)
