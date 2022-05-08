from dataclasses import dataclass
from typing import List
import requests as req
import json
from bs4 import BeautifulSoup as bs
from tqdm import tqdm


@dataclass
class ProductInfo:
    product_url: str
    product_name: str
    price: str
    pack_size: str
    inventory_left: int
    description: str
    all_images_url: List[str]


class Scrapper:
    def __init__(self):
        self._base_url = "https://www.carrefour.ke"
        self._category_beverage_url = self._base_url + "/mafken/en/c/FKEN1500000"
        self._product_info_list = []

    def scrap_product_url(self) -> None:
        category_beverage_url = self._category_beverage_url
        page_src = req.get(category_beverage_url, headers={'User-Agent': 'PostmanRuntime/7.29.0'}).text
        page_soup = bs(page_src, "html.parser")
        page_txt = page_soup.find("script", {"id": "__NEXT_DATA__"}).text
        page_json = json.loads(page_txt)
        for idx in page_json["props"]["initialState"]["search"]["products"]:
            product_url = self._base_url + idx["url"]
            page_src = req.get(product_url, headers={'User-Agent': 'PostmanRuntime/7.29.0'}).text
            detail_product_soup = bs(page_src, "html.parser")
            product_info = self._parse_product_info(detail_product_soup, product_url)
            self._product_info_list.append(product_info)

    @classmethod
    def _parse_product_info(cls, product_soup: bs, product_url: str) -> ProductInfo:
        product_url = product_url
        product_name = cls._get_product_name(product_soup)
        price = cls._get_price(product_soup)
        pack_size = cls._get_pack_size(product_soup)
        inventory_left = cls._get_inventory_left(product_soup)
        description = cls._get_description(product_soup)
        image_urls = cls._get_image_urls(product_soup)

        return ProductInfo(product_url, product_name, price, pack_size, inventory_left, description, image_urls)

    @staticmethod
    def _get_product_name(product_soup: bs) -> str:
        product_txt = product_soup.find("script", {"type": "application/ld+json"}).text
        product_json = json.loads(product_txt)
        return product_json["name"].strip()

    @staticmethod
    def _get_price(product_soup: bs) -> str:
        product_txt = product_soup.find("h2", {"class": "css-17ctnp"}).text.split("(Inc. VAT)")
        return product_txt[0]

    @staticmethod
    def _get_pack_size(product_soup: bs) -> str:
        try:
            product_txt = product_soup.find("div", {"class": "css-1kxxv3q"}).text
            idx = product_txt.index(":")
            pack_size = product_txt[idx + 2:]
            return pack_size
        except AttributeError as e:
            print("Pack size not available")
            return ""

    @staticmethod
    def _get_inventory_left(product_soup: bs) -> int:
        try:
            product_txt = product_soup.find("div", {"class": "css-g4iap9"}).text.split()
            for i in product_txt:
                if i.isdigit():
                    return int(i)
        except AttributeError as e:
            return 0

    @staticmethod
    def _get_description(product_soup: bs) -> str:
        product_txt = product_soup.find("script", {"type": "application/ld+json"}).text
        product_json = json.loads(product_txt)
        return product_json["description"]

    @staticmethod
    def _get_image_urls(product_soup: bs) -> List[str]:
        img_url_list = []
        product_txt = product_soup.findAll("div", {"class": "swiper-wrapper"})
        product_imgs = product_txt[1].findAll("img")
        for idx in product_imgs:
            img_url_list.append(idx.get("data-src").strip())
        return img_url_list
