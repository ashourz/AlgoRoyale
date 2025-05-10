# tests/db/dao/test_base_dao.py
from unittest import TestCase
from unittest.mock import MagicMock, patch
from algo_royale.live_trading.db.dao.base_dao import BaseDAO

class TestBaseDAO(TestCase):

    def setUp(self):
        """Set up the mock connection and BaseDAO instance for testing."""
        self.mock_conn = MagicMock()  # Mock the DB connection
        self.dao = BaseDAO(self.mock_conn)  # Instantiate BaseDAO with the mock connection

    @patch("builtins.open", create=True)
    @patch("os.path.join")
    def test_fetch(self, mock_join, mock_open):
        """Test the fetch operation (SELECT)"""
        
        # Mock the behavior of os.path.join to return a path to the SQL file
        mock_join.return_value = "fake_path.sql"
        # Mock the reading of the SQL file to simulate an actual SQL SELECT query
        mock_open.return_value.__enter__.return_value.read.return_value = "SELECT * FROM signals WHERE symbol = %s"

        # Mock cursor and result for fetchall
        mock_cursor = self.mock_conn.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = [("AAPL",)]

        # Run the fetch method
        result = self.dao.fetch("get_signals_by_symbol.sql", ("AAPL",), log_name="test_fetch")

        # Assertions to verify behavior
        self.assertEqual(result, [("AAPL",)])  # Verify that the result matches the mock data
        # Check that the cursor's execute method was called with the correct SQL and parameters
        mock_cursor.execute.assert_called_once_with("SELECT * FROM signals WHERE symbol = %s", ("AAPL",))
        # Verify that no commit was called (since fetch doesn't modify the database)
        self.mock_conn.commit.assert_not_called()

    @patch("builtins.open", create=True)
    @patch("os.path.join")
    def test_insert(self, mock_join, mock_open):
        """Test the insert operation (INSERT INTO)"""
        
        # Mock the behavior of os.path.join to return a path to the SQL file
        mock_join.return_value = "fake_insert.sql"
        # Mock the reading of the SQL file to simulate an actual SQL INSERT query
        mock_open.return_value.__enter__.return_value.read.return_value = "INSERT INTO signals (symbol, signal, price, created_at) VALUES (%s, %s, %s, %s)"

        # Mock cursor for insert
        mock_cursor = self.mock_conn.cursor.return_value.__enter__.return_value

        # Run the insert method
        self.dao.insert("insert_signal.sql", ("AAPL", "Positive news", 0.85, "2023-04-05 09:00:00"), log_name="test_insert")

        # Assertions to verify behavior
        # Check that the cursor's execute method was called with the correct SQL and parameters
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO signals (symbol, signal, price, created_at) VALUES (%s, %s, %s, %s)",
            ("AAPL", "Positive news", 0.85, "2023-04-05 09:00:00")
        )
        # Verify that the connection's commit method was called (since insert modifies the database)
        self.mock_conn.commit.assert_called_once()

    @patch("builtins.open", create=True)
    @patch("os.path.join")
    def test_update(self, mock_join, mock_open):
        """Test the update operation (UPDATE)"""
        
        # Mock the behavior of os.path.join to return a path to the SQL file
        mock_join.return_value = "fake_update.sql"
        # Mock the reading of the SQL file to simulate an actual SQL UPDATE query
        mock_open.return_value.__enter__.return_value.read.return_value = "UPDATE signals SET signal = %s WHERE symbol = %s"

        # Mock cursor for update
        mock_cursor = self.mock_conn.cursor.return_value.__enter__.return_value

        # Run the update method
        self.dao.update("update_signal.sql", ("New signal", "AAPL"), log_name="test_update")

        # Assertions to verify behavior
        # Check that the cursor's execute method was called with the correct SQL and parameters
        mock_cursor.execute.assert_called_once_with(
            "UPDATE signals SET signal = %s WHERE symbol = %s", 
            ("New signal", "AAPL")
        )
        # Verify that the connection's commit method was called (since update modifies the database)
        self.mock_conn.commit.assert_called_once()

    @patch("builtins.open", create=True)
    @patch("os.path.join")
    def test_delete(self, mock_join, mock_open):
        """Test the delete operation (DELETE)"""
        
        # Mock the behavior of os.path.join to return a path to the SQL file
        mock_join.return_value = "fake_delete.sql"
        # Mock the reading of the SQL file to simulate an actual SQL DELETE query
        mock_open.return_value.__enter__.return_value.read.return_value = "DELETE FROM signals WHERE symbol = %s"

        # Mock cursor for delete
        mock_cursor = self.mock_conn.cursor.return_value.__enter__.return_value

        # Run the delete method
        self.dao.delete("delete_signal.sql", ("AAPL",), log_name="test_delete")

        # Assertions to verify behavior
        # Check that the cursor's execute method was called with the correct SQL and parameters
        mock_cursor.execute.assert_called_once_with("DELETE FROM signals WHERE symbol = %s", ("AAPL",))
        # Verify that the connection's commit method was called (since delete modifies the database)
        self.mock_conn.commit.assert_called_once()

    def test_error_handling(self):
        """Test that errors in SQL execution are handled properly."""
        
        # Test error in fetching (fetch method should raise an exception)
        with self.assertRaises(Exception):
            self.dao.fetch("invalid_query.sql", ("AAPL",), log_name="test_error_fetch")

        # Test error in inserting (insert method should raise an exception)
        with self.assertRaises(Exception):
            self.dao.insert("invalid_insert.sql", ("AAPL", "Positive news", 0.85, "2023-04-05 09:00:00"), log_name="test_error_insert")

        # Test error in updating (update method should raise an exception)
        with self.assertRaises(Exception):
            self.dao.update("invalid_update.sql", ("New signal", "AAPL"), log_name="test_error_update")

        # Test error in deleting (delete method should raise an exception)
        with self.assertRaises(Exception):
            self.dao.delete("invalid_delete.sql", ("AAPL",), log_name="test_error_delete")
