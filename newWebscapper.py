from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/krakow/"

data = []

for i in range(1, 3):
    response = requests.get(f"{BASE_URL}?page={i}")

    soup = BeautifulSoup(response.text, "html.parser")

    offers = soup.find_all("div", class_="css-1sw7q4x")
    print(f"Trwa ogarnianie strony nr {i}...")

    for offer in offers:

        title = offer.find("h4", class_="css-hzlye5")
        price = offer.find("p", class_= "css-blr5zl")
        link = offer.find("a")
        area = offer.find("span", class_="css-h59g4b")
        region = offer.find("p", class_="css-1b24pxk")

        try:
            data_row = {
                "Tytuł": title.text,
                "Cena": price.text,
                "link": link["href"],
                "Metraż": area.text.split(" ")[0],
                "Dzielnica": region.text
            }

            data.append(data_row)
        except:
            pass

        print(f"Zakończono.")


# OBRÓBKA DANYCH
df = pd.DataFrame(data)

df.to_csv("mieszkania_krakow.csv", index=False, encoding="utf-8")

print(df["Cena"])
df["Cena"] = (
    df["Cena"]
    .str.replace("zł", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.extract(r"(\d+)")
    .astype(float)
)
print(df["Cena"])

# WIZUALIZACJA DANYCH
plt.hist(df["Cena"].dropna(), bins=50)
plt.xlabel("Cena mieszkania w mln złotych")
plt.ylabel("Liczba ofert w danym przedziale")
plt.title("Rozkład cen mieszkań w Krakowie")
plt.show()