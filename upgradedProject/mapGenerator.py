import webbrowser

import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import MiniMap

from upgradedProject.config import CITY_COORDINATES, CSS_TITLE_STYLE


class MapGenerator:


    def generate_map(self, map_data: gpd.GeoDataFrame, output_file: str):

        m = folium.Map(location=CITY_COORDINATES, zoom_start=12, zoom_control=True)
        folium.Choropleth(
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
        folium.Choropleth(
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
        m.save(output_file)
        webbrowser.open(output_file)
