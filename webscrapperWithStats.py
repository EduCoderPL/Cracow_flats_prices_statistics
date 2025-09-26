import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/krakow/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

data = []

for i in range(1, 26):

    page = f"{url}?page={i}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Znajdź ogłoszenia mieszkań
    offers = soup.find_all("div", class_="css-1sw7q4x")

    for offer in offers:

        title = offer.find("h4", class_="css-hzlye5")
        price = offer.find("p", class_="css-blr5zl")
        link = offer.find("a")

        if title and price and link:
            print("Tytuł:", title.text.strip())
            print("Cena:", price.text.strip())
            print("Link:", "https://www.olx.pl" + link["href"])
            print("-" * 40)
            data.append({
                "Tytuł": title.text.strip(),
                "Cena": price.text.strip(),
                "Link": "https://www.olx.pl" + link["href"]
            })

df = pd.DataFrame(data)

# Wyświetl pierwsze rekordy
print(df.head())

# Zapisz do CSV (opcjonalnie)
df.to_csv("mieszkania_krakow.csv", index=False, encoding="utf-8")


df["Cena_num"] = (
    df["Cena"]
    .str.replace("zł", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.extract(r"(\d+)")
    .astype(float)
)

import matplotlib.pyplot as plt

plt.hist(df["Cena_num"].dropna(), bins=30)
plt.xlabel("Cena mieszkania [PLN]")
plt.ylabel("Liczba ofert")
plt.title("Rozkład cen mieszkań w Krakowie (OLX)")
plt.show()