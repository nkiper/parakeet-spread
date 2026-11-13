"""Shared plot style for the presentation figures.

Font sizes as in the records-per-year plot (01_explore-sources): title 17, axis labels 15,
tick labels 13, legend 15. Call `apply()` once after importing matplotlib.
"""
import matplotlib.pyplot as plt

# Presentation palette (maps stay grey)
PRIMARY_DARK = "#345D31"   # dark green
PRIMARY_LIGHT = "#C1C16C"  # light olive
SECONDARY = "#DA6B51"      # terracotta
TERTIARY = "#DEB34F"       # mustard

TEXT = "#333333"
MUTED = "#898781"  # secondary text, reference lines, land outlines
GRID = "#e1e0d9"   # grid lines
LAND = "#f0efec"   # land on maps, shaded periods
ANNOTATION_SIZE = 12  # labels inside the plot area (atlas names, start years, ...)

STYLE = {
    "font.size": 13,
    "axes.titlesize": 17,
    "axes.titlelocation": "left",
    "axes.labelsize": 15,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 15,
    "figure.titlesize": 17,
    "text.color": TEXT,
    "axes.titlecolor": TEXT,
    "axes.labelcolor": TEXT,
    "axes.edgecolor": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
}


def apply():
    plt.rcParams.update(STYLE)
