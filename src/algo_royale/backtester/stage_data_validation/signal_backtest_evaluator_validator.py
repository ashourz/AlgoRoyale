# Define the validation function outside the Enum
def signal_backtest_evaluator_validator(d) -> bool:
    """Validate the structure of a backtest stage dictionary for signal backtest evaluation."""
    return (
        isinstance(d, dict)
        and "total_return" in d
        and "sharpe_ratio" in d
        and "win_rate" in d
        and "max_drawdown" in d
        and isinstance(d["total_return"], float)
        and isinstance(d["sharpe_ratio"], float)
        and isinstance(d["win_rate"], float)
        and isinstance(d["max_drawdown"], float)
    )
