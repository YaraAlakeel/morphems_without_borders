# Boundary precision, recall, F1 evaluated on corpus level (micro-averaged corpus-level)
# full words (no boundaries) are treated as 0 — not skipped, not rewarded

import json
import os

from .io_utils import load_file_to_dict


def extract_internal_bounds(spans):
    if not spans or len(spans) <= 1:
        return set()
    return {e for (_, e) in spans[:-1]}


def spans_equal(g_spans, p_spans):
    return g_spans == p_spans


def micro_prf1(TP, FP, FN):
    p = TP / (TP + FP) if (TP + FP) else 0.0
    r = TP / (TP + FN) if (TP + FN) else 0.0
    f = (2 * p * r / (p + r)) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f, 4)


def evaluate(gold_file_path, pred_file_path, output_jsonl=None):
    gold = load_file_to_dict(gold_file_path)
    pred = load_file_to_dict(pred_file_path)

    common_ids = sorted(set(gold) & set(pred))
    missing_in_gold = sorted(set(pred) - set(gold))
    missing_in_pred = sorted(set(gold) - set(pred))

    if missing_in_gold:
        print(f"[!] {len(missing_in_gold)} IDs missing in gold (present only in pred).")
    if missing_in_pred:
        print(f"[!] {len(missing_in_pred)} IDs missing in pred (present only in gold).")

    skipped_sentences = 0
    total_TP = total_FP = total_FN = 0

    for cid in common_ids:
        g_words = gold[cid]
        p_words = pred[cid]

        if len(g_words) != len(p_words):
            skipped_sentences += 1
            continue

        for g_spans, p_spans in zip(g_words, p_words):
            gold_b = extract_internal_bounds(g_spans)
            pred_b = extract_internal_bounds(p_spans)

            if not gold_b and not pred_b:
                continue

            total_TP += len(gold_b & pred_b) # boundaries in both gold and pred
            total_FP += len(pred_b - gold_b) # boundaries in pred but not in gold
            total_FN += len(gold_b - pred_b) # boundaries in gold but not in pred

    precision, recall, f1 = micro_prf1(total_TP, total_FP, total_FN)

    output_data = {
        "predicted_file": os.path.basename(pred_file_path),
        "metrics": {
            "boundary_precision": precision,
            "boundary_recall": recall,
            "boundary_f1": f1,
        },
    }

    if output_jsonl is not None:
        with open(output_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(output_data, ensure_ascii=False) + "\n")
        print(f"[✓] Results written to {output_jsonl} | Skipped sentences: {skipped_sentences}")

    return output_data


def evaluate_multiple(gold_file_path, pred_file_paths, output_jsonl):
    for pred_file in pred_file_paths:
        evaluate(gold_file_path, pred_file, output_jsonl)
