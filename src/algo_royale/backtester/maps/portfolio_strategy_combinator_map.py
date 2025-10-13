from algo_royale.backtester.strategy_combinator.portfolio.equal_risk_contribution_portfolio_strategy_combinator import (
    EqualRiskContributionPortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.equal_weight_portfolio_strategy_combinator import (
    EqualWeightPortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.inverse_volatility_portfolio_strategy_combinator import (
    InverseVolatilityPortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.max_sharpe_portfolio_strategy_combinator import (
    MaxSharpePortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.mean_variance_portfolio_strategy_combinator import (
    MeanVariancePortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.minimum_variance_portfolio_strategy_combinator import (
    MinimumVariancePortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.momentum_portfolio_strategy_combinator import (
    MomentumPortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.risk_parity_portfolio_strategy_combinator import (
    RiskParityPortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.volatility_weighted_portfolio_strategy_combinator import (
    VolatilityWeightedPortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.portfolio.winner_takes_all_portfolio_strategy_combinator import (
    WinnerTakesAllPortfolioStrategyCombinator,
)

PORTFOLIO_STRATEGY_COMBINATOR_MAP = {
    "EqualRiskContributionPortfolioStrategyCombinator": EqualRiskContributionPortfolioStrategyCombinator,
    "EqualWeightPortfolioStrategyCombinator": EqualWeightPortfolioStrategyCombinator,
    "InverseVolatilityPortfolioStrategyCombinator": InverseVolatilityPortfolioStrategyCombinator,
    "MaxSharpePortfolioStrategyCombinator": MaxSharpePortfolioStrategyCombinator,
    "MeanVariancePortfolioStrategyCombinator": MeanVariancePortfolioStrategyCombinator,
    "MinimumVariancePortfolioStrategyCombinator": MinimumVariancePortfolioStrategyCombinator,
    "MomentumPortfolioStrategyCombinator": MomentumPortfolioStrategyCombinator,
    "RiskParityPortfolioStrategyCombinator": RiskParityPortfolioStrategyCombinator,
    "VolatilityWeightedPortfolioStrategyCombinator": VolatilityWeightedPortfolioStrategyCombinator,
    "WinnerTakesAllPortfolioStrategyCombinator": WinnerTakesAllPortfolioStrategyCombinator,
}
