"""
Day 1 - API Data Analysis Using Python Structures
Squad Python Specialization - Data Science, AI & Analytics
"""
import json
from pathlib import Path
import os
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.request.exceptions.RequestException as error:
        print(f"Error fetching customers: {error}")
        return []

customers = get_customers()
# print(customers)


def explore(record: dict, indent: int = 0) -> None:
    """Print every key in a (possibly nested) record with its type, indented by depth."""
    pad = "     " * indent
    if isinstance(record, dict):
        for key, value in record.items():
            print(f"{pad}{key}:{type(value).__name__}") #class <str>
            explore(value, indent + 1)
    elif isinstance(record, list):
        for i, item in enumerate(record):
            if isinstance(item, (dict, list)):
                print(f"{pad}{i}:{type(item).__name__}")
                explore(item, indent + 1)

if customers:
    explore(customers[0])

def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    rows = [
        # creating an empty list , inisde it will have many dictionaries, each dictinary has individual attributes from the jason file(a nested dictinary)
    ]
    # customers is the whole json file with (eg 500 customers), c stands for one out of the 500 customers.
    for c in customers:
        rows.append({
            'id': c['id'],
            'name': c['name'],
            "username": c["username"],
            "email": c["email"],
            "email_domain": c["email"].split("@")[-1].lower(),
            "phone": c["phone"],
            "city": c["address"]["city"],
            "zipcode": c["address"]["zipcode"],
            "latitude": float(c["address"]["geo"]["lat"]),
            "longitude": float(c["address"]["geo"]["lng"]),
            "company": c["company"]["name"],
            "website": c["website"],
        })
    return rows


result_x = extract_attributes(customers)
print(result_x)


def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {c["address"]["city"] for c in customers}

cities = unique_cities(customers)
print(cities)



def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts = {}

    for c in customers:
        city = c["address"]["city"]
        counts[city] = counts.get(city, 0) + 1

    return counts


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Return {email domain: number of customers} using a dict comprehension."""
    domains = [c["email"].split("@")[-1].lower() for c in customers]
    return {d: domains.count(d) for d in set(domains)}
      
distict_count = city_counts(customers)
distinct_email = email_domain_counts(customers)
# print_sorted(city_counts(customers), "Customers by city")
# print_sorted(email_domain_counts(customers), "Customers by email domain")
print(distict_count, "Distict customer Names")
print(distinct_email, "distict emails")


def print_sorted(counts: dict[str, int], title: str) -> None:
    """Print counts from most to least common, ties listed alphabetically."""
    print(title)
    for name, n in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {name}: {n}")


distinct_email = email_domain_counts(customers)
print(distinct_email)

def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)
pd.set_option("display.max_columns", None)
df = to_dataframe(result_x)
print(df.shape)
print(df.dtypes)
 # 2. Confirm pandas agrees with the hand-written counts
hand_cities = city_counts(customers)
hand_domains = email_domain_counts(customers)

pd_cities = df["city"].value_counts().to_dict()
pd_domains = df["email_domain"].value_counts().to_dict()

# groupby gives the same answer a second way
gb_cities = df.groupby("city").size().to_dict()

print("city_counts matches value_counts:", hand_cities == pd_cities)
print("city_counts matches groupby:     ", hand_cities == gb_cities)
print("email_domain_counts matches:     ", hand_domains == pd_domains)

# assert stops the script if they ever disagree
assert hand_cities == pd_cities == gb_cities
assert hand_domains == pd_domains

# 3. Export to CSV
out_dir = Path("output")
out_dir.mkdir(exist_ok=True)          # creates the folder if missing

# customers.csv: one row per customer
df.to_csv(out_dir / "customers.csv", index=False)

# city_counts.csv: most common first, ties alphabetical (same as print_sorted)
city_df = (
    df.groupby("city")
      .size()
      .reset_index(name="count")
      .sort_values(["count", "city"], ascending=[False, True])
)
city_df.to_csv(out_dir / "city_counts.csv", index=False)

print(f"Wrote {len(df)} rows to customers.csv and {len(city_df)} rows to city_counts.csv")


def plot_distribution(counts: dict[str, int], path: str,
                      title: str = "Distribution", xlabel: str = "Customers") -> None:
    """Save a horizontal bar chart of counts, most common first."""
    # same ordering as print_sorted: count desc, then name A-Z
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    labels = [name for name, _ in items]
    values = [n for _, n in items]

    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(labels))))
    ax.barh(labels, values, color="steelblue")
    ax.invert_yaxis()                      # largest bar at the top
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_xticks(range(0, max(values) + 1))   # counts are whole numbers

    for i, v in enumerate(values):         # label each bar with its count
        ax.text(v + 0.05, i, str(v), va="center")

    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)                         # free memory, don't show twice


# Chart 1: customers by city (required file)
plot_distribution(
    city_counts(customers),
    "output/customer_distribution.png",
    title="Customers by city",
)

# Chart 2: customers by email top-level domain
df["email_tld"] = df["email_domain"].str.rsplit(".", n=1).str[-1]
tld_counts = df["email_tld"].value_counts().to_dict()
print(tld_counts)                          # check that it actually varies

plot_distribution(
    tld_counts,
    "output/email_tld_distribution.png",
    title="Customers by email top-level domain",
)