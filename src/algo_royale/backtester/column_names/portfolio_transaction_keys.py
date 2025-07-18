class PortfolioTransactionKeys:
    """Keys used in each transaction dictionary in the portfolio execution output."""

    TRADE_ID = "trade_id"
    TIMESTAMP = "timestamp"
    STEP = "step"
    ASSET = "asset"
    ACTION = "action"
    QUANTITY = "quantity"
    PRICE = "price"
    COST = "cost"  # For buys
    PROCEEDS = "proceeds"  # For sells
    CASH_AFTER = "cash_after"
    HOLDINGS_AFTER = "holdings_after"
