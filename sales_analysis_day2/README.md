# September 2026 Sales Analysis

This project reads the electronics sales export with Python's standard-library
`csv` module, cleans the numeric fields, calculates the sales report, and saves
it to `output/sales_report.txt`. Pandas is used only at the end to independently
verify the headline results.

## Run

From the project directory:

```bash
python sales_analysis.py
```

The script prints the discovered row count and CSV columns, prints the pandas
verification results, and writes the complete report to
`output/sales_report.txt`. Pandas must be installed for the verification step;
the core calculations before that step use no third-party packages.

## Cleaning rules

- Numeric values are stripped of surrounding whitespace and commas before being
	converted to `float`.
- A leading `KES` currency prefix is removed because it is an unambiguous unit
	marker. This repairs the `KES 18999` price in the source data.
- Blank values, `N/A`, and nonnumeric text such as `two` are rejected.
- Quantity and unit price must both be greater than zero. A row is skipped if
	either required value is missing, invalid, or non-positive.
- Skipped rows retain their `sale_id` and a reason in the report. Valid rows
	retain the original text columns and gain numeric quantity, unit price, and
	revenue (`quantity * unit price`) fields.

These rules skip four invalid records while safely repairing formatted numeric
prices. They are applied identically by the standard-library calculations and
the pandas verification.

## Calculations and assumptions

Revenue is grouped with ordinary dictionaries for products, stores, and payment
methods. Top products are sorted by descending revenue; equal revenues are
broken alphabetically by product name. High-value transactions use an inclusive
threshold of KES 50,000. Mean, median, minimum, and maximum are calculated from
valid per-transaction revenue values, and the custom statistical functions raise
`ValueError` for an empty list.
