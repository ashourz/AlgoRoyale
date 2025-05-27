import pytest

from algo_royale.backtester.watchlist.watchlist import load_watchlist, save_watchlist


def test_load_watchlist_reads_symbols(tmp_path):
    # Create a temporary watchlist file
    watchlist_path = tmp_path / "watchlist.txt"
    symbols = ["AAPL", "GOOG", "MSFT"]
    watchlist_path.write_text("\n".join(symbols) + "\n")
    result = load_watchlist(str(watchlist_path))
    assert result == symbols


def test_load_watchlist_ignores_blank_lines(tmp_path):
    watchlist_path = tmp_path / "watchlist.txt"
    watchlist_path.write_text("AAPL\n\nGOOG\n\n")
    result = load_watchlist(str(watchlist_path))
    assert result == ["AAPL", "GOOG"]


def test_load_watchlist_file_not_found(tmp_path):
    watchlist_path = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        load_watchlist(str(watchlist_path))


def test_save_watchlist_writes_symbols(tmp_path):
    watchlist_path = tmp_path / "watchlist.txt"
    symbols = ["AAPL", "GOOG", "MSFT"]
    save_watchlist(str(watchlist_path), symbols)
    # Read back and check
    with open(watchlist_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    assert lines == symbols


def test_save_and_load_roundtrip(tmp_path):
    watchlist_path = tmp_path / "watchlist.txt"
    symbols = ["AAPL", "GOOG", "MSFT"]
    save_watchlist(str(watchlist_path), symbols)
    loaded = load_watchlist(str(watchlist_path))
    assert loaded == symbols
