import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def heat_water_analysis(
    df,
    time_freq="d",
    time_window=7,
    trend=None,
    draw_fig=True,
    draw_diffs=True,
):
    """
    Analiza zużycia CWU na podstawie różnicy między dwoma licznikami (WM1 i WM2) lub pojedynczym licznikiem (WM1 lub WM2).
    Parametry:
    - df: DataFrame zawierający kolumny "VolumeWM1" i "VolumeWM2" z danymi liczników, indeksowany datą i czasem.
    - time_freq: Częstotliwość resamplowania danych (np. "d" dla dziennie, "h" dla godzinowo).
    - time_window: Rozmiar okna czasowego dla obliczania trendu (w jednostkach zgodnych z time_freq).
    - trend: Metoda obliczania trendu ("SMA" - średnia krocząca, "EMA" - wykładnicza średnia krocząca, "Linear" - nachylenie trendu liniowego).
    - draw_fig: Czy rysować wykres analizy zużycia CWU.
    - draw_diffs: Czy rysować różnice WM1 i WM2 na wykresie.
    Zwraca:
    - fig: Obiekt figury Matplotlib z wykresem analizy zużycia CWU. Jeśli draw_fig=False, zwraca None.
    - data: Słownik z danymi analizy, zawierający:
        - "HeatWaterUsed": Szacowane zużycie CWU na podstawie różnicy między WM1 a WM2.
        - "HeatWaterUsedTrend": Obliczony trend zużycia CWU.
        - "WM1Diff": Różnica między kolejnymi odczytami WM1.
        - "WM2Diff": Różnica między kolejnymi odczytami WM2.
    """
    if trend is None:
        trend = "SMA"
    df = df.copy()

    vector_name = (
        df["Id"].mode()[0] if "Id" in df.columns and not df["Id"].mode().empty else None
    )
    wm1_diff = df["VolumeWM1"].resample(time_freq).last().diff()
    wm1_diff[wm1_diff < 0] = 0
    wm2_diff = df["VolumeWM2"].resample(time_freq).last().diff()
    wm2_diff[wm2_diff < 0] = 0
    heat_water_used = abs(wm1_diff - wm2_diff)

    if trend == "SMA":
        heat_water_used_trend = heat_water_used.rolling(
            window=time_window, min_periods=1, center=True
        ).mean()
    elif trend == "EMA":
        heat_water_used_trend = heat_water_used.ewm(
            span=time_window, adjust=True
        ).mean()
    elif trend == "Linear":
        heat_water_used_trend = rolling_linear_trend(
            heat_water_used, window=time_window
        )

    # Rysowanie wykresu
    if draw_fig:
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.scatter(
            heat_water_used.index,
            heat_water_used.values,
            label="Heat Water Used [m3]",
            alpha=0.7,
        )
        ax1.plot(
            heat_water_used_trend.index,
            heat_water_used_trend.values,
            label=f"{trend} Trend, time_window={time_window}",
            color="red",
        )
        if draw_diffs:
            ax2 = ax1.twinx()
            ax2.plot(
                wm1_diff.index, wm1_diff.values, label="WM1 Diff [m3]", color="green"
            )
            ax2.plot(
                wm2_diff.index, wm2_diff.values, label="WM2 Diff [m3]", color="orange"
            )
        plt.title(
            f"Heat Water Analysis for {vector_name}"
            if vector_name
            else "Heat Water Analysis"
        )
        plt.xlabel("Time")
        plt.ylabel("Volume [m3]")
        plt.legend()
        plt.grid()

        data = {
            "HeatWaterUsed": heat_water_used,
            "HeatWaterUsedTrend": heat_water_used_trend,
            "WM1Diff": wm1_diff,
            "WM2Diff": wm2_diff,
        }

        return fig, data
    else:
        return None, {
            "HeatWaterUsed": heat_water_used,
            "HeatWaterUsedTrend": heat_water_used_trend,
            "WM1Diff": wm1_diff,
            "WM2Diff": wm2_diff,
        }


def rolling_linear_trend(series: pd.Series, window: int) -> pd.Series:
    """
    Nachylenie trendu liniowego w oknie kroczącym
    """

    def slope(x):
        t = np.arange(len(x))
        a, _ = np.polyfit(t, x, 1)
        return a

    return series.rolling(window).apply(slope, raw=True)
