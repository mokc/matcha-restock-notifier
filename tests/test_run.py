
import json
import pytest
from matcha_notifier.run import run

    
def test_run():
    result = run()
    
    assert result is True
