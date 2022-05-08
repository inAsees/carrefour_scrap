from dataclasses import dataclass
import requests as req
import json
from bs4 import BeautifulSoup as bs


@dataclass
class ProductInfo:
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
        self._category_beverage_url = self._base_url + "/mafken/en/c/FKEN1500000"
        self._product_info_list = []

    def scrap_product_url(self, base_url: str) -> None:
        category_beverage_url = self._category_beverage_url
        page_src = req.get(category_beverage_url).text
        page_soup = bs(page_src, "html.parser")
        page_txt = page_soup.find("script", {"id": "__NEXT_DATA__"}).text
        page_json = json.loads(page_txt)
        for idx in page_json["props"]["initialState"]["search"]["products"]:
            product_url = base_url + idx["url"]
            product_info = self._parse_product_info(product_url)
            self._product_info_list.append(product_info)

    def _parse_product_info(self, product_url: str) -> ProductInfo:
        product_url = product_url
        product_name =

    def _get_product_name(self, ):
        pass



