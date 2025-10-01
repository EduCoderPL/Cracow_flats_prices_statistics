import pandas as pd
import requests
from bs4 import BeautifulSoup

from upgradedProject.config import BASE_URL


class Scrapper:

    def __init__(self, max_pages: int):
        self.max_pages: int = max_pages

    def scrap_offers(self) -> pd.DataFrame:
        """Returns list of offers as a DataFrame"""

        data = []

        for i in range(1, self.max_pages + 1):

            soup = self.scrap_one_page(i)
            offers = soup.find_all("div", class_="css-1sw7q4x")
            print(f"Trwa ogarnianie strony nr {i}...")

            for offer in offers:

                title = offer.find("h4", class_="css-hzlye5")
                price = offer.find("p", class_="css-blr5zl")
                link = offer.find("a")
                area = offer.find("span", class_="css-h59g4b")
                region = offer.find("p", class_="css-1b24pxk")

                try:
                    data_row = {
                        "Tytuł": title.text,
                        "Cena": price.text,
                        "link": link["href"] if link["href"].startswith("https") else "https://www.olx.pl" + link[
                            "href"],
                        "Metraż": area.text.split(" ")[0],
                        "Dzielnica": region.text.strip().split(" - ")[0].split(", ")[1]
                    }

                    data.append(data_row)
                except:
                    pass

        return pd.DataFrame(data)

    def scrap_one_page(self, page_number: int) -> BeautifulSoup:
        """Downloads and parses pages from one page in OLX"""
        response = requests.get(f"{BASE_URL}?page={page_number}")
        response.raise_for_status()

        return BeautifulSoup(response.text, "html.parser")
