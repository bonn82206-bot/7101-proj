"""
Utility to cap outliers using IQR and apply rolling smoothing. Can disable capping.

Usage:
  python clean_and_smooth.py --raw prepared_dataset.csv --out prepared_dataset_clean.csv \\
      --smooth CSUSHPISA Houses Cons_Material FEDFUNDS UNRATE EmpRate --window 3
"""

import argparse
from pathlib import Path
from typing import Iterable, List

import pandas as pd


def cap_outliers_iqr(df: pd.DataFrame) -> pd.DataFrame:
    """Winsorize numeric columns by IQR fences (Q1-1.5*IQR, Q3+1.5*IQR)."""
    capped = df.copy()
    num_cols = capped.select_dtypes(include=["number"]).columns
    for col in num_cols:
        s = capped[col]
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        capped[col] = s.clip(lower, upper)
    return capped


def smooth_columns(
    df: pd.DataFrame, cols: Iterable[str], window: int, use_past_window: bool
) -> pd.DataFrame:
    """
    Add smoothed versions of selected columns via rolling mean.

    If use_past_window is True, use a trailing window (avoids peeking into the future).
    Otherwise, use a centered window (better for visualization, but not for prediction).
    """
    smoothed = df.copy()
    for col in cols:
        if col not in smoothed:
            continue
        smoothed[f"{col}_smoothed"] = smoothed[col].rolling(
            window=window, center=not use_past_window, min_periods=1
        ).mean()
    return smoothed


def summarize_changes(original: pd.DataFrame, cleaned: pd.DataFrame) -> List[str]:
    """Return human-readable summary of which columns were clipped."""
    changed = []
    num_cols = cleaned.select_dtypes(include=["number"]).columns
    for col in num_cols:
        if col not in original:
            continue
        if not original[col].equals(cleaned[col]):
            changed.append(col)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Outlier capping + smoothing.")
    parser.add_argument("--raw", required=True, help="Path to raw CSV.")
    parser.add_argument("--out", required=True, help="Path to save cleaned CSV.")
    parser.add_argument(
        "--smooth",
        nargs="+",
        default=[],
        help="Columns to smooth (will add *_smoothed).",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=3,
        help="Rolling window size for smoothing (centered).",
    )
    parser.add_argument(
        "--past-window",
        action="store_true",
        help="Use trailing window (only past data) for smoothing to avoid leakage.",
    )
    parser.add_argument(
        "--no-cap",
        action="store_true",
        help="Disable IQR capping; only smoothing will be applied.",
    )
    args = parser.parse_args()

    raw_path = Path(args.raw)
    out_path = Path(args.out)

    df_raw = pd.read_csv(raw_path, parse_dates=["DATE"])
    df_capped = df_raw if args.no_cap else cap_outliers_iqr(df_raw)
    df_clean = smooth_columns(
        df_capped, args.smooth, args.window, use_past_window=args.past_window
    )

    df_clean.to_csv(out_path, index=False, date_format="%Y-%m-%d")

    changed_cols = [] if args.no_cap else summarize_changes(df_raw, df_capped)
    print(f"Saved cleaned data -> {out_path}")
    if changed_cols:
        print("Columns with clipped outliers:", ", ".join(changed_cols))
    elif not args.no_cap:
        print("No columns were clipped by IQR thresholds.")
    print("Smoothed columns:", ", ".join(args.smooth) if args.smooth else "None")
    if args.no_cap:
        print("IQR capping disabled (--no-cap).")


if __name__ == "__main__":
    main()
