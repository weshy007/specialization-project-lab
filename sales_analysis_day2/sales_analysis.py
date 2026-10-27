"""
Day 2 - Sales Analytics Without Pandas
Squad Python Specialization - Data Science, AI & Analytics

Tasks 1-7 use only the standard library. pandas is allowed in task 8, to check your work.
"""
import csv
from pathlib import Path

DATA_PATH = Path("data") / "electronics_sales.csv"
OUTPUT_PATH = Path("output") / "sales_report.txt"
HIGH_VALUE_THRESHOLD = 50_000.0


def read_sales(path: Path = DATA_PATH) -> list[dict[str, str]]:
    """Read the CSV with the csv module and return the raw rows."""
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    print(f"Rows read: {len(rows)}")
    print(f"Columns found: {', '.join(reader.fieldnames or [])}")
    return rows


def parse_number(value: str) -> float | None:
    """Convert a messy numeric string to a float, or return None if it cannot be trusted."""
    if not isinstance(value, str):
        return None
    cleaned = value.strip().replace(",", "")
    if cleaned.upper().startswith("KES"):
        cleaned = cleaned[3:].strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def convert_rows(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    """Return (clean_rows, skipped_rows). Clean rows have numeric quantity, unit price and revenue."""
    clean_rows = []
    skipped_rows = []
    for row in rows:
        quantity = parse_number(row.get("quantity", ""))
        unit_price = parse_number(row.get("unit_price_kes", ""))
        reasons = []
        if quantity is None:
            reasons.append("invalid quantity")
        elif quantity <= 0:
            reasons.append("quantity must be positive")
        if unit_price is None:
            reasons.append("invalid unit price")
        elif unit_price <= 0:
            reasons.append("unit price must be positive")
        if reasons:
            skipped_rows.append({"sale_id": row.get("sale_id", ""), "reason": "; ".join(reasons)})
            continue

        # Keep the original text fields while adding trusted numeric values for analysis.
        clean_row = dict(row)
        clean_row["quantity"] = quantity
        clean_row["unit_price_kes"] = unit_price
        clean_row["revenue"] = quantity * unit_price
        clean_rows.append(clean_row)
    return clean_rows, skipped_rows


def total_revenue(rows: list[dict]) -> float:
    return sum(row["revenue"] for row in rows)


def revenue_by(rows: list[dict], field: str) -> dict[str, float]:
    """Total revenue grouped by any column (product, store, payment_method...)."""
    totals: dict[str, float] = {}
    for row in rows:
        group = row[field]
        totals[group] = totals.get(group, 0.0) + row["revenue"]
    return totals


def top_n(totals: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the n highest (key, value) pairs, highest first."""
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:n]


def high_value(rows: list[dict], threshold: float) -> list[dict]:
    """Transactions whose revenue is at or above threshold (use a comprehension)."""
    return [row for row in rows if row["revenue"] >= threshold]


# Reusable statistics - implement these yourself, no statistics module.
def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("mean() requires at least one value")
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("median() requires at least one value")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def minimum_maximum(values: list[float]) -> tuple[float, float]:
    if not values:
        raise ValueError("minimum_maximum() requires at least one value")
    minimum = values[0]
    maximum = values[0]
    for value in values[1:]:
        if value < minimum:
            minimum = value
        if value > maximum:
            maximum = value
    return minimum, maximum


def verify_with_pandas(path: Path, my_results: dict) -> list[str]:
    """Recompute the headline numbers with pandas and print whether each one matches."""
    import pandas as pd

    frame = pd.read_csv(path, dtype=str)
    frame["quantity_num"] = frame["quantity"].map(parse_number)
    frame["price_num"] = frame["unit_price_kes"].map(parse_number)
    valid = (
        frame["quantity_num"].notna()
        & (frame["quantity_num"] > 0)
        & frame["price_num"].notna()
        & (frame["price_num"] > 0)
    )
    frame = frame.loc[valid].copy()
    frame["revenue"] = frame["quantity_num"] * frame["price_num"]
    pandas_total = float(frame["revenue"].sum())
    pandas_by_product = frame.groupby("product")["revenue"].sum().to_dict()
    pandas_top = top_n(pandas_by_product)
    pandas_mean = float(frame["revenue"].mean())
    pandas_median = float(frame["revenue"].median())

    def matches(left: float, right: float) -> bool:
        return abs(left - right) < 0.005

    total_match = matches(my_results["total"], pandas_total)
    products_match = all(
        product in pandas_by_product and matches(amount, pandas_by_product[product])
        for product, amount in my_results["by_product"].items()
    ) and len(my_results["by_product"]) == len(pandas_by_product)
    top_match = my_results["top_three"] == pandas_top
    stats_match = matches(my_results["mean"], pandas_mean) and matches(my_results["median"], pandas_median)
    total_status = "MATCH" if total_match else f"MISMATCH (pure={my_results['total']}, pandas={pandas_total})"
    top_status = "MATCH" if top_match else f"MISMATCH (pure={my_results['top_three']}, pandas={pandas_top})"
    stats_status = (
        "MATCH"
        if stats_match
        else f"MISMATCH (pure=({my_results['mean']}, {my_results['median']}), pandas=({pandas_mean}, {pandas_median}))"
    )
    verification_lines = [
        "=== pandas verification ===",
        f"Total revenue      : {total_status}",
        f"Revenue by product : {'MATCH' if products_match else 'MISMATCH'}",
        f"Top 3              : {top_status}",
        f"Mean / median      : {stats_status}",
    ]
    print("\n" + "\n".join(verification_lines))
    return verification_lines


if __name__ == "__main__":
    raw_rows = read_sales()
    clean_rows, skipped_rows = convert_rows(raw_rows)
    product_totals = revenue_by(clean_rows, "product")
    top_products = top_n(product_totals)
    high_value_rows = high_value(clean_rows, HIGH_VALUE_THRESHOLD)
    high_value_by_store = {
        store: sum(1 for row in high_value_rows if row["store"] == store)
        for store in {row["store"] for row in high_value_rows}
    }
    revenues = [row["revenue"] for row in clean_rows]
    minimum, maximum = minimum_maximum(revenues)
    results = {
        "total": total_revenue(clean_rows),
        "by_product": product_totals,
        "top_three": top_products,
        "mean": mean(revenues),
        "median": median(revenues),
    }

    report_lines = [
        "=== Sales report: September 2026 ===",
        f"Rows read          : {len(raw_rows)}",
        f"Rows used          : {len(clean_rows)}",
        f"Rows skipped       : {len(skipped_rows)}   ("
        + ", ".join(f"{row['sale_id']}: {row['reason']}" for row in skipped_rows)
        + ")",
        "",
        f"Total revenue (KES): {results['total']:,.2f}",
        "",
        "Revenue by product (KES)",
    ]
    report_lines.extend(f"  {product:<24}{amount:,.2f}" for product, amount in top_n(product_totals, len(product_totals)))
    report_lines.extend(["", "Top 3 products"])
    report_lines.extend(f"  {index}. {product} - KES {amount:,.2f}" for index, (product, amount) in enumerate(top_products, 1))
    report_lines.extend(["", f"High-value transactions (>= KES {HIGH_VALUE_THRESHOLD:,.0f}): {len(high_value_rows)}"])
    report_lines.extend(
        f"  {row['sale_id']}  {row['sale_date']}  {row['store']}  {row['product']}  KES {row['revenue']:,.2f}"
        for row in high_value_rows
    )
    report_lines.extend(["", "High-value transactions by store"])
    report_lines.extend(f"  {store}: {count}" for store, count in sorted(high_value_by_store.items()))
    report_lines.extend([
        "",
        "Transaction revenue statistics",
        f"  mean   : {results['mean']:,.2f}",
        f"  median : {results['median']:,.2f}",
        f"  min    : {minimum:,.2f}",
        f"  max    : {maximum:,.2f}",
    ])
    verification_lines = verify_with_pandas(DATA_PATH, results)
    report_lines.extend(["", *verification_lines])
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(OUTPUT_PATH)