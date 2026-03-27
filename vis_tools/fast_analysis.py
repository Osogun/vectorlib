import pandas as pd
import matplotlib.pyplot as plt
from .draw_axhline_with_label import draw_axhline_with_label
from sklearn.linear_model import LinearRegression
import numpy as np


def fast_analysis(
    df,
    column,
    vector_id="None",
    c="TempDifference",
    cmap="viridis",
    s=20,
    regression=False,
    draw_quartiles=True,
    params={"min": 0, "max": 9999},
    quantiles=[0.05, 0.95],
    config={"width": 10, "height": 12},
):
    """
    Analiza mocy w zależności od temperatury zewnętrznej oraz różnicy temperatur.
    Parametry:
    df (pd.DataFrame): Dane do analizy.
    column (str): Nazwa kolumny z danymi do analizy.
    vector_id (str, optional): Identyfikator wektora do wyświetlenia w tytule wykresu. Domyślnie "None".
    c (str, optional): Nazwa kolumny do użycia jako kolor w scatter plot. Domyślnie "TempDifference".
    cmap (str, optional): Nazwa mapy kolorów do użycia w scatter plot. Domyślnie "viridis".
    s (int, optional): Rozmiar punktów w scatter plot. Domyślnie 20.
    regression (bool, optional): Czy rysować linię regresji liniowej na wykresie. Domyślnie False. Jeśli True, funkcja zwróci również model regresji liniowej jako drugi element krotki.
    draw_quartiles (bool, optional): Czy rysować linie kwartylowe na wykresie. Domyślnie True.
    params (dict, optional): Słownik z parametrami filtracji danych. Oczekiwane klucze to "min" i "max". Domyślnie {"min": 0, "max": 9999}.
    quantiles (list, optional): Lista z wartościami kwantyli do narysowania (jeżeli draw_quartiles=True). Domyślnie [0.05, 0.95].
    config (dict, optional): Słownik z parametrami konfiguracji wykresu. Oczekiwane klucze to "width" i "height". Domyślnie {"width": 10, "height": 12}.
    Zwraca:
    fig (matplotlib.figure.Figure): Obiekt figury z wykresami.
    Jeśli regression=True, funkcja zwraca również model regresji liniowej jako drugi element krotki.
    """

    df = df.copy()

    df["filtered"] = df[column].where(
        (df[column] <= params["max"]) & (df[column] >= params["min"])
    )

    if regression:
        mask = (df["ExternalTemp"].isna()) | (df["filtered"].isna())
        x = df.loc[~mask, "ExternalTemp"].values.reshape(-1, 1)
        y = df.loc[~mask, "filtered"].values
        x_time = df.loc[~mask].index
        model = LinearRegression()
        model.fit(x, y)
        y_pred = model.predict(x)
        color = df.loc[~mask, c]
    else:
        x = df["ExternalTemp"].values.reshape(-1, 1)
        y = df["filtered"].values
        x_time = df.index
        color = df[c]

    fig, ax = plt.subplots(2, 1, figsize=(config["width"], config["height"]))
    sc1 = ax[0].scatter(
        x,
        y,
        c=color,
        cmap=cmap,
        s=s,
        label=f"{column}",
    )
    fig.colorbar(sc1, ax=ax[0], label=f"{c}")
    if regression:
        ax[0].plot(
            x,
            y_pred,
            color="red",
            linewidth=2,
            alpha=0.7,
            label=f"Predicted {column}",
        )
    tittle = (
        f"{column} as a function of ExternalTemp"
        if not regression
        else (
            f"{column} as a function of ExternalTemp with Linear Regression"
            if vector_id is None
            else f"{column} as a function of ExternalTemp with Linear Regression\nfor vector {vector_id}"
        )
    )
    ax[0].set_title(tittle)
    ax[0].set_xlabel("ExternalTemp [°C]")
    ax[0].set_ylabel(f"{column}")
    ax[0].minorticks_on()
    ax[0].grid(True, which="major", alpha=1, linewidth=1)
    ax[0].grid(True, which="minor", alpha=0.5, linewidth=0.5)
    ax[0].legend()

    sc2 = ax[1].scatter(
        x_time,
        y,
        c=color,
        cmap=cmap,
        s=s,
        label=f"{column}",
    )
    fig.colorbar(sc2, ax=ax[1], label=f"{c}")
    if draw_quartiles:
        draw_axhline_with_label(
            ax[1],
            y=np.nanmedian(y),
            label=f"Median {column}",
            color="red",
            linestyle="--",
        )
        draw_axhline_with_label(
            ax[1],
            y=np.nanquantile(y, quantiles[0]),
            label=f"{int(quantiles[0]*100)}th Percentile {column}",
            color="orange",
            linestyle=":",
        )
        draw_axhline_with_label(
            ax[1],
            y=np.nanquantile(y, quantiles[1]),
            label=f"{int(quantiles[1]*100)}th Percentile {column}",
            color="orange",
            linestyle=":",
        )
        draw_axhline_with_label(
            ax[1],
            y=np.nanmin(y),
            label=f"Min {column}",
            color="purple",
            linestyle="-.",
        )
        draw_axhline_with_label(
            ax[1],
            y=np.nanmax(y),
            label=f"Max {column}",
            color="purple",
            linestyle="-.",
        )
    tittle = (
        f"{column} over time"
        if vector_id is None
        else f"{column} over time for vector {vector_id}"
    )
    ax[1].set_title(tittle)
    ax[1].legend()
    ax[1].set_xlabel("Date")
    ax[1].set_ylabel(f"{column}")
    ax[1].minorticks_on()
    ax[1].grid(True, which="major", alpha=1, linewidth=1)
    ax[1].grid(True, which="minor", alpha=0.5, linewidth=0.5)
    fig.tight_layout()

    if regression:
        return fig, model

    return fig
