import pandas as pd
import matplotlib.pyplot as plt


def draw_nan_analysis(series):
    """Rysuje wykres analizy brakujących danych w serii czasowej.
    Parametry:
    series (pd.Series): Seria do analizy.
    Zwraca:
    matplotlib.axes.Axes: Obiekt osi wykresu.
    """
    is_nan = series.isna()
    groups = is_nan.ne(is_nan.shift()).cumsum()

    nan_lengths = is_nan.groupby(groups).transform("sum").where(is_nan, 0)

    _, ax = plt.subplots(figsize=(12, 4))
    ax.bar(series.index, nan_lengths)
    ax.set_ylabel("Długość ciągłego NaN")
    return ax
