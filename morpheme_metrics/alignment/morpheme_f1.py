# Morpheme F1 (macro-averaged corpus-level)
# Computes per-word coverage scores, then averages across all words.

import json
import os
from collections import Counter
from statistics import mean

from .io_utils import load_file_to_dict


def spans_equal(g_spans, p_spans):
    return g_spans == p_spans


def morpheme_span_prf1(g_spans, p_spans):
    """
    Precision/Recall/F1 using full spans (start,end).
    """
    gold_counter = Counter(g_spans)
    pred_counter = Counter(p_spans)

    TP = 0
    for span, gcount in gold_counter.items():
        pcount = pred_counter.get(span, 0)
        TP += min(gcount, pcount)

    FP = sum(pred_counter.values()) - TP
    FN = sum(gold_counter.values()) - TP

    precision = TP / (TP + FP) if (TP + FP) else 0.0
    recall = TP / (TP + FN) if (TP + FN) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return precision, recall, f1


def evaluate(gold_file_path, pred_file_path, output_jsonl=None):
    gold = load_file_to_dict(gold_file_path)
    pred = load_file_to_dict(pred_file_path)

    common_ids = sorted(set(gold) & set(pred))
    missing_in_gold = sorted(set(pred) - set(gold))
    missing_in_pred = sorted(set(gold) - set(pred))

    if missing_in_gold:
        print(f"[!] Missing in gold file: {missing_in_gold}")
    if missing_in_pred:
        print(f"[!] Missing in predicted file: {missing_in_pred}")

    all_p, all_r, all_f1 = [], [], []
    skipped_sentences = 0

    for cid in common_ids:
        g_words = gold[cid]
        p_words = pred[cid]

        if len(g_words) != len(p_words):
            skipped_sentences += 1
            print(f"[Warn] Word count mismatch in {cid}: gold={len(g_words)} pred={len(p_words)}")
            continue

        for g_spans, p_spans in zip(g_words, p_words):
            p, r, f1 = morpheme_span_prf1(g_spans, p_spans)
            all_p.append(p)
            all_r.append(r)
            all_f1.append(f1)

    def avg(x):
        return round(mean(x), 4) if x else 0.0

    output_data = {
        "predicted_file": os.path.basename(pred_file_path),
        "metrics": {
            "morpheme_precision": avg(all_p),
            "morpheme_recall": avg(all_r),
            "morpheme_f1": avg(all_f1),
        },
    }

    if output_jsonl is not None:
        with open(output_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(output_data, ensure_ascii=False) + "\n")
        print(f"[✓] Results written to {output_jsonl} | Skipped sentences: {skipped_sentences}")

    return output_data
