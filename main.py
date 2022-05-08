from dataclasses import dataclass


@dataclass
class BeverageInfo:
    product_url: str
    product_name: str
    price: str
    pack_size: str
    inventory_left: int
    description: str
    brand: str
    all_images_url: str


class Scrapper:
    def __init__(self):
        pass
