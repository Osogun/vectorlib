import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe


def draw_axhline_with_label(ax, y, color, linestyle, label, zorder=5, linewidth=2):
    ax.axhline(y, color=color, linestyle=linestyle, zorder=zorder, linewidth=linewidth)
    txt = ax.text(
        ax.get_xlim()[1],
        y,
        f"{label} : {y:.2f}",
        color=color,
        va="bottom",
        ha="right",
        zorder=zorder,
    )
    txt.set_path_effects([pe.withStroke(linewidth=3, foreground="white")])
