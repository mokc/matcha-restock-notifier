import json
import os
from copy import deepcopy
from dataclasses import asdict
from matcha_notifier.enums import StockStatus, Website
from matcha_notifier.models import ItemStock
from pathlib import Path
from typing import Dict, Tuple


class StockData:
    def __init__(self):
        self.state_file = 'state.json'

    def get_stock_changes(
            self,
            all_items: Dict[Website, Dict[str, ItemStock]],
            state: Dict[str, Dict[str, ItemStock]]
    ) -> Tuple[Dict[str, ItemStock], Dict[str, Dict[str, ItemStock]]]:
        """
        Detect item stock changes and returns new/restocked items and the new state.
        """
        all_new_instock_items = {}
        new_state = deepcopy(state) # Create a copy to avoid modifying the original state
        for site, items in all_items.items():
            instock_items = {}

            if site.value not in new_state:    # New site
                new_state[site.value] = {}

            for item, data in items.items():
                if item not in new_state[site.value]:    # New item
                    new_state[site.value][item] = data
                    if data.stock_status == StockStatus.INSTOCK.value:
                        instock_items[item] = data
                elif (
                    new_state[site.value][item].stock_status == StockStatus.OUT_OF_STOCK.value
                    and data.stock_status == StockStatus.INSTOCK.value
                ):
                    # Item was out of stock but instock now
                    new_state[site.value][item].stock_status = StockStatus.INSTOCK.value
                    instock_items[item] = data
                elif (
                    new_state[site.value][item].stock_status == StockStatus.INSTOCK.value
                    and data.stock_status == StockStatus.OUT_OF_STOCK.value
                ):
                    # Item was instock but out of stock now
                    new_state[site.value][item].stock_status = StockStatus.OUT_OF_STOCK.value
                else: 
                    # Item is still in stock
                    pass

            if instock_items:
                all_new_instock_items[site] = deepcopy(instock_items)

        return (all_new_instock_items, new_state)
    
    def load_state(self) -> Dict[str, Dict[str, ItemStock]]:
        """
        Load state file
        """
        if Path(self.state_file).exists():
            with open(self.state_file) as f:
                website_items = json.load(f)
                state = {}
                for website, items in website_items.items():
                    state[website] = {k: ItemStock(**v) for k, v in items.items()}
                return state
        return {}

    def save_state(self, new_state: Dict[str, Dict[str, ItemStock]]) -> None:
        """
        Update state file with product stock changes
        """
        temp_file = self.state_file + '.tmp'
        with open(temp_file, 'w') as f:
            temp_state = {}
            for website, items in new_state.items():
                temp_state[website] = {k: asdict(v) for k, v in items.items()}
            json.dump(temp_state, f, indent=2)

        os.replace(temp_file, self.state_file)  # Atomically replace state file
