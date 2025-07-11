import logging
from matcha_notifier.enums import StockStatus, Brand
from matcha_notifier.stock_data import StockData
from matcha_notifier.enums import StockStatus


logger = logging.getLogger(__name__)

def test_stock_data_update_stock_change_new_brand():
    stock_data = StockData()
    initial_state = {}
    all_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            },
        }
    }
    
    instock_items, new_state = stock_data.get_stock_changes(all_items, initial_state)
    
    assert len(instock_items) == 1
    assert len(instock_items[Brand.MARUKYU_KOYAMAEN]) == 1
    assert instock_items == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            },
        }
    }
    assert len(new_state) == 1
    assert len(new_state[Brand.MARUKYU_KOYAMAEN.value]) == 1
    assert new_state == {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            },
        }
    }

def test_stock_data_update_stock_change_brand_exists_new_items():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1385CTH25': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Amazing Matcha Mix',
                'url': 'https://example.com/amazing-matcha-mix',
                'stock_status': StockStatus.INSTOCK.value
            }
        }
    } 
    all_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': StockStatus.INSTOCK.value
            }
        }
    }
    
    instock_items, new_state = stock_data.get_stock_changes(all_items, initial_state)
    
    assert len(instock_items) == 1
    assert len(instock_items[Brand.MARUKYU_KOYAMAEN]) == 2
    assert instock_items == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': StockStatus.INSTOCK.value
            }
        }
    }
    assert len(new_state) == 1
    assert len(new_state[Brand.MARUKYU_KOYAMAEN.value]) == 3
    assert new_state == {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1385CTH25': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Amazing Matcha Mix',
                'url': 'https://example.com/amazing-matcha-mix',
                'stock_status': StockStatus.INSTOCK.value
            },
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': StockStatus.INSTOCK.value
            }
        }
    }

def test_stock_data_update_stock_change_item_stock_change():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': StockStatus.OUT_OF_STOCK.value
            },
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.OUT_OF_STOCK.value
            },
        }
    } 

    all_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': StockStatus.OUT_OF_STOCK.value
            }
        }
    }
    
    instock_items, new_state = stock_data.get_stock_changes(all_items, initial_state)
    
    assert len(instock_items) == 1
    assert len(instock_items[Brand.MARUKYU_KOYAMAEN]) == 1
    assert instock_items == {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            }
        }
    }
    assert len(new_state) == 1
    assert len(new_state[Brand.MARUKYU_KOYAMAEN.value]) == 2
    assert new_state == {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': StockStatus.OUT_OF_STOCK.value
            }
        }
    }

def test_stock_data_no_new_stock_changes():
    stock_data = StockData()
    initial_state = {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'outofstock'
            }
        }
    }

    all_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'outofstock'
            }
        }
    }
    
    instock_items, new_state = stock_data.get_stock_changes(all_items, initial_state)
    
    assert len(instock_items) == 0
    assert instock_items == {}
    assert len(new_state) == 1
    assert len(new_state[Brand.MARUKYU_KOYAMAEN.value]) == 2
    assert new_state == {
        Brand.MARUKYU_KOYAMAEN.value: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix',
                'url': 'https://example.com/matcha-mix',
                'stock_status': 'outofstock'
            }
        }
    }