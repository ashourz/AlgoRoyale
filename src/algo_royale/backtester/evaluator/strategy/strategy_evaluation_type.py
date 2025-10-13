class StrategyEvaluationType:
    """
    Enum representing the type of walk forward evaluation.
    - TEST: Evaluate the test set.
    - OPTIMIZATION: Evaluate the optimization set.
    - BOTH: Evaluate both test and optimization sets.
    """

    TEST = "test"
    OPTIMIZATION = "optimization"
    BOTH = "both"
