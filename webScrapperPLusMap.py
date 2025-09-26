from bs4 import BeautifulSoup
import requests
import pandas as pd
import geopandas as gpd
import folium
import matplotlib.pyplot as plt

converter = {
    "Dzielnica VII Zwierzyniec": "Zwierzyniec",
    "Dzielnica X Swoszowice": "Swoszowice",
    "Dzielnica VIII Dębniki": "Dębniki",
    "Dzielnica XII Biezanow-Prokocim": "Bieżanów-Prokocim",
    "Dzielnica XIII Podgórze": "Podgórze",
    "Dzielnica XVIII Nowa Huta": "Nowa Huta",
    "Dzielnica XVI Bieńczyce": "Bieńczyce",
    "Dzielnica IX Łagiewniki-Borek Fałęcki": "Łagiewniki-Borek Fałęcki",
    "Dzielnica I Stare Miasto": "Stare Miasto",
    "Dzielnica II Grzegórzki": "Grzegórzki",
    "Dzielnica III Prądnik Czerwony": "Prądnik Czerwony",
    "Dzielnica IV Prądnik Biały": "Prądnik Biały",
    "Dzielnica V Krowodrza": "Krowodrza",
    "Dzielnica VI Bronowice": "Bronowice",
    "Dzielnica XI Podgórze Duchackie": "Podgórze Duchackie",
    "Dzielnica XIV Czyżyny": "Czyżyny",
    "Dzielnica XV Mistrzejowice": "Mistrzejowice",
    "Dzielnica XVII Wzgórza Krzeszławickie": "Wzgórza Krzesławickie",
}

# ---- WEBSCRAPPER ---- #
BASE_URL = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/krakow/"

data = []

# --- SCRAPING OLX ---
for i in range(1, 4):  # np. 2 strony
    response = requests.get(f"{BASE_URL}?page={i}")
    soup = BeautifulSoup(response.text, "html.parser")
    offers = soup.find_all("div", class_="css-1sw7q4x")

    for offer in offers:
        print(f"Trwa ogarnianie strony nr {i}...")
        title = offer.find("h4", class_="css-hzlye5")
        price = offer.find("p", class_="css-blr5zl")
        link = offer.find("a")
        area = offer.find("span", class_="css-h59g4b")
        region = offer.find("p", class_="css-1b24pxk")

        try:
            data_row = {
                "Tytuł": title.text,
                "Cena": price.text,
                "Link": link["href"],
                "Metraż": area.text.split(" ")[0],
                "Dzielnica": region.text.strip().split(" - ")[0].split(", ")[1]
            }
            data.append(data_row)
        except:
            pass

        print(f"Zakończono stronę {i}.")


# ---- TWORZENIE DATAFRAME ---- #
df = pd.DataFrame(data)
df.to_csv("mieszkania_krakow.csv", index=False, encoding="utf-8")

# --- CZYSZCZENIE DANYCH --- #

df["Cena"] = (
    df["Cena"]
    .str.replace("zł", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.extract(r"(\d+)")
    .astype(float)
)

df["Metraż"] = pd.to_numeric(df["Metraż"].str.replace(",", "."), errors="coerce")
df["Cena_m2"] = df["Cena"] / df["Metraż"]

# ---- HISTOGRAM CEN ---- #
# plt.hist(df["Cena"].dropna(), bins=50)
# plt.xlabel("Cena mieszkania (PLN)")
# plt.ylabel("Liczba ofert w przedziale")
# plt.title("Rozkład cen mieszkań w Krakowie")
# plt.show()

# ---- AGREGACJA (grupowanie i przypisywanie liczby ofert do danej dzielnicy ---- #
agg = df.groupby("Dzielnica").agg({
    "Tytuł": lambda x: list(x),
    "Cena_m2": "mean"
}).rename(columns={"Cena_m2": "Średnia cena/m²"})

agg["Liczba ofert"] = agg["Tytuł"].apply(len)
agg = agg.reset_index()

# --- GENEROWANIE DZIELNIC KRAKOWA I ŁĄCZENIE ZE STATYSTYKAMI ---
dzielnice = gpd.read_file("districts/krakow-dzielnice.geojson")
dzielnice["name"] = dzielnice["name"].map(converter)

dzielnice = dzielnice.merge(agg, left_on="name", right_on="Dzielnica", how="left")
dzielnice["Liczba ofert"] = dzielnice["Liczba ofert"].fillna(0)


# --- FOLIUM MAPA ---
m = folium.Map(location=[50.0614, 19.9366], zoom_start=12)

# --- WARSTWA: Liczba ofert ---
choropleth_oferty = folium.Choropleth(
    geo_data=dzielnice,
    data=dzielnice,
    columns=["name", "Liczba ofert"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Liczba ofert",
    name="Liczba ofert"   # <<< NAZWA WARSTWY
).add_to(m)

# --- WARSTWA: Średnia cena za m² ---
choropleth_cena = folium.Choropleth(
    geo_data=dzielnice,
    data=dzielnice,
    columns=["name", "Średnia cena/m²"],
    key_on="feature.properties.name",
    fill_color="PuBuGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Średnia cena za m²",
    name="Średnia cena za m²"   # <<< NAZWA WARSTWY
).add_to(m)

# --- ETYKIETY I POPUPY (wspólne dla obu warstw) ---
for _, row in dzielnice.iterrows():
    centroid = row["geometry"].centroid
    if pd.notnull(row["Liczba ofert"]) and row["Liczba ofert"] > 0:
        tytuly = "<br>".join(row["Tytuł"][:5])  # max 5 tytułów na popup
        popup_html = f"""
            <b>{row['name']}</b><br>
            Liczba ofert: {int(row['Liczba ofert'])}<br>
            Średnia cena za m²: {row['Średnia cena/m²']:.0f} zł<br>
            <br>
            <u>Przykładowe mieszkania:</u><br>
            {tytuly}
            """
    else:
        popup_html = f"<b>{row['name']}</b><br>Brak ofert"

    folium.Marker(
        [centroid.y, centroid.x],
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)

# --- PRZEŁĄCZNIK WARSTW ---
folium.LayerControl(collapsed=False).add_to(m)

m.save("mapa_oferty_krakow.html")
print("Mapa zapisana jako mapa_oferty_krakow.html")