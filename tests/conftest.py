import logging
import pytest
from matcha_notifier.stock_data import StockData
from pathlib import Path
from tests.constants import TEST_STATE_FILE


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s',
    )

@pytest.fixture(autouse=True)
def teardown():
    """
    Creates the state file before each test and cleans it up after.
    """
    path = Path(TEST_STATE_FILE)

    # Ensure the file exists and is clean
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{}')

    yield path
    
    if path.exists():
        path.unlink()

@pytest.fixture(autouse=True)
def mock_stock_data_init(monkeypatch):
    """
    Mocks the StockData class's __init__ method to use a test state file.
    This allows tests to run without affecting the actual state file.
    """
    original_init = StockData.__init__
    def mock_init(self):
        original_init(self)
        self.state_file = TEST_STATE_FILE

    monkeypatch.setattr('matcha_notifier.stock_data.StockData.__init__', mock_init)
