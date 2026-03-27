import pandas as pd
from .configs import vector_config, vector_clone_config, weather_Gdansk, weather_Tczew
import os
import sys


class DataLoader:
    """
    Klasa do ładowania danych z plików Vector i podłaczania danych pogodowych na podstawie podanej konfiguracji.
    Umożliwia iteracyjne ładowanie wielu plików, zwracając każdy jako pandas DataFrame.

    Parametry:
    fpathes (list): Lista ścieżek do plików danych Vector do załadowania. Mogą to być pliki CSV lub XLSX.
    config (dict): Słownik konfiguracji określający kolumny do załadowania, częstotliwość czasową,
        separator, kodowanie itp. Jeśli None lub "clone_vector", używana jest domyślna konfiguracja dla plików z bazy klona vectora.
        Jeśli "vector", używana jest konfiguracja dla plików z bazy vectora.

    Zwraca:
    DataLoader: Obiekt DataLoader, który można iterować, aby uzyskać kolejne DataFrame z załadowanymi danymi.

    Przykład użycia:
    dl = DataLoader(
        fpathes=["data1.csv", "data2.xlsx"],
        config="vector"
    )
    for df in dl:
        print(df.head())

    Alternatywnie aby wyciągnąc jeden DataFrame:
    dl = DataLoader(
        fpathes=["data1.csv", "data2.xlsx"],
        config="vector"
    )
    df = next(dl)
    """

    def __init__(self, fpathes, config=None, weather_config=None, write_log=False):
        self.fpathes = fpathes

        if config is None or config == "clone_vector":
            config = vector_clone_config
        if config == "vector":
            config = vector_config

        if weather_config is None or weather_config == "gdansk":
            weather_config = weather_Gdansk
        elif weather_config == "port_polnocny":
            weather_config = weather_Gdansk
            weather_config["data_col"] = 1
        elif weather_config == "reibechowo":
            weather_config = weather_Gdansk
            weather_config["data_col"] = 4
        elif weather_config == "tczew":
            weather_config = weather_Tczew

        self.config = config
        self.weather_config = weather_config
        self.weather_data = None
        self.log = [] if write_log else None

        # Wewnętrzny generator, który faktycznie produkuje kolejne DataFrame
        # Dzięki temu obiekt DataLoader może być jednocześnie iteratorem
        self.gen = None

    def __iter__(self):
        """
        Metoda wywoływana, przez iter(dl) albo for df in dl, gdzie dl = DataLoader(...)
        Tworzy nowy, iterowalny generator danych i zapisuje go w self.gen.
        """
        self.gen = self.load_data()
        return self

    def __next__(self):
        """
        Metoda wywoływana przez next(dl), gdzie dl = DataLoader(...)
        Zwraca kolejny DataFrame z generatora danych.
        """
        if self.gen is None:
            iter(self)
        return next(self.gen)

    def load_data(self):
        # Procedura zwracająca generator danych z plików
        try:
            self.load_weather_data()
        except Exception as e:
            raise RuntimeError(f"Failed to load weather data: {e}")

        for fpath in self.fpathes:
            try:
                file_ext = None
                fpath_lower = fpath.lower()
                if fpath_lower.endswith(".csv"):
                    file_ext = "csv"
                elif fpath_lower.endswith(".xlsx") or fpath_lower.endswith(".xls"):
                    file_ext = "xlsx"
                else:
                    if self.log is not None:
                        self.log.append(
                            f"{fpath} : Unsupported file format. Skipping this file."
                        )
                    raise ValueError(f"Unsupported file format: {fpath}")

                if "UNIT_DATE" not in self.config["columns"].keys():
                    if self.log is not None:
                        self.log.append(
                            f"{fpath} : UNIT_DATE column must be included in columns to load. Skipping this file."
                        )
                    raise ValueError("UNIT_DATE must be included in columns to load.")

                if file_ext == "csv":
                    data = pd.read_csv(
                        fpath,
                        usecols=self.config["columns"].values(),
                        sep=self.config["separator"],
                        encoding=self.config["encoding"],
                    )

                elif file_ext == "xlsx":
                    data = pd.read_excel(
                        fpath,
                        usecols=self.config["columns"].values(),
                    )

                # Pomijanie danych, jeżeli plik ma mniej niż 3 wiersze
                if len(data) < 3:
                    if self.log is not None:
                        self.log.append(
                            f"{fpath} : File has less than 3 rows. Skipping this file."
                        )
                    print(
                        f"Data from {fpath} has less than 3 rows. Skipping this file."
                    )
                    continue

                # Mapowanie kolumn po nazwie, nie po kolejności
                name_map = {
                    v: k for k, v in self.config["columns"].items() if v is not None
                }
                data = data.rename(columns=name_map)
                data["UNIT_DATE"] = pd.to_datetime(data["UNIT_DATE"], errors="coerce")
                data.set_index("UNIT_DATE", inplace=True)

                for col in [col for col in data.columns if col != "Id"]:
                    data[col] = pd.to_numeric(
                        data[col]
                        .astype(str)
                        .str.replace(self.config["decimal_sep"], "."),
                        errors="coerce",
                    )
                data["Id"] = data["Id"].astype(str)

                if self.config["time_frequency"] is not None:
                    data = data.sort_index(ascending=True)
                    data = data.resample(self.config["time_frequency"]).agg(
                        {
                            "Id": "last",
                            "ThermalEnergy": "last",
                            "Volume": "last",
                            "SourceTemp": "mean",
                            "ReturnTemp": "mean",
                            "TempDifference": "mean",
                            "FlowVolume": "mean",
                            "Power": "mean",
                            "VolumeWM1": "last",
                            "VolumeWM2": "last",
                        }
                    )
                    min_date = data.index.min()
                    max_date = data.index.max()
                    full_index = pd.date_range(
                        start=min_date, end=max_date, freq=self.config["time_frequency"]
                    )
                    data = data.reindex(full_index)

                    weather_data = self.weather_data[
                        (self.weather_data.index >= min_date)
                        & (self.weather_data.index <= max_date)
                    ]
                    weather_data = weather_data.resample(
                        self.config["time_frequency"]
                    ).agg({"ExternalTemp": "mean", "Season": "first"})
                    weather_data = weather_data.reindex(full_index)
                else:
                    data = data.sort_index(ascending=True)
                    time_freq = data.index.to_series().diff().mode()[0]
                    min_date = data.index.min()
                    max_date = data.index.max()
                    full_index = pd.date_range(
                        start=min_date, end=max_date, freq=time_freq
                    )
                    data = data.reindex(full_index, method="nearest", tolerance=None)
                    weather_data = self.weather_data[
                        (self.weather_data.index >= min_date)
                        & (self.weather_data.index <= max_date)
                    ]
                    weather_data = weather_data.resample(time_freq).agg(
                        {"ExternalTemp": "mean", "Season": "first"}
                    )
                    weather_data = weather_data.reindex(
                        full_index, method="nearest", tolerance=None
                    )

                data = data.join(weather_data, how=self.config["join_method"])

                yield data
            except Exception as e:
                if self.log is not None:
                    self.log.append(
                        f"{fpath} : Failed to load data from this file. Error: {type(e).__name__}: {str(e)}"
                    )
                print(
                    f"Failed to load data from {fpath}. Error: {type(e).__name__}: {str(e)}"
                )
                continue

    def load_weather_data(self):

        weather_data = pd.read_excel(
            self.weather_config["weather_data_path"],
            sheet_name=self.weather_config["sheet_name"],
            header=self.weather_config["header"],
            skiprows=self.weather_config["skiprows"],
            usecols=[
                self.weather_config["index_col"],
                self.weather_config["data_col"],
                self.weather_config["seson_col"],
            ],
            parse_dates=[self.weather_config["index_col"]],
            index_col=self.weather_config["index_col"],
        )

        weather_data.columns = ["ExternalTemp", "Season"]
        weather_data.index = pd.to_datetime(weather_data.index, errors="coerce")
        weather_data.sort_index(ascending=True)
        self.weather_data = weather_data

    def get_log(self):
        log_path = os.path.join(os.path.dirname(sys.argv[0]), "dataloader_log.txt")
        if self.log is not None:
            with open(log_path, "w", encoding="utf-8") as f:
                for item in self.log:
                    f.write("%s\n" % item)
