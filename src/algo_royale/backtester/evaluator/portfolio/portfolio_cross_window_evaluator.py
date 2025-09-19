import json
from pathlib import Path

import numpy as np

from algo_royale.logging.loggable import Loggable


class PortfolioCrossWindowEvaluator:
    """
    Aggregates all window-specific optimization results for a given portfolio-strategy and writes evaluation_result.json.
    """

    def __init__(
        self,
        logger: Loggable,
        window_json_filename: str,
        output_filename: str = "evaluation_result.json",
    ):
        self.logger = logger
        self.window_json_filename = window_json_filename
        self.output_filename = output_filename

    def run(
        self,
        strategy_dir: Path,
    ):
        window_results = []
        # First, iterate over window-level directories
        if not strategy_dir.is_dir():
            self.logger.error(f"Strategy directory does not exist: {strategy_dir}")
            return None
        for window_dir in sorted(strategy_dir.iterdir()):
            if not window_dir.is_dir():
                continue
            self.logger.debug(
                f"Processing window directory: {window_dir} | {self.window_json_filename}"
            )
            opt_path = window_dir / self.window_json_filename
            if not opt_path.exists():
                self.logger.warning(f"No optimization result found: {opt_path}")
                continue
            try:
                with open(opt_path) as f:
                    opt_json = json.load(f)
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON in {opt_path}, skipping file.")
                continue
            # Defensive: ensure opt_json is a dict
            if not isinstance(opt_json, dict):
                self.logger.error(
                    f"Optimization result at {opt_path} is not a dict: {type(opt_json)}. Skipping."
                )
                continue
            self.logger.debug(
                f"Loaded optimization results from {opt_path}, found {len(opt_json)} windows."
            )
            # New format: {window_id: {"strategy": ..., "symbols": ..., "optimization": {...}, "window": {...}}}
            for window_id, window_obj in opt_json.items():
                optimization = window_obj.get("optimization")
                if not optimization:
                    self.logger.warning(f"No optimization section in {opt_path}")
                    continue
                metrics = optimization.get("metrics", {})
                params = optimization.get("best_params", {})
                window_params = {
                    k: v for k, v in optimization.items() if k.endswith("_conditions")
                }
                window_result = {
                    "window_id": window_id,
                    "metrics": metrics,
                    "params": params,
                    **window_params,
                }
                window_results.append(window_result)

        if not window_results:
            self.logger.warning(f"No window results found for {strategy_dir}")
            return None
        self.logger.debug(
            f"Aggregated {len(window_results)} window results for {strategy_dir.name}"
        )
        # Aggregate metrics across windows
        metric_keys = set()
        for wr in window_results:
            metric_keys.update(wr.get("metrics", {}).keys())
        summary = {}
        for key in metric_keys:
            vals = [
                wr["metrics"].get(key)
                for wr in window_results
                if key in wr["metrics"] and wr["metrics"].get(key) is not None
            ]
            if vals:
                summary[key] = {
                    "mean": float(np.mean(vals)),
                    "std": float(np.std(vals)),
                    "min": float(np.min(vals)),
                    "max": float(np.max(vals)),
                }

        # Most common best params (simple mode for each param)
        from collections import Counter

        def most_common_param(param_name):
            self.logger.debug(
                f"Finding most common value for param: {param_name} in {len(window_results)} windows"
            )
            all_vals = []
            for wr in window_results:
                val = wr.get("params", {}).get(param_name)
                if val is not None:
                    if isinstance(val, dict):
                        all_vals.append(tuple(sorted(val.items())))
                    else:
                        all_vals.append(val)
            if not all_vals:
                return None
            most_common_val = Counter(all_vals).most_common(1)[0][0]
            # If the most common value is a tuple (from dict), convert back to dict, else return as is
            if isinstance(most_common_val, tuple):
                return dict(most_common_val)
            else:
                return most_common_val

        # For entry/exit/trend_conditions, collect most common
        def most_common_conditions(cond_name):
            all_conds = [
                str(wr.get(cond_name)) for wr in window_results if cond_name in wr
            ]
            if not all_conds:
                return None
            return eval(Counter(all_conds).most_common(1)[0][0])

        param_keys = set()
        for wr in window_results:
            param_keys.update(wr.get("params", {}).keys())
        most_common_best_params = {}
        for pk in param_keys:
            self.logger.debug(
                f"[PK LOOP] Finding most common value for param: {pk} in {len(window_results)} windows"
            )
            val = most_common_param(pk)
            if val is not None:
                most_common_best_params[pk] = val
        for cond in ["entry_conditions", "exit_conditions", "trend_conditions"]:
            val = most_common_conditions(cond)
            if val is not None:
                most_common_best_params[cond] = val

        # Param consistency: fraction of windows with most common params
        self.logger.debug(f"Most common best params: {most_common_best_params}")
        param_consistency = 0.0
        if most_common_best_params:
            count = 0
            for wr in window_results:
                match = True
                for k, v in most_common_best_params.items():
                    if wr.get("params", {}).get(k) != v and wr.get(k) != v:
                        match = False
                        break
                if match:
                    count += 1
            param_consistency = count / len(window_results)

        # Viability score: mean of all window total_returns (or 0 if not present)
        viability_score = summary.get("total_return", {}).get("mean", 0.0)
        self.logger.info(
            f"Viability score for {strategy_dir.name}: {viability_score} (threshold: 0.75)"
        )
        evaluation_result = {
            "summary": summary,
            "n_windows": len(window_results),
            "metric_type": "both",
            "viability_score": viability_score,
            "is_viable": viability_score >= 0.75,
            "most_common_best_params": most_common_best_params,
            "param_consistency": param_consistency,
            "window_params": [
                {k: v for k, v in wr.items() if k != "metrics"} for wr in window_results
            ],
        }
        out_path = strategy_dir / self.output_filename
        with open(out_path, "w") as f:
            json.dump(evaluation_result, f, indent=2)
        self.logger.info(f"Wrote cross-window evaluation to {out_path}")
        return evaluation_result
