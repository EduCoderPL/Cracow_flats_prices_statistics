import geopandas as gpd
import pandas as pd


class GeoDataProcessor:

    def __init__(self, geojson_path: str, mapping_dict: dict):
        self.geojson_path: str = geojson_path
        self.mapping_dict: dict = mapping_dict

    def generate_geodata(self, offers_data: pd.DataFrame) -> gpd.GeoDataFrame:
        result_geodata = gpd.read_file(self.geojson_path)
        result_geodata["name"] = result_geodata["name"].map(self.mapping_dict)
        result_geodata = result_geodata.merge(offers_data, left_on="name", right_on="Dzielnica", how="left")
        result_geodata["Liczba ofert"] = result_geodata["Liczba ofert"].fillna(0)

        return result_geodata
