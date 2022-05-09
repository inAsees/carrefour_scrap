from dataclasses import dataclass
from typing import List, Dict, Optional
import requests as req
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
import csv


@dataclass
class ProductInfo:
    product_url: str
    product_name: str
    price: str
    pack_size: Optional[str]
    inventory_left: Optional[str]
    description: str
    brand: Optional[str]
    image_urls: List[str]


class Scrapper:
    def __init__(self):
        self._base_url = "https://www.carrefour.ke"
        self._page_0_url = "https://www.carrefour.ke/api/v7/categories/FKEN1500000?filter=&sortBy=relevance&" \
                           "currentPage=0&pageSize=60&maxPrice=&minPrice=&areaCode=Westlands%20-%20Nairobi&lang=" \
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
            page_json = req.get(url, headers=self._headers).json()
            self._parse_product_info(page_json["products"])

    def dump(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["product_url", "product_name", "price", "pack_size",
                                                   "inventory_left", "description", "brand", "image_urls"])
            writer.writeheader()
            for ele in tqdm(self._product_info_list, desc="Dumping..."):
                writer.writerow(
                    {
                        "product_url": ele.product_url,
                        "product_name": ele.product_name,
                        "price": ele.price,
                        "pack_size": ele.pack_size,
                        "inventory_left": ele.inventory_left,
                        "description": ele.description,
                        "brand": ele.brand,
                        "image_urls": ele.all_images_url
                    }
                )

    def _get_total_pages(self) -> int:
        page_src = req.get(self._page_0_url, headers=self._headers).json()
        return page_src["numOfPages"]

    def _parse_product_info(self, products_list: List[Dict]) -> ProductInfo:
        for product in products_list:
            product_url = self._get_product_url(product)
            product_name = self._get_product_name(product)
            price = self._get_price(product)
            pack_size = self._get_pack_size(product)
            inventory_left = self._get_inventory_left(product)
            description = self._get_description(product)
            brand = self._get_brand(product)
            image_urls = self._get_image_urls(product)

            return ProductInfo(product_url, product_name, price, pack_size, inventory_left, description, brand,
                               image_urls)

    def _get_product_url(self, product: Dict) -> str:
        return self._base_url + product["links"]["productUrl"]["href"]

    def _get_description(self, product: Dict) -> str:
        product_url = self._get_product_url(product)
        page_src = req.get(product_url, headers=self._headers).text
        product_soup = bs(page_src, "html.parser")
        product_json = product_soup.find("script", {"type": "application/ld+json"}).json()
        return product_json["description"]

    @staticmethod
    def _get_product_name(product: Dict) -> str:
        return product["name"]

    @staticmethod
    def _get_price(product: Dict) -> str:
        return product["price"]["currency"] + " " + product["price"]["minBuyingValue"]

    @staticmethod
    def _get_pack_size(product: Dict) -> Optional[str]:
        try:
            return product["size"]
        except AttributeError:
            print("Pack size not available")
            return None

    @staticmethod
    def _get_inventory_left(product: Dict) -> Optional[str]:
        try:
            return str(product["stock"]["value"])
        except AttributeError as e:
            return None

    @staticmethod
    def _get_brand(product: Dict) -> Optional[str]:
        return product["brand"]["name"]

    @staticmethod
    def _get_image_urls(product: Dict) -> List[str]:
        img_url_list = []
        for idx in product["links"]["images"]:
            img_url_list.append(idx["href"])
        return img_url_list


if __name__ == "__main__":
    scrapper = Scrapper().scrap_all_pages()
