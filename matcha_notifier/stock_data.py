import json
import os
from matcha_notifier.enums import StockStatus
from pathlib import Path
from typing import Dict


class StockData:
    def __init__(self):
        self.state_file = 'state.json'

    def update_stock_changes(self, all_items: Dict) -> Dict:
        """
        Detects when an item goes from out of stock to instock
        """
        state = self.load_state()

        all_instock_items = {}
        new_state = state.copy()  # Create a copy to avoid modifying the original state
        for brand, items in all_items.items():
            instock_items = {brand: {}}

            if brand.value not in new_state:    # New brand
                new_state[brand.value] = {}

            for item, data in items.items():
                if item not in new_state[brand.value]:    # New item
                    new_state[brand.value][item] = data
                    if data['stock_status'] == StockStatus.INSTOCK.value:
                        instock_items[brand][item] = data
                elif (
                    new_state[brand.value][item]['stock_status'] == StockStatus.OUT_OF_STOCK.value
                    and data['stock_status'] == StockStatus.INSTOCK.value
                ):  # Item was out of stock but instock now
                    new_state[brand.value][item]['stock_status'] = StockStatus.INSTOCK.value
                    instock_items[brand][item] = data
                else: # Item was instock but out of stock now
                    new_state[brand.value][item]['stock_status'] = StockStatus.OUT_OF_STOCK.value

            if instock_items[brand]:
                all_instock_items[brand] = instock_items[brand].copy()

        if new_state != state:
            self.save_state(new_state)

        return all_instock_items
    
    def load_state(self) -> Dict:
        """
        Load state file
        """
        if Path(self.state_file).exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {}

    def save_state(self, new_state: Dict) -> None:
        """
        Update state file with product stock changes
        """
        temp_file = self.state_file + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(new_state, f, indent=2)

        os.replace(temp_file, self.state_file)  # Atomically replace state file
