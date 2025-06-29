import logging
import pytest
from matcha_notifier.run import run


logger = logging.getLogger(__name__)

class MockResponse:
    def __init__(self, text):
        self.text = text
        self.is_redirect = False
        self.raise_for_status = lambda: None
        self.status_code = 200

@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()

@pytest.mark.asyncio
async def test_run(monkeypatch, mock_session, mock_response, mk_request):
    mock_response.content = mk_request
    mock_session.get = lambda *args: mock_response
    monkeypatch.setattr('matcha_notifier.scraper.ClientSession', mock_session)

    result = await run()
    
    assert result is True
