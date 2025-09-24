import pytest

## Removed unused import
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


@pytest.fixture
def repo():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    # Ensure the database and tables exist
    db_container = application.repo_container.db_container
    db_container.register_user()
    application.repo_container.db_container.db_connection(create_if_not_exists=True)
    repo = application.repo_container.watchlist_repo
    yield repo
    # Cleanup logic if needed
    db_container.close()


def test_watchlist_repo_methods(repo):
    # Save
    repo.save_watchlist(["AAPL", "SNDL"])
    # Load
    symbols = repo.load_watchlist()
    assert "AAPL" in symbols and "SNDL" in symbols
    # Save empty should raise
    with pytest.raises(ValueError):
        repo.save_watchlist([])
