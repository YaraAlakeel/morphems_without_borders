import argparse
import json
import os
import sys


METRICS = ("token_totals", "fertility", "morpheme_f1", "boundary_f1", "coverage_rate") 
CHOICES = ("all",) + METRICS


def _selected_metrics(metrics_list: list[str]) -> tuple[str, ...]:# helper function to determine which metrics to compute based on user input. If the user selects "all" or provides an empty list, it returns all available metrics; otherwise, it returns only the specified metrics.
    if not metrics_list or "all" in metrics_list:
        return METRICS
    return tuple(metrics_list)


def evaluate_one(gold_path: str, pred_path: str, metrics: tuple[str, ...]) -> dict: # will call the relevant evaluation functions based on the selected metrics and aggregate results into a single record
    record = {
        "predicted_file": os.path.basename(pred_path),
        "metrics": {},
    }

    if "token_totals" in metrics:
        from morpheme_metrics.alignment.token_totals import evaluate_token_totals

        data = evaluate_token_totals(gold_path, pred_path, output_jsonl=None)
        record["metrics"].update((data.get("metrics", {})))

    if "fertility" in metrics:
        from morpheme_metrics.alignment.fertility import fertility

        data = fertility(gold_path, pred_path, output_jsonl=None)
        record["metrics"].update((data.get("metrics", {})))

    if "morpheme_f1" in metrics:
        from morpheme_metrics.alignment.morpheme_f1 import evaluate as eval_morpheme_f1

        data = eval_morpheme_f1(gold_path, pred_path, output_jsonl=None)
        record["metrics"].update((data.get("metrics", {})))

    if "boundary_f1" in metrics:
        from morpheme_metrics.alignment.morpheme_boundary_f1 import evaluate as eval_boundary_f1

        data = eval_boundary_f1(gold_path, pred_path, output_jsonl=None)
        record["metrics"].update((data.get("metrics", {})))

    if "coverage_rate" in metrics:
        from morpheme_metrics.alignment.morpheme_coverage_rate import evaluate as eval_morpheme_coverage_rate

        data = eval_morpheme_coverage_rate(gold_path, pred_path, output_jsonl=None)
        record["metrics"].update((data.get("metrics", {})))

    return record


def build_parser() -> argparse.ArgumentParser: # sets up the command-line interface for the evaluation script, allowing users to specify gold and predicted files, select which metrics to compute, and choose output options.
    p = argparse.ArgumentParser(prog="morpheme-eval")
    p.add_argument("--gold", required=True, help="Gold spans file")
    p.add_argument("--pred", required=True, nargs="+", help="One or more predicted spans files")
    p.add_argument(
        "--metrics",
        nargs="+",
        choices=CHOICES,
        default=["all"],
        help="Which metrics to compute (default: all)",
    )
    p.add_argument("--output", action="append", help="Write JSONL to this path (default: stdout)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    metrics = _selected_metrics(args.metrics)

    records = [evaluate_one(args.gold, pred_path, metrics) for pred_path in args.pred]

    if args.output:
        for output_path in args.output:
            with open(output_path, "a", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return 0

    for r in records:
        sys.stdout.write(json.dumps(r, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
