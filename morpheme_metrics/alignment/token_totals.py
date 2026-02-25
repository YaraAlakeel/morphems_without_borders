import json
import os

from .io_utils import load_file_to_dict


def evaluate_token_totals(gold_file, pred_file_path, output_jsonl=None):
    gold_dict = load_file_to_dict(gold_file)
    pred_dict = load_file_to_dict(pred_file_path)

    shared_ids = set(gold_dict.keys()) & set(pred_dict.keys())
    missing_in_gold = set(pred_dict.keys()) - set(gold_dict.keys())
    missing_in_pred = set(gold_dict.keys()) - set(pred_dict.keys())

    if missing_in_gold:
        print(f"[!] Missing in gold file: {missing_in_gold}")
    if missing_in_pred:
        print(f"[!] Missing in predicted file: {missing_in_pred}")

    total_words = 0
    total_gold_tokens = 0
    total_pred_tokens = 0

    for chunk_id in sorted(shared_ids):
        gold_words = gold_dict[chunk_id]
        pred_words = pred_dict[chunk_id]

        if len(gold_words) != len(pred_words):
            print(f"[Warning] Word count mismatch: {chunk_id}")
            continue

        for g_word, p_word in zip(gold_words, pred_words):
            total_words += 1
            total_gold_tokens += len(g_word)
            total_pred_tokens += len(p_word)

    result_entry = {
        "predicted_file": os.path.basename(pred_file_path),
        "metrics": {
            "total_sentences": len(shared_ids),
            "total_words": total_words,
            "total ground truth tokens": total_gold_tokens,
            "total predicted tokens": total_pred_tokens,
        },
    }

    if output_jsonl is not None:
        with open(output_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(result_entry, ensure_ascii=False) + "\n")
        print(f"[✓] Results written to {output_jsonl}")

    return result_entry
