import webbrowser

from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from folium.plugins import MiniMap

from upgradedProject.config import BASE_URL, CITY_COORDINATES, CSS_TITLE_STYLE, geopandas_to_olx_names_dict


def scrap_offers(max_websites=2) -> pd.DataFrame:
    """Returns list of offers as a DataFrame"""

    data = []

    for i in range(1, max_websites + 1):

        soup = scrap_one_page(i)
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
                    "link": link["href"] if link["href"].startswith("https") else "https://www.olx.pl" + link["href"],
                    "Metraż": area.text.split(" ")[0],
                    "Dzielnica": region.text.strip().split(" - ")[0].split(", ")[1]
                }

                data.append(data_row)
            except:
                pass

    return pd.DataFrame(data)

def scrap_one_page(page_number: int):
    """Downloads and parses pages from one page in OLX"""
    response = requests.get(f"{BASE_URL}?page={page_number}")
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")



def edit_dataframe(data_frame: pd.DataFrame):

    data_frame["Cena"] = (
        data_frame["Cena"]
        .str.replace("zł", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.extract(r"(\d+)")
        .astype(float)
    )

    data_frame["Metraż"] = pd.to_numeric(df["Metraż"].str.replace(",", "."), errors="coerce")
    data_frame["Cena_m2"] = data_frame["Cena"] / data_frame["Metraż"]


def group_and_aggregate_data(data_frame: pd.DataFrame) -> pd.DataFrame:

    result_data_frame = data_frame.groupby("Dzielnica").agg({
        "Tytuł": lambda x: list(x),
        "link": lambda x: list(x),
        "Cena_m2": "mean"
    }).rename(columns={"Cena_m2": "Średnia cena/m²"})

    result_data_frame["Liczba ofert"] = result_data_frame["Tytuł"].apply(len)
    result_data_frame = result_data_frame.reset_index()

    return result_data_frame


def generate_geodata(offers_data: pd.DataFrame) -> pd.DataFrame:
    result_geodata = gpd.read_file("../districts/krakow-dzielnice.geojson")
    result_geodata["name"] = result_geodata["name"].map(geopandas_to_olx_names_dict)
    result_geodata = result_geodata.merge(offers_data, left_on="name", right_on="Dzielnica", how="left")
    result_geodata["Liczba ofert"] = result_geodata["Liczba ofert"].fillna(0)

    return result_geodata


def generate_map(map_data):

    m = folium.Map(location=CITY_COORDINATES, zoom_start=12, zoom_control=True)
    choropleth_oferty = folium.Choropleth(
        geo_data=map_data,
        data=map_data,
        columns=["name", "Liczba ofert"],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Liczba ofert",
        name="Liczba ofert"  # <<< NAZWA WARSTWY
    ).add_to(m)
    # --- WARSTWA: Średnia cena za m² ---
    choropleth_cena = folium.Choropleth(
        geo_data=map_data,
        data=map_data,
        columns=["name", "Średnia cena/m²"],
        key_on="feature.properties.name",
        fill_color="PuBuGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Średnia cena za m²",
        name="Średnia cena za m²"  # <<< NAZWA WARSTWY
    ).add_to(m)

    fg_oferty = folium.FeatureGroup(name="Etykiety ofert")
    fg_cena = folium.FeatureGroup(name="Etykiety cen")


    for _, row in map_data.iterrows():
        centroid = row["geometry"].centroid
        if pd.notnull(row["Liczba ofert"]) and row["Liczba ofert"] > 0:
            tytuly = row["Tytuł"][:5]
            linki = row["link"][:5]

            # łączymy w klikalne odnośniki HTML
            oferty_html = "<br>".join(
                [f'<a href="{l}" target="_blank">{t}</a>' for t, l in zip(tytuly, linki)]
            )

            popup_html = f"""
            <b>{row['name']}</b><br>
            Liczba ofert: {int(row['Liczba ofert'])}<br>
            Średnia cena za m²: {row['Średnia cena/m²']:.0f} zł<br>
            <br>
            <u>Przykładowe mieszkania:</u><br>
            {oferty_html}
            """
        else:
            popup_html = f"<b>{row['name']}</b><br>Brak ofert"

        folium.Marker(
            [centroid.y, centroid.x],
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(fg_cena)

        folium.map.Marker(
            [centroid.y, centroid.x],
            icon=folium.DivIcon(
                html=f"<div style='{CSS_TITLE_STYLE}'>{row['name']}</div>",
                icon_anchor=(-30, 60),
                icon_size=(50, 50)
            )
        ).add_to(m)

    fg_oferty.add_to(m)
    fg_cena.add_to(m)

    folium.plugins.MiniMap(toggle_display=True).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    m.save("./mapa_oferty_kraków_test.html")


# OBRÓBKA DANYCH
df: pd.DataFrame = scrap_offers(3)

df.to_csv("mieszkania_krakow.csv", index=False, encoding="utf-8")
edit_dataframe(df)

grouped_olx_data = group_and_aggregate_data(df)
regions_geodata = generate_geodata(grouped_olx_data)

generate_map(regions_geodata)
webbrowser.open("mapa_oferty_kraków_test.html")
