import pandas as pd
import numpy as np


def found_best_span(df):
    ema = []
    for span in [3, 6, 12]:
        ema.append(df["ExternalTemp"].ewm(span=span).mean())
    best_span = max(span, key=lambda x: df["Power"].corr(ema[x]))
    return best_span


def feature_extraction(df, span=3, standardize=True):
    time_delta = df.index.to_series().diff().dt.total_seconds().mode()[0]
    feautures = pd.DataFrame()
    feautures = feautures.reindex(df.index)
    feautures["ExternalTemp"] = df["ExternalTemp"]
    feautures["month_sin"] = np.sin(2 * np.pi * df.index.month / 12)
    feautures["month_cos"] = np.cos(2 * np.pi * df.index.month / 12)
    if time_delta <= 3600:
        feautures["h_sin"] = np.sin(2 * np.pi * df.index.hour / 24)
        feautures["h_cos"] = np.cos(2 * np.pi * df.index.hour / 24)
    feautures["ExternalTempDiff"] = df["ExternalTemp"].diff()
    feautures["ExternalTempEMA"] = df["ExternalTemp"].ewm(span=span).mean()
    if standardize:
        std = feautures.std().replace(0, 1.0)  # ochrona przed dzieleniem przez zero
        feautures = (feautures - feautures.mean()) / std
    return feautures
