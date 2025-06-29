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

@pytest.fixture
def mock_response():
    """
    Mocks the response from an HTTP request to prevent actual network calls during tests.
    """
    class MockResponse:
        def __init__(self, content='', status=200, history=[]):
            self.content = content
            self.status = status
            self.history = history
            self.raise_for_status = lambda: None

        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def text(self):
            return self.content

    return MockResponse()

@pytest.fixture
def mock_session(mock_response):
    """
    Mocks the session to prevent actual HTTP requests during tests.
    """
    class MockSession:
        def __init__(self):
            pass
            
        async def __aenter__(self):
            return self
    
        async def __aexit__(self, exc_type, exc, tb):
            pass

        def get(self, url):
            return ''

    return MockSession