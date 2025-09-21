from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


class TestAlpacaCorporateActionClientIntegration:
    @classmethod
    def setup_class(cls):
        # Use the integration environment for real endpoint testing
        cls.container = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
        cls.client = (
            cls.container.adapter_container()
            .client_container()
            .alpaca_corporate_action_client()
        )

    def test_get_corporate_actions(self):
        # Replace with a real method and parameters for your client
        # For example, get corporate actions for a known symbol/date
        response = self.client.get_corporate_actions(symbol="AAPL")
        assert response is not None
        assert isinstance(response, list)
        # Optionally, check for expected keys/fields in the response
        if response:
            assert "corporate_action_id" in response[0]
