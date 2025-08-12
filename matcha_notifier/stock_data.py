import aiofiles
import json
import os
from copy import deepcopy
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
            state: Dict[Website, Dict[str, ItemStock]]
    ) -> Tuple[Dict[Website, ItemStock], Dict[Website, Dict[str, ItemStock]]]:
        """
        Detect item stock changes and returns new/restocked items and the new state.
        """
        all_new_instock_items = {}
        new_state = deepcopy(state) # Create a copy to avoid modifying the original state
        for site, items in all_items.items():
            instock_items = {}

            if site not in new_state:    # New site
                new_state[site] = {}

            for item, data in items.items():
                if item not in new_state[site]:    # New item
                    new_state[site][item] = data
                    if data.stock_status == StockStatus.INSTOCK:
                        instock_items[item] = data
                elif (
                    new_state[site][item].stock_status == StockStatus.OUT_OF_STOCK
                    and data.stock_status == StockStatus.INSTOCK
                ):
                    # Item was out of stock but instock now
                    new_state[site][item].stock_status = StockStatus.INSTOCK
                    instock_items[item] = data
                elif (
                    new_state[site][item].stock_status == StockStatus.INSTOCK
                    and data.stock_status == StockStatus.OUT_OF_STOCK
                ):
                    # Item was instock but out of stock now
                    new_state[site][item].stock_status = StockStatus.OUT_OF_STOCK
                else: 
                    # Item is still in stock
                    pass

            if instock_items:
                all_new_instock_items[site] = deepcopy (instock_items)

        return (all_new_instock_items, new_state)
    
    async def load_state(self) -> Dict[str, Dict[str, ItemStock]]:
        """
        Load state file
        """
        if Path(self.state_file).exists():
            async with aiofiles.open(self.state_file, mode='r') as f:
                content = await f.read()
                website_items = json.loads(content)

            # Convert website_items to data models when applicable
            state = {}
            for website, items in website_items.items():
                state[Website(website)] = {}
                for item_id, data in items.items():
                    state[Website(website)][item_id] = ItemStock.from_dict(data)
            return state
        return {}

    async def save_state(self, new_state: Dict[Website, Dict[str, ItemStock]]) -> None:
        """
        Update state file with product stock changes
        """
        temp_state = {}
        for website, items in new_state.items():
            temp_state[website.value] = {k: v.to_dict() for k, v in items.items()}

        text = json.dumps(temp_state, indent=2)
        
        # Write to a temporary file first to avoid data loss
        temp_file = self.state_file + '.tmp'
        async with aiofiles.open(temp_file, mode='w') as f:
            await f.write(text)

        os.replace(temp_file, self.state_file)  # Atomically replace state file

    def get_website_instock_items(
        self, website: Website, state: Dict[Website, Dict[str, ItemStock]]
    ) -> Dict[str, ItemStock]:
        """
        Get all in-stock items for a specific website.
        """
        instock_items = {website: {}}
        if website in state:
            for k, v in state[website].items():
                if v.stock_status == StockStatus.INSTOCK:
                    instock_items[website][k] = v
        
        if instock_items[website]:
            return instock_items

        return {}
    
    async def get_all_instock_items(self) -> Dict[Website, Dict[str, ItemStock]]:
        """
        Get all in-stock items across all websites.
        """
        state = await self.load_state()
        all_instock_items = {}
        for website in state:
            instock_items = self.get_website_instock_items(website, state)
            if instock_items:
                all_instock_items.update(instock_items)
        return all_instock_items
