import pandas as pd

from upgradedProject.config import OUTPUT_FILE_NAME, geopandas_to_olx_names_dict
from upgradedProject.dataProcessor import DataProcessor
from upgradedProject.geoDataProcessor import GeoDataProcessor
from upgradedProject.mapGenerator import MapGenerator
from upgradedProject.scrapper import Scrapper


class MainApp:

    def __init__(self, max_pages=3):
        self.scrapper = Scrapper(max_pages)
        self.data_processor = DataProcessor()
        self.geodata_processor = GeoDataProcessor("../districts/krakow-dzielnice.geojson", geopandas_to_olx_names_dict)
        self.map_generator = MapGenerator()
        print("Created app")

    def run(self):
        # OBRÓBKA DANYCH
        df: pd.DataFrame = self.scrapper.scrap_offers()
        df.to_csv("mieszkania_krakow.csv", index=False, encoding="utf-8")

        df = self.data_processor.edit_dataframe(df)

        grouped_df = self.data_processor.group_and_aggregate_data(df)
        regions_geodata = self.geodata_processor.generate_geodata(grouped_df)

        self.map_generator.generate_map(regions_geodata, OUTPUT_FILE_NAME)





if __name__ == "__main__":
    app = MainApp(3)
    app.run()
