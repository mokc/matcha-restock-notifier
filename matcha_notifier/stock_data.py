import json
from matcha_notifier.enums import StockStatus
from pathlib import Path
from typing import Dict


class StockData:
    def __init__(self):
        self.state_file = 'state.json'

    def detect_stock_changes(self, instock_items: Dict) -> Dict:
        """
        Detects when an item goes from out of stock to instock
        """
        changes = {}
        state = self.load_state()
        for brand, items in instock_items.items():
            true_changes = {brand: {}}

            for item, data in items.items():
                if brand.value not in state:    # New brand
                    true_changes[brand][item] = data
                elif item not in state[brand.value]:    # New item
                    true_changes[brand][item] = data
                elif state[brand.value][item] == StockStatus.OUT_OF_STOCK.value:    # Item was out of stock before
                    true_changes[brand][item] = data
                else:
                    pass

            if true_changes[brand]:
                changes[brand] = true_changes[brand].copy()

        if changes:
            self.save_state(state, changes)

        return changes
    
    def load_state(self) -> Dict:
        """
        Load state file
        """
        if Path(self.state_file).exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {}

    def save_state(self, state: Dict, changes: Dict) -> None:
        """
        Update state file with product stock changes
        """
        if not changes:
            return

        # Update stock status for all items in changes
        for brand, items in changes.items():
            if brand.value not in state:      # Brand not in state
                state[brand.value] = {}

            for item, data in items.items():
                state[brand.value][item] = data

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
