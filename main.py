from dataclasses import dataclass
import requests as req
import json
from bs4 import BeautifulSoup as bs


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
        self._base_url = "https://www.carrefour.ke"
        self._category_beverages_url = self._base_url + "/mafken/en/c/FKEN1500000"

    def get_beverage_url(self, base_url: str):
        with open("base_url.html", "r", encoding="UTF-8") as f:
            page_soup = bs(f, "html.parser")
        page_txt = page_soup.find("script", {"id": "__NEXT_DATA__"}).text
        page_json = json.loads(page_txt)
        for url in page_json["props"]["initialState"]["search"]["products"]:
            beverage_url = base_url + url["url"]
            pass


if __name__ == "__main__":
    pass
