import pytest

## Removed unused import
from algo_royale.di.application_container import ApplicationContainer


@pytest.fixture
def repo(environment_setup: bool, application: ApplicationContainer):
    logger = application.repo_container.db_container.logger
    logger.debug(f"Environment setup status: {environment_setup}")
    if not environment_setup:
        pytest.skip("Environment setup failed, skipping tests.")
    repo = application.repo_container.watchlist_repo
    yield repo


def test_watchlist_repo_methods(repo):
    # Save
    repo.save_watchlist(["AAPL", "SNDL"])
    # Load
    symbols = repo.load_watchlist()
    assert "AAPL" in symbols and "SNDL" in symbols
    # Save empty should raise
    with pytest.raises(ValueError):
        repo.save_watchlist([])
