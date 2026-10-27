# Customer Analysis

The script in `analysis.py` retrieves customer records from JSONPlaceholder,
flattens selected attributes, counts categories, exports CSV files, and saves
distribution charts in `output/`.

## Nested attributes

The customer record stores related values below these paths:

- `address.city` and `address.zipcode`
- `address.geo.lat` and `address.geo.lng`
- `company.name`

For example, the latitude is reached with `customer["address"]["geo"]["lat"]`.
The `explore` function recursively prints each key, its Python type, and its
depth so these paths can be inspected without manually guessing the structure.

## Findings

The number of unique cities is compared with the number of customers. When
those numbers are equal, every customer is in a different city, so marketing
should treat city as a poor segment for this sample and use another attribute.

The hand-written city counts are checked against pandas `value_counts()` on the
DataFrame. The exported city counts are sorted by count descending and then by
city name.

## Outputs

- `output/customers.csv` contains the requested flat customer attributes.
- `output/city_counts.csv` contains `city` and `customer_count`.
- `output/customer_distribution.png` charts customer counts by city.
- `output/email_tld_distribution.png` charts customer counts by email top-level domain.

Because each city appears once in this sample, the email-domain chart is more
useful: it groups customers into repeated categories and reveals a distribution
that city counts cannot show here.

## Run

From this directory, install the dependencies and run the script:

```bash
python -m pip install -e .
python analysis.py
```

The script requires network access to `https://jsonplaceholder.typicode.com/users`.
If the request fails, it prints an error and continues with empty results; the
CSV files are still written and empty charts are skipped safely.

## Assumptions

- Each customer has the JSONPlaceholder fields used by `extract_attributes`.
- Email domains are the text after `@`, converted to lowercase.
- Latitude and longitude are converted from API strings to floats.
