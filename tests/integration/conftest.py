# tests/integration/conftest.py

import asyncio

import pytest

from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def application():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    yield application
    await application.async_close()


@pytest.fixture(scope="session", autouse=True)
def environment_setup(application):
    logger = application.repo_container.db_container.logger
    logger.debug("Starting environment setup in test fixture...")
    db_container = application.repo_container.db_container
    db_container.setup_environment()
    yield True
    db_container.teardown_environment()
