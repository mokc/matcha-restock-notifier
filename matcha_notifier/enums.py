from enum import Enum


class Brand(Enum):
    IPPODO = 'Ippodo Tea'
    KANBAYASHI = 'Kanbayashi Shunsho'
    MARUKYU_KOYAMAEN = 'Marukyu Koyamaen'
    MARUYASU = 'Maruyasu'
    NAKAMURA_TOKICHI = 'Nakamura Tokichi'
    OSADA_TEA = 'Osada Tea'
    YAMAMASA_KOYAMAEN ='Yamamasa Koyamaen'
    UNKNOWN = 'Unknown'

class StockStatus(Enum):
    INSTOCK = 'instock'
    OUT_OF_STOCK = 'outofstock'

class Website(Enum):
    MARUKYU_KOYAMAEN = 'Marukyu Koyamaen'
    NAKAMURA_TOKICHI = 'Nakamura Tokichi'
    STEEPING_ROOM = 'Steeping Room'

