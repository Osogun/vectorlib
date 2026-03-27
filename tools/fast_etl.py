from ..datacleaner import DataCleaner
import numpy as np
import pandas as pd


STANDARD_CONFIG = config = {
    "Power": {
        "min": 0,
        "max": 10000,
        "method": "iqr",
        "k": 1.5,
        "q_low": 0.01,
        "q_high": 0.99,
        "winsorization": True,
        "rolling": False,
        "time_window": 24,
    },
    "FlowVolume": {
        "min": 0,
        "max": 150000,
        "method": "iqr",
        "k": 1.5,
        "q_low": 0.01,
        "q_high": 0.99,
        "winsorization": True,
        "rolling": False,
        "time_window": 24,
    },
    "TempDifference": {
        "min": 0,
        "max": 100,
        "method": "iqr",
        "k": 1.5,
        "q_low": 0.01,
        "q_high": 0.99,
        "winsorization": True,
        "rolling": False,
        "time_window": 24,
    },
}


def fast_etl(
    df,
    cols=["Power", "FlowVolume", "TempDifference"],
    config=None,
    Physic=True,
    FillNaN=False,
):
    """
    Szybki proces ETL dla danych wektorowych, obejmujący:
    - Uzupełnianie brakujących wartości liczników energii i objętości (domyślnie)
    - Uzupełnianie brakujących wartości temperatur (domyślnie)
    - Usuwanie wartości niemozliwych fizycznie dla różnicy temperatur, przepływu i mocy
    - Uzupełnianie braków na podstawie fizycznych zależności między zmiennymi
    - Detekcja i obsługa wartości odstających dla różnicy temperatur, przepływu i mocy
    - Opcjonalne uzupełnianie brakujących wartości po detekcji odstających
    Parametry:
    - df: DataFrame z danymi wektorowymi, indeksowany datą i czasem
    - cols - lista kolumn do przetwarzania (np. ["Power", "FlowVolume", "TempDifference"])
    Uwaga! Dotyczy tylko kolumn z zakresu "Power", "FlowVolume", "TempDifference". Pozostałe kolumny (np. "ThermalEnergy", "Volume") są przetwarzane według domyślnych reguł.
    - config: Słownik z konfiguracją parametrów dla poszczególnych zmiennych, np.:
    W config może zawierać następujące klucze:
        - "Power": {
            "min": minimalna dopuszczalna wartość mocy,
            "max": maksymalna dopuszczalna wartość mocy,
            "method": metoda detekcji odstających (np. "iqr"),
            "k": współczynnik dla metody IQR,
            "q_low": dolny quantyl dla metody IQR,
            "q_high": górny quantyl dla metody IQR,
            "winsorization": czy stosować winsoryzację,
            "rolling": czy stosować detekcję na oknie ruchomym,
            "time_window": rozmiar okna czasowego dla detekcji ruchomej (w godzinach),
        },
        - "FlowVolume": { ... }, - analogicznie do "Power"
        - "TempDifference": { ... }, - analogicznie do "Power"
    - "Physic": True/False - czy stosować reguły fizyczne do uzupełniania braków i usuwania wartości niemozliwych
    - "FillNaN": True/False - czy uzupełniać brakujące wartości po detekcji odstających
    Zwraca:
    - Przetworzony DataFrame z uzupełnionymi brakami i obsługą wartości odstających
    """
    if config is None:
        config = STANDARD_CONFIG

    df = df.copy()
    ### Określenie częstotliwości próbkowania danych
    ### ----------------------------------------------------------------
    time_diff = df.index.to_series().diff().dt.total_seconds() / 3600.0  # w godzinach
    time_freq = time_diff.mode()[0]
    ### ----------------------------------------------------------------
    #### Uzupełnianie brakujących wartości liczników energii i objętości
    ### ----------------------------------------------------------------
    for col in ["ThermalEnergy", "Volume", "VolumeWM1", "VolumeWM2"]:
        df[col] = DataCleaner.fill_nan_values(
            df, col, "interpolate", max_gap=int(round(720 / time_freq))
        )
        # Obsługa restartów liczników
        diff = df[col].diff().fillna(0)
        mask = diff < 0
        df.loc[mask, col] = 0
    ### ----------------------------------------------------------------
    ### Uzupełnianie brakujących wartości temperatur
    ### ----------------------------------------------------------------
    for col in ["SourceTemp", "ReturnTemp", "ExternalTemp"]:
        df[col] = DataCleaner.fill_nan_values(
            df, col, "mean", time_window=int(round(24 / time_freq))
        )
    ### ----------------------------------------------------------------
    ### Schłodzenie czynnika
    ### ----------------------------------------------------------------
    if "TempDifference" in cols:
        if Physic:
            # Usuwanie wartości niemozliwych fizycznie
            mask = (df["TempDifference"] < config["TempDifference"]["min"]) | (
                df["TempDifference"] > config["TempDifference"]["max"]
            )
            df.loc[mask, "TempDifference"] = np.nan
            # Uzupełnianie braków na podstawie temperatury zasilania i powrotu
            mask = df["TempDifference"].isna()
            df.loc[mask, "TempDifference"] = (
                df.loc[mask, "SourceTemp"] - df.loc[mask, "ReturnTemp"]
            )
        # Usuwanie wartości odstających
        df["TempDifference"] = DataCleaner.remove_outliers(
            df["TempDifference"],
            method=config["TempDifference"]["method"],
            k=config["TempDifference"]["k"],
            q_low=config["TempDifference"]["q_low"],
            q_high=config["TempDifference"]["q_high"],
            winsorization=config["TempDifference"]["winsorization"],
            rolling=config["TempDifference"]["rolling"],
            time_window=config["TempDifference"]["time_window"],
        )
        # Uzupełnianie brakujących wartości
        if FillNaN:
            df["FlowVolume"] = DataCleaner.fill_nan_values(
                df, "FlowVolume", method="knn", n_neighbors=5
            )
    ### ----------------------------------------------------------------
    ### Przepływ chwilowy
    ### ----------------------------------------------------------------
    if "FlowVolume" in cols:
        if Physic:
            # Usuwanie wartości niemozliwych fizycznie
            mask = (df["FlowVolume"] < config["FlowVolume"]["min"]) | (
                df["FlowVolume"] > config["FlowVolume"]["max"]
            )
            df.loc[mask, "FlowVolume"] = np.nan
            # Uzupełnianie braków na podstawie licznika przepływu
            volume_diff = df["Volume"].diff().fillna(0)
            volume_diff[volume_diff < 0] = np.nan
            mask = df["FlowVolume"].isna()
            df.loc[mask, "FlowVolume"] = (
                volume_diff[mask] * 1000 / time_diff[mask]
            )  # konwersja z m3/h na l/hd

        df["FlowVolume"] = DataCleaner.remove_outliers(
            df["FlowVolume"],
            method=config["FlowVolume"]["method"],
            k=config["FlowVolume"]["k"],
            q_low=config["FlowVolume"]["q_low"],
            q_high=config["FlowVolume"]["q_high"],
            winsorization=config["FlowVolume"]["winsorization"],
            rolling=config["FlowVolume"]["rolling"],
            time_window=config["FlowVolume"]["time_window"],
        )

        if FillNaN:
            df["FlowVolume"] = DataCleaner.fill_nan_values(
                df, "FlowVolume", method="knn", n_neighbors=5
            )
    ### ----------------------------------------------------------------
    # Moc chwilowa
    ### ----------------------------------------------------------------
    if "Power" in cols:
        if Physic:
            mask = (df["Power"] < config["Power"]["min"]) | (
                df["Power"] > config["Power"]["max"]
            )
            df.loc[mask, "Power"] = np.nan
            mask = df["Power"].isna()
            df.loc[mask, "Power"] = (
                df.loc[mask, "TempDifference"] * df.loc[mask, "FlowVolume"] * 4.19
            ) / (
                time_diff[mask] * 3600
            )  # kW
            mask = df["Power"].isna()
            thermal_energy_diff = df["ThermalEnergy"].diff().fillna(0)
            thermal_energy_diff[thermal_energy_diff < 0] = np.nan
            df.loc[mask, "Power"] = (
                thermal_energy_diff[mask] * 1000 / 3.6
            ) / time_diff[
                mask
            ]  # kW

        df["Power"] = DataCleaner.remove_outliers(
            df["Power"],
            method=config["Power"]["method"],
            k=config["Power"]["k"],
            q_low=config["Power"]["q_low"],
            q_high=config["Power"]["q_high"],
            winsorization=config["Power"]["winsorization"],
            rolling=config["Power"]["rolling"],
            time_window=config["Power"]["time_window"],
        )

        if FillNaN:
            df["FlowVolume"] = DataCleaner.fill_nan_values(
                df, "FlowVolume", method="knn", n_neighbors=5
            )
    ### ----------------------------------------------------------------
    return df
