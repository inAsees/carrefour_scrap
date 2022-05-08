from dataclasses import dataclass
from typing import List
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
    all_images_url: List[str]


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
            page_src = req.get(product_url).text
            product_soup = bs(page_src, "html.parser")
            product_info = self._parse_product_info(product_soup, product_url)
            self._product_info_list.append(product_info)

    @classmethod
    def _parse_product_info(cls, product_soup: bs, product_url: str) -> ProductInfo:
        product_url = product_url
        product_name = cls._get_product_name(product_soup)
        price = cls._get_price(product_soup)

    @staticmethod
    def _get_product_name(product_soup: bs) -> str:
        product_txt = product_soup.find("script", {"type": "application/ld+json"}).text
        product_json = json.loads(product_txt)
        return product_json["name"].strip()

    @staticmethod
    def _get_price(product_soup: bs) -> str:
        product_txt = product_soup.find("h2", {"class": "css-17ctnp"}).text
        return " ".join(product_txt.split()[:2])

    @staticmethod
    def _get_pack_size(product_soup: bs) -> str:
        product_txt = product_soup.find("div", {"class": "css-1kxxv3q"}).text
        idx = product_txt.index(":")
        pack_size = product_txt[idx + 2:]
        return pack_size
