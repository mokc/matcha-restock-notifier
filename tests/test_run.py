
import json
import pytest
from run import run

    
def test_run():
    result = run()
    
    assert result is True
