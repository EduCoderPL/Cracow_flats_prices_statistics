import pandas as pd


class DataProcessor:

    def edit_dataframe(self, data_frame: pd.DataFrame)-> pd.DataFrame:

        data_frame["Cena"] = (
            data_frame["Cena"]
            .str.replace("zł", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.extract(r"(\d+)")
            .astype(float)
        )

        data_frame["Metraż"] = pd.to_numeric(data_frame["Metraż"].str.replace(",", "."), errors="coerce")
        data_frame["Cena_m2"] = data_frame["Cena"] / data_frame["Metraż"]

        return data_frame

    def group_and_aggregate_data(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        result_data_frame = data_frame.groupby("Dzielnica").agg({
            "Tytuł": lambda x: list(x),
            "link": lambda x: list(x),
            "Cena_m2": "mean"
        }).rename(columns={"Cena_m2": "Średnia cena/m²"})

        result_data_frame["Liczba ofert"] = result_data_frame["Tytuł"].apply(len)
        return result_data_frame.reset_index()
