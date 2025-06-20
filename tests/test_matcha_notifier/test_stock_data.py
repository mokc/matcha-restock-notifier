import pytest
from matcha_notifier.enums import StockStatus, Brand
from matcha_notifier.stock_data import StockData
from matcha_notifier.enums import StockStatus


def test_stock_data_detect_stock_change_new_brand():
    stock_data = StockData()
    initial_state = {}
    stock_data.load_state = lambda: initial_state
    # New instock items
    instock_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {'name': 'Hojicha Mix', 'url': 'https://example.com/hojicha-mix'},
        }
    }
    
    changes = stock_data.detect_stock_changes(instock_items)
    
    assert changes == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {'name': 'Hojicha Mix', 'url': 'https://example.com/hojicha-mix'},
        }
    }

def test_stock_data_detect_stock_change_brand_exists_new_items():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1385CTH25': {'name': 'Amazing Matcha Mix', 'url': StockStatus.INSTOCK.value}
        }
    } 
    stock_data.load_state = lambda: initial_state
    # New instock items
    instock_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {'name': 'Hojicha Mix', 'url': 'https://example.com/hojicha-mix'},
            '1G9D000CC-1GAD200C6': {'name': 'Matcha Mix', 'url': 'https://example.com/matcha-mix'}
        }
    }
    
    changes = stock_data.detect_stock_changes(instock_items)
    
    assert changes == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {'name': 'Hojicha Mix', 'url': 'https://example.com/hojicha-mix'},
            '1G9D000CC-1GAD200C6': {'name': 'Matcha Mix', 'url': 'https://example.com/matcha-mix'}
        }
    }

def test_stock_data_detect_stock_change_item_stock_change():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G9D000CC-1GAD200C6': StockStatus.OUT_OF_STOCK.value,
            '1G28200C6': StockStatus.OUT_OF_STOCK.value,
        }
    } 
    stock_data.load_state = lambda: initial_state
    # New instock items
    instock_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {'name': 'Hojicha Mix', 'url': 'https://example.com/hojicha-mix'},
            '1G9D000CC-1GAD200C6': {'name': 'Matcha Mix', 'url': 'https://example.com/matcha-mix'}
        }
    }
    
    changes = stock_data.detect_stock_changes(instock_items)
    
    assert changes == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {'name': 'Hojicha Mix', 'url': 'https://example.com/hojicha-mix'},
            '1G9D000CC-1GAD200C6': {'name': 'Matcha Mix', 'url': 'https://example.com/matcha-mix'}
        }
    }

def test_stock_data_no_stock_changes():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G28200C6': StockStatus.INSTOCK.value,
            '1G9D000CC-1GAD200C6': StockStatus.INSTOCK.value
        }
    }

    stock_data.load_state = lambda: initial_state
    
    # Instock items
    instock_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {'name': 'Hojicha Mix', 'url': 'https://example.com/hojicha-mix'},
            '1G9D000CC-1GAD200C6': {'name': 'Matcha Mix', 'url': 'https://example.com/matcha-mix'}
        }
    }
    
    changes = stock_data.detect_stock_changes(instock_items)
    
    assert changes == {}