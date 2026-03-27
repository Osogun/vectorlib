import pandas as pd
import matplotlib.pyplot as plt
from .draw_axhline_with_label import draw_axhline_with_label
from sklearn.linear_model import LinearRegression
import numpy as np


def power_analysis(
    df,
    vector_id="None",
    draw_quartiles=True,
    params={"power_min": 0, "power_max": 8000},
    config={"width": 10, "height": 12},
):
    """
    Analiza mocy w zależności od temperatury zewnętrznej oraz różnicy temperatur.
    Parametry:
    df (pd.DataFrame): Dane do analizy.
    vector_id (str, optional): Identyfikator wektora do wyświetlenia w tytule wykresu. Domyślnie "None".
    draw_quartiles (bool, optional): Czy rysować linie kwartylowe na wykresie. Domyślnie True.
    params (dict, optional): Słownik z parametrami filtracji danych. Oczekiwane klucze to "power_min" i "power_max". Domyślnie {"power_min": 0, "power_max": 8000}.
    config (dict, optional): Słownik z parametrami konfiguracji wykresu. Oczekiwane klucze to "width" i "height". Domyślnie {"width": 10, "height": 12}.
    Zwraca:
    fig (matplotlib.figure.Figure): Obiekt figury z wykresami.
    """

    df = df.copy()

    df["filtered_Power"] = df["Power"].where(
        (df["Power"] < params["power_max"]) & (df["Power"] > params["power_min"])
    )
    mask = (df["ExternalTemp"].isna()) | (df["filtered_Power"].isna())
    x = df.loc[~mask, "ExternalTemp"].values.reshape(-1, 1)
    y = df.loc[~mask, "filtered_Power"].values
    x_time = df.loc[~mask].index
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    fig, ax = plt.subplots(2, 1, figsize=(config["width"], config["height"]))
    sc1 = ax[0].scatter(
        x,
        y,
        c=df.loc[~mask, "TempDifference"],
        cmap="viridis",
        s=1,
        label="Actual Power [kW]",
    )
    fig.colorbar(sc1, ax=ax[0], label="TempDifference [°C]")
    ax[0].plot(
        x, y_pred, color="red", linewidth=2, alpha=0.7, label="Predicted Power [kW]"
    )
    tittle = (
        f"Power as a function of ExternalTemp with Linear Regression"
        if vector_id is None
        else f"Power as a function of ExternalTemp with Linear Regression\nfor vector {vector_id}"
    )
    ax[0].set_title(tittle)
    ax[0].set_xlabel("ExternalTemp [°C]")
    ax[0].set_ylabel("Power [kW]")
    ax[0].minorticks_on()
    ax[0].grid(True, which="major", alpha=1, linewidth=1)
    ax[0].grid(True, which="minor", alpha=0.5, linewidth=0.5)
    ax[0].legend()

    sc2 = ax[1].scatter(
        x_time,
        y,
        c=df.loc[~mask, "TempDifference"],
        cmap="viridis",
        s=1,
        label="Power [kW]",
    )
    fig.colorbar(sc2, ax=ax[1], label="TempDifference [°C]")
    if draw_quartiles:
        draw_axhline_with_label(
            ax[1],
            y=np.nanmedian(y),
            label="Median Power [kW]",
            color="red",
            linestyle="--",
        )
        draw_axhline_with_label(
            ax[1],
            y=np.nanquantile(y, 0.10),
            label="10th Percentile [kW]",
            color="orange",
            linestyle=":",
        )
        draw_axhline_with_label(
            ax[1],
            y=np.nanquantile(y, 0.90),
            label="90th Percentile [kW]",
            color="orange",
            linestyle=":",
        )
        draw_axhline_with_label(
            ax[1],
            y=np.nanmin(y),
            label="Min Power [kW]",
            color="purple",
            linestyle="-.",
        )
        draw_axhline_with_label(
            ax[1],
            y=np.nanmax(y),
            label="Max Power [kW]",
            color="purple",
            linestyle="-.",
        )
    tittle = (
        f"Power over time"
        if vector_id is None
        else f"Power over time for vector {vector_id}"
    )
    ax[1].set_title(tittle)
    ax[1].legend()
    ax[1].set_xlabel("Date")
    ax[1].set_ylabel("Power [kW]")
    ax[1].minorticks_on()
    ax[1].grid(True, which="major", alpha=1, linewidth=1)
    ax[1].grid(True, which="minor", alpha=0.5, linewidth=0.5)
    fig.tight_layout()

    return fig
