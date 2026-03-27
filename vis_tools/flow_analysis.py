import pandas as pd
import matplotlib.pyplot as plt
from .draw_axhline_with_label import draw_axhline_with_label
from sklearn.linear_model import LinearRegression
import numpy as np


def flow_analysis(
    df,
    vector_id="None",
    draw_quartiles=True,
    params={"flow_min": 350, "flow_max": 300000},
    config={"width": 10, "height": 12},
):
    """
    Analiza przepływu w zależności od temperatury zewnętrznej oraz różnicy temperatur.
    Parametry:
    df (pd.DataFrame): Dane do analizy.
    vector_id (str, optional): Identyfikator wektora do wyświetlenia w tytule wykresu. Domyślnie "None".
    draw_quartiles (bool, optional): Czy rysować linie kwartylowe na wykresie. Domyślnie True.
    params (dict, optional): Słownik z parametrami filtracji danych. Oczekiwane klucze to "flow_min" i "flow_max". Domyślnie {"flow_min": 350, "flow_max": 300000}.
    config (dict, optional): Słownik z parametrami konfiguracji wykresu. Oczekiwane klucze to "width" i "height". Domyślnie {"width": 10, "height": 12}.
    Zwraca:
    fig (matplotlib.figure.Figure): Obiekt figury z wykresami.
    """

    df = df.copy()
    fig, ax = plt.subplots(2, 1, figsize=(config["width"], config["height"]))
    mask = (df["FlowVolume"] > params["flow_min"]) & (
        df["FlowVolume"] < params["flow_max"]
    )
    df["FlowVolume_filtered"] = df["FlowVolume"].where(mask)
    scatter = ax[0].scatter(
        df["ExternalTemp"],
        df["FlowVolume_filtered"],
        c=df["TempDifference"],
        cmap="viridis",
    )
    ax[0].set_xlabel("ExternalTemp [°C]")
    ax[0].set_ylabel("FlowVolume [l/h]")
    title = (
        "FlowVolume as a function of ExternalTemp"
        if vector_id is None
        else f"FlowVolume as a function of ExternalTemp for Vector: {vector_id}"
    )
    ax[0].set_title(title)
    if draw_quartiles:
        draw_axhline_with_label(
            ax[0],
            y=df["FlowVolume_filtered"].median(),
            label="Median FlowVolume [l/h]",
            color="red",
            linestyle="--",
        )
        draw_axhline_with_label(
            ax[0],
            y=df["FlowVolume_filtered"].quantile(0.10),
            label="10th Percentile [l/h]",
            color="orange",
            linestyle=":",
        )
        draw_axhline_with_label(
            ax[0],
            y=df["FlowVolume_filtered"].quantile(0.90),
            label="90th Percentile [l/h]",
            color="orange",
            linestyle=":",
        )
        draw_axhline_with_label(
            ax[0],
            y=df["FlowVolume_filtered"].min(),
            label="Min FlowVolume [l/h]",
            color="purple",
            linestyle="-.",
        )
        draw_axhline_with_label(
            ax[0],
            y=df["FlowVolume_filtered"].max(),
            label="Max FlowVolume [l/h]",
            color="purple",
            linestyle="-.",
        )
    plt.colorbar(scatter, ax=ax[0], label="TempDifference")
    ax[0].minorticks_on()
    ax[0].grid(True, which="major", alpha=1, linewidth=1)
    ax[0].grid(True, which="minor", alpha=0.5, linewidth=0.5)
    ax[0].legend()

    ax[1].hist(
        df["TempDifference"].dropna(), bins=50, color="orange", edgecolor="black"
    )
    tittle = (
        f'Histogram of TempDifference\nMean: {df["TempDifference"].mean():.2f}°C, Std: {df["TempDifference"].std():.2f}°C'
        if vector_id is None
        else f'Histogram of TempDifference for Vector: {vector_id}\nMean: {df["TempDifference"].mean():.2f}°C, Std: {df["TempDifference"].std():.2f}°C'
    )
    ax[1].set_title(tittle)
    ax[1].set_xlabel("TempDifference [°C]")
    ax[1].set_ylabel("Frequency")
    ax[1].minorticks_on()
    ax[1].grid(True, which="major", alpha=1, linewidth=1)
    ax[1].grid(True, which="minor", alpha=0.5, linewidth=0.5)
    fig.tight_layout()

    return fig
