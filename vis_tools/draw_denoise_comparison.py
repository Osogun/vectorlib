import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .draw_axhline_with_label import draw_axhline_with_label


def draw_denoise_comparison(df, df_denoised, vector_name, show_quartiles=False):
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    numeric_df_denoised = df_denoised.select_dtypes(include=[np.number])

    n_cols = numeric_df.shape[1]

    if n_cols == 0:
        raise ValueError("No numeric columns found in the DataFrame")

    fig, ax = plt.subplots(
        n_cols, 2, figsize=(12, 3 * n_cols), sharex=True, constrained_layout=True
    )

    # Handle single column case
    if n_cols == 1:
        ax = ax.reshape(1, -1)

    for i, column in enumerate(numeric_df.columns):
        ax[i, 0].plot(
            numeric_df.index, numeric_df[column], label="Oryginalny szereg", alpha=0.7
        )
        ax[i, 0].set_title(f"{vector_name}: {column}, original")
        ax[i, 0].grid(True, alpha=0.3)

        ax[i, 1].plot(
            numeric_df_denoised.index,
            numeric_df_denoised[column],
            label="Oczyszczony szereg",
            color="orange",
            alpha=0.7,
        )
        ax[i, 1].set_title(f"{vector_name}: {column}, denoised")
        ax[i, 1].grid(True, alpha=0.3)
        ax[i, 1].set_ylabel("Wartość")

        # Zaznaczmy kwartyle i mediane razem z ich wartością na wykresie
        if show_quartiles:
            q2_after = numeric_df_denoised[column].median()
            q1_after = numeric_df_denoised[column].quantile(0.25)
            q3_after = numeric_df_denoised[column].quantile(0.75)
            min_val_after = numeric_df_denoised[column].min()
            max_val_after = numeric_df_denoised[column].max()
            q2_before = numeric_df[column].median()
            q1_before = numeric_df[column].quantile(0.25)
            q3_before = numeric_df[column].quantile(0.75)
            min_val_before = numeric_df[column].min()
            max_val_before = numeric_df[column].max()
            draw_axhline_with_label(ax[i, 0], q2_before, "green", "--", "Mediana (Q2)")
            draw_axhline_with_label(ax[i, 0], q1_before, "purple", ":", "Q1 (25%)")
            draw_axhline_with_label(ax[i, 0], q3_before, "purple", ":", "Q3 (75%)")
            draw_axhline_with_label(ax[i, 0], min_val_before, "red", "-.", "Min")
            draw_axhline_with_label(ax[i, 0], max_val_before, "blue", "-.", "Max")
            draw_axhline_with_label(ax[i, 1], q2_after, "green", "--", "Mediana (Q2)")
            draw_axhline_with_label(ax[i, 1], q1_after, "purple", ":", "Q1 (25%)")
            draw_axhline_with_label(ax[i, 1], q3_after, "purple", ":", "Q3 (75%)")
            draw_axhline_with_label(ax[i, 1], min_val_after, "red", "-.", "Min")
            draw_axhline_with_label(ax[i, 1], max_val_after, "blue", "-.", "Max")

    ax[-1, 0].set_xlabel("Data")
    ax[-1, 1].set_xlabel("Data")
    return fig
