# Strict Morpheme Coverage Rate (macro-averaged corpus-level)
# Computes per-word coverage scores, then averages across all words.

import json
import os
from statistics import mean

from .io_utils import load_file_to_dict


def morpheme_coverage_rate(g_spans, p_spans):
    """
    Compute morpheme coverage rate for one word.
    Returns (#correct, #total_gold_morphemes).
    """
    if not g_spans:
        return 0, 0

    gold_bounds = [g_spans[0][0]] + [e for (_, e) in g_spans] # get all gold boundaries (start of first morpheme + ends of all morphemes)
    gold_bound_set = set(gold_bounds)
    pred_bounds = [p_spans[0][0]] + [e for (_, e) in p_spans] #get all pred boundaries (start of first morpheme + ends of all morphemes)
    pred_split_points = set(pred_bounds[1:-1])  # internal predicted cuts

    correct = 0
    total = len(g_spans)

    for (i, j) in g_spans: # for each gold morpheme span
        has_split_inside = any(i < b < j for b in pred_split_points)
        if has_split_inside: # any predicted split point falls inside the gold morpheme span, then it's not fully covered
            continue

        covering = None 
        for (p, q) in p_spans:# find a predicted span that fully contains the gold morpheme span (i, j).
            if p <= i and q >= j:
                covering = (p, q)
                break
        if covering is None:
            continue

        p, q = covering
        if p in gold_bound_set and q in gold_bound_set: # if the predicted span that covers the gold morpheme span also has boundaries that match gold boundaries, then it's correct
            correct += 1

    return correct, total #  return correct covered morphemes and total gold morphemes for this word


def safe_div(a, b):
    return round(a / b, 4) if b else 0.0


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

    per_word_scores = []
    skipped_sentences = 0

    for cid in common_ids:
        g_words = gold[cid]
        p_words = pred[cid]

        if len(g_words) != len(p_words):
            skipped_sentences += 1
            continue

        for g_spans, p_spans in zip(g_words, p_words):
            correct, total = morpheme_coverage_rate(g_spans, p_spans)
            per_word_scores.append(safe_div(correct, total))

    mcr = round(mean(per_word_scores), 4) if per_word_scores else 0.0

    output_data = {
        "predicted_file": os.path.basename(pred_file_path),
        "metrics": {
            "morpheme_coverage_rate": mcr,
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
