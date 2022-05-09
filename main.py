from dataclasses import dataclass
from typing import List
import requests as req
import json
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
import csv


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
        self._page_0_url = "https://www.carrefour.ke/api/v7/categories/FKEN1500000?filter=&sortBy=relevance&" \
                           "currentPage=1&pageSize=60&maxPrice=&minPrice=&areaCode=Westlands%20-%20Nairobi&lang=" \
                           "en&displayCurr=KES&latitude=-1.2672236834605626&longitude=36.810586556760555&" \
                           "responseWithCatTree=true&depth=3"
        self._headers = {'appid': 'Reactweb',
                         'storeid': 'mafken',
                         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                       'Chrome/101.0.4951.54 Safari/537.36'
                         }
        _total_pages = self._get_total_pages()
        self._page_urls = ["https://www.carrefour.ke/api/v7/categories/FKEN1500000?filter=&sortBy=relevance&" \
                           "currentPage={}&pageSize=60&maxPrice=&minPrice=&areaCode=Westlands%20-%20Nairobi&lang=" \
                           "en&displayCurr=KES&latitude=-1.2672236834605626&longitude=36.810586556760555&" \
                           "responseWithCatTree=true&depth=3".format(page) for page in range(_total_pages + 1)]

        self._product_info_list = []  # type: List[ProductInfo]

    def scrap_all_pages(self) -> None:
        for url in self._page_urls:
            print(url)

    def dump(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["product_url", "product_name", "price", "pack_size",
                                                   "inventory_left", "description", "all_images_url"])
            writer.writeheader()
            for ele in tqdm(self._product_info_list, desc="Dumping..."):
                writer.writerow(
                    {"product_url": ele.product_url,
                     "product_name": ele.product_name,
                     "price": ele.price,
                     "pack_size": ele.pack_size,
                     "inventory_left": ele.inventory_left,
                     "description": ele.description,
                     "all_images_url": ele.all_images_url})

    def _get_total_pages(self) -> int:
        page_src = req.get(self._page_0_url, headers=self._headers).json()
        return page_src["numOfPages"]

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
        except AttributeError:
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


if __name__ == "__main__":
    scrapper = Scrapper()
    scrapper.scrap_all_pages()
