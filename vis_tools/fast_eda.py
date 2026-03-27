import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def fast_eda(df):
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    col_num = numeric_df.shape[1]

    if col_num == 0:
        raise ValueError("No numeric columns found in the DataFrame")

    fig, axes = plt.subplots(col_num, 2, figsize=(12, 5 * col_num))

    # Handle single column case
    if col_num == 1:
        axes = axes.reshape(1, -1)

    for i, column in enumerate(numeric_df.columns):
        axes[i, 0].hist(
            numeric_df[column].dropna(), bins=30, color="skyblue", edgecolor="black"
        )
        axes[i, 0].set_title(f"Histogram of {column}")
        axes[i, 0].set_xlabel(column)
        axes[i, 0].set_ylabel("Frequency")

        axes[i, 1].boxplot(numeric_df[column].dropna(), vert=False)
        axes[i, 1].set_title(f"Boxplot of {column}")
        axes[i, 1].set_xlabel(column)
    plt.tight_layout()
    return fig
