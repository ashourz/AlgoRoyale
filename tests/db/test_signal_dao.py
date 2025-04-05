# tests/db/test_signal_dao.py
import unittest
from unittest.mock import patch, MagicMock
from db.dao.signal_dao import SignalDAO

class Test_TestSignalDAO(unittest.TestCase):

    @patch("db.dao.signal_dao.connect_db")
    def test_get_signals_by_symbol(self, mock_connect_db):
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        signal_dao = SignalDAO()
        mock_cursor.fetchall.return_value = [
            (1, "AAPL", "2023-04-05 09:00:00", "Positive news", 0.85)
        ]

        # Act
        result = signal_dao.get_signals_by_symbol("AAPL")

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "AAPL")  # symbol should be AAPL
        self.assertEqual(result[0][4], 0.85)  # sentiment score should be 0.85

    @patch("db.dao.signal_dao.connect_db")
    def test_insert_signal(self, mock_connect_db):
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        signal_dao = SignalDAO()

        # Act
        signal_dao.insert_signal("AAPL", "2023-04-05 09:00:00", "Positive news", 0.85)

        # Assert
        mock_cursor.execute.assert_called_once_with(
            """
            INSERT INTO trade_signals (symbol, signal, price, created_at)
            VALUES (%s, %s, %s, NOW())
            """,
            ("AAPL", "2023-04-05 09:00:00", "Positive news", 0.85)
        )
        mock_conn.commit.assert_called_once()  # Ensure commit was called

if __name__ == "__main__":
    unittest.main()
