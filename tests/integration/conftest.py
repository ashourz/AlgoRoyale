# tests/integration/conftest.py

import pytest

from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


@pytest.fixture(scope="session")
def application():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    yield application
    application.close()


@pytest.fixture(scope="session", autouse=True)
def environment_setup(application):
    logger = application.repo_container.db_container.logger
    logger.debug("Starting environment setup in test fixture...")
    db_container = application.repo_container.db_container
    db_container.setup_environment()
    yield True
    db_container.teardown_environment()
