import logging
from matcha_notifier.enums import StockStatus, Brand
from matcha_notifier.stock_data import StockData
from matcha_notifier.enums import StockStatus


logger = logging.getLogger(__name__)

def test_stock_data_update_stock_change_new_brand():
    stock_data = StockData()
    initial_state = {}
    stock_data.load_state = lambda: initial_state
    all_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
        }
    }
    
    instock_items = stock_data.update_stock_changes(all_items)
    
    assert len(instock_items) == 1
    assert len(instock_items[Brand.MARUKYU_KOYAMAEN]) == 1
    assert instock_items == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
        }
    }

def test_stock_data_update_stock_change_brand_exists_new_items():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1385CTH25': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Amazing Matcha Mix',
                'url': 'https://example.com/amazing-matcha-mix',
                'stock_status': 'instock'
            }
        }
    } 
    stock_data.load_state = lambda: initial_state
    all_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'instock'
            }
        }
    }
    
    instock_items = stock_data.update_stock_changes(all_items)
    
    assert len(instock_items) == 1
    assert len(instock_items[Brand.MARUKYU_KOYAMAEN]) == 2
    assert instock_items == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'instock'
            }
        }
    }

def test_stock_data_update_stock_change_item_stock_change():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'outofstock'
            },
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'outofstock'
            },
        }
    } 
    stock_data.load_state = lambda: initial_state
    all_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'outofstock'
            }
        }
    }
    
    instock_items = stock_data.update_stock_changes(all_items)
    
    assert len(instock_items) == 1
    assert len(instock_items[Brand.MARUKYU_KOYAMAEN]) == 1
    assert instock_items == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            }
        }
    }

def test_stock_data_no_stock_changes():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'outofstock'
            }
        }
    }

    stock_data.load_state = lambda: initial_state
    all_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'outofstock'
            }
        }
    }
    
    instock_items = stock_data.update_stock_changes(all_items)
    
    assert instock_items == {}