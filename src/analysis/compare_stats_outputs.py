import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def infer_key_columns(df: pd.DataFrame) -> list[str]:
    candidates = [
        ["tumor_type", "ae"],
        ["drug_category", "ae"],
    ]
    for keys in candidates:
        if all(k in df.columns for k in keys):
            return keys
    if "ae" in df.columns:
        return ["ae"]
    raise ValueError(
        "Could not infer key columns. Please pass --keys explicitly for this file pair."
    )


def is_missing(value) -> bool:
    return pd.isna(value)


def values_equal(left, right, float_tol: float) -> bool:
    if is_missing(left) and is_missing(right):
        return True

    left_num = pd.to_numeric(pd.Series([left]), errors="coerce").iloc[0]
    right_num = pd.to_numeric(pd.Series([right]), errors="coerce").iloc[0]

    if not pd.isna(left_num) and not pd.isna(right_num):
        return bool(np.isclose(left_num, right_num, atol=float_tol, rtol=0.0))

    return str(left) == str(right)


def values_equal_trimmed_text(left, right) -> bool:
    if is_missing(left) and is_missing(right):
        return True
    return str(left).strip() == str(right).strip()


def normalize_key_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def compare_pair(current_path: Path, copy_path: Path, keys: list[str] | None, float_tol: float) -> int:
    current_df = pd.read_csv(current_path)
    copy_df = pd.read_csv(copy_path)

    if keys is None:
        keys = infer_key_columns(current_df)

    if set(current_df.columns) != set(copy_df.columns):
        current_only = sorted(set(current_df.columns) - set(copy_df.columns))
        copy_only = sorted(set(copy_df.columns) - set(current_df.columns))
        print(f"\n{current_path.name} vs {copy_path.name}")
        print("Column mismatch detected:")
        print(f"  Columns only in current: {current_only}")
        print(f"  Columns only in copy:    {copy_only}")
        return 1

    ordered_columns = list(current_df.columns)

    left = current_df.copy()
    right = copy_df.copy()

    norm_key_cols = [f"__norm_key_{key}" for key in keys]
    for key, norm_col in zip(keys, norm_key_cols):
        left[norm_col] = left[key].map(normalize_key_value)
        right[norm_col] = right[key].map(normalize_key_value)

    for side_name, side_df in (("current", left), ("copy", right)):
        duplicates = side_df.duplicated(subset=norm_key_cols, keep=False)
        if duplicates.any():
            print(f"\n{current_path.name} vs {copy_path.name}")
            print(f"Duplicate keys in {side_name} file after normalization. Sample:")
            print(side_df.loc[duplicates, keys].head(10).to_string(index=False))
            return 1

    merged = left.merge(
        right,
        on=norm_key_cols,
        how="outer",
        suffixes=("_current", "_copy"),
        indicator=True,
    )

    missing_left = merged[merged["_merge"] == "right_only"]
    missing_right = merged[merged["_merge"] == "left_only"]

    differences: list[tuple[int, dict, str, object, object]] = []
    numeric_differences: list[tuple[int, dict, str, object, object]] = []
    whitespace_only_differences: list[tuple[int, dict, str, object, object]] = []

    matched = merged[merged["_merge"] == "both"].reset_index(drop=True)
    for row_idx in range(len(matched)):
        key_snapshot = {
            key: matched.at[row_idx, f"{key}_current"]
            if f"{key}_current" in matched.columns
            else matched.at[row_idx, f"{key}_copy"]
            for key in keys
        }
        for col in ordered_columns:
            left_col = f"{col}_current"
            right_col = f"{col}_copy"
            if left_col not in matched.columns or right_col not in matched.columns:
                continue
            left_val = matched.at[row_idx, left_col]
            right_val = matched.at[row_idx, right_col]
            if not values_equal(left_val, right_val, float_tol=float_tol):
                diff_entry = (row_idx, key_snapshot, col, left_val, right_val)
                differences.append(diff_entry)

                left_num = pd.to_numeric(pd.Series([left_val]), errors="coerce").iloc[0]
                right_num = pd.to_numeric(pd.Series([right_val]), errors="coerce").iloc[0]
                if not pd.isna(left_num) and not pd.isna(right_num):
                    numeric_differences.append(diff_entry)
                elif values_equal_trimmed_text(left_val, right_val):
                    whitespace_only_differences.append(diff_entry)

    print(f"\n{current_path.name} vs {copy_path.name}")
    print(f"Keys used: {keys}")

    if len(missing_left) > 0 or len(missing_right) > 0:
        print("❌ Key-set mismatch detected.")
        print(f"  Keys only in current: {len(missing_right)}")
        print(f"  Keys only in copy:    {len(missing_left)}")
        if len(missing_right) > 0:
            sample = [f"{k}_current" for k in keys if f"{k}_current" in missing_right.columns]
            print("  Sample keys only in current:")
            print(missing_right[sample].head(5).to_string(index=False))
        if len(missing_left) > 0:
            sample = [f"{k}_copy" for k in keys if f"{k}_copy" in missing_left.columns]
            print("  Sample keys only in copy:")
            print(missing_left[sample].head(5).to_string(index=False))
        return 1

    if not differences:
        print("✅ All values match (after key-based row alignment).")
        return 0

    print(f"❌ Found {len(differences)} differing cells.")
    print(f"  Numeric differences: {len(numeric_differences)}")
    print(f"  Whitespace-only text differences: {len(whitespace_only_differences)}")

    if len(numeric_differences) == 0:
        print("✅ Statistical/numeric outputs match; differences are non-numeric formatting only.")

    print("First 20 differences:")
    for row_idx, key_snapshot, col, left_val, right_val in differences[:20]:
        print(
            f"  row={row_idx} keys={key_snapshot} col='{col}' current={left_val!r} copy={right_val!r}"
        )

    return 0 if len(numeric_differences) == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare stats CSV outputs with their copied versions value-by-value."
    )
    parser.add_argument(
        "--stats-dir",
        default="data/processed/statistics",
        help="Directory containing the stats CSV files.",
    )
    parser.add_argument(
        "--float-tol",
        type=float,
        default=1e-12,
        help="Absolute tolerance for numeric comparisons.",
    )
    args = parser.parse_args()

    stats_dir = Path(args.stats_dir)
    pairs = [
        (stats_dir / "tumor_type_stats.csv", stats_dir / "tumor_type_stats copy.csv", ["tumor_type", "ae"]),
        (stats_dir / "drug_category_stats.csv", stats_dir / "drug_category_stats copy.csv", ["drug_category", "ae"]),
    ]

    exit_code = 0
    for current_path, copy_path, keys in pairs:
        if not current_path.exists() or not copy_path.exists():
            print(f"\nSkipping pair: {current_path.name} / {copy_path.name} (file missing)")
            exit_code = 1
            continue
        result = compare_pair(current_path, copy_path, keys=keys, float_tol=args.float_tol)
        exit_code = max(exit_code, result)

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
