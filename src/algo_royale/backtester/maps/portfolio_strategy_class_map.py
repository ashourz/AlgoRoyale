from algo_royale.backtester.strategy.portfolio.equal_risk_contribution_portfolio_strategy import (
    EqualRiskContributionPortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.equal_weight_portfolio_strategy import (
    EqualWeightPortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.inverse_volatility_portfolio_strategy import (
    InverseVolatilityPortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.max_sharpe_portfolio_strategy import (
    MaxSharpePortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.mean_variance_portfolio_strategy import (
    MeanVariancePortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.minimum_variance_portfolio_strategy import (
    MinimumVariancePortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.momentum_portfolio_strategy import (
    MomentumPortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.risk_parity_portfolio_strategy import (
    RiskParityPortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.volatility_weighted_portfolio_strategy import (
    VolatilityWeightedPortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.winner_takes_all_portfolio_strategy import (
    WinnerTakesAllPortfolioStrategy,
)

PORTFOLIO_STRATEGY_CLASS_MAP: dict[str, type] = {
    "EqualRiskContributionPortfolioStrategy": EqualRiskContributionPortfolioStrategy,
    "EqualWeightPortfolioStrategy": EqualWeightPortfolioStrategy,
    "InverseVolatilityPortfolioStrategy": InverseVolatilityPortfolioStrategy,
    "MaxSharpePortfolioStrategy": MaxSharpePortfolioStrategy,
    "MeanVariancePortfolioStrategy": MeanVariancePortfolioStrategy,
    "MinimumVariancePortfolioStrategy": MinimumVariancePortfolioStrategy,
    "MomentumPortfolioStrategy": MomentumPortfolioStrategy,
    "RiskParityPortfolioStrategy": RiskParityPortfolioStrategy,
    "VolatilityWeightedPortfolioStrategy": VolatilityWeightedPortfolioStrategy,
    "WinnerTakesAllPortfolioStrategy": WinnerTakesAllPortfolioStrategy,
}
