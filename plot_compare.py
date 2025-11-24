"""
Quick visual comparison of raw vs cleaned/smoothed time series.

Usage:
  python plot_compare.py --raw prepared_dataset.csv --clean prepared_dataset_clean.csv \\
      --cols CSUSHPISA UNRATE FEDFUNDS Houses Cons_Material EmpRate
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot raw vs cleaned series.")
    parser.add_argument("--raw", required=True, help="Path to raw CSV.")
    parser.add_argument("--clean", required=True, help="Path to cleaned CSV.")
    parser.add_argument(
        "--cols",
        nargs="+",
        required=True,
        help="Columns to plot (will look for *_smoothed in clean).",
    )
    args = parser.parse_args()

    raw = pd.read_csv(Path(args.raw), parse_dates=["DATE"])
    clean = pd.read_csv(Path(args.clean), parse_dates=["DATE"])

    fig, axes = plt.subplots(len(args.cols), 1, figsize=(10, 2.5 * len(args.cols)), sharex=True)

    if len(args.cols) == 1:
        axes = [axes]

    for ax, col in zip(axes, args.cols):
        ax.plot(raw["DATE"], raw[col], color="tab:blue", alpha=0.6, label=f"{col} raw")
        sm_col = f"{col}_smoothed"
        series = clean[sm_col] if sm_col in clean else clean[col]
        ax.plot(clean["DATE"], series, color="tab:orange", label=f"{col} cleaned/smoothed")
        ax.set_ylabel(col)
        ax.legend(loc="upper left")

    axes[-1].set_xlabel("Date")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
