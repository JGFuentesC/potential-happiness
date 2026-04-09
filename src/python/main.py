import csv
import sys
from typing import List, Dict

def main():
    filepath = "../../data/samples.csv"
    data: List[Dict[str, float]] = []

    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "id": int(row["id"]),
                    "value": float(row["value"]),
                    "latency": float(row["latency"])
                })
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        sys.exit(1)

    # Descriptive Statistics
    values = [d["value"] for d in data]
    latencies = [d["latency"] for d in data]

    count = len(data)
    mean_val = sum(values) / count
    max_val = max(values)
    min_val = min(values)

    mean_lat = sum(latencies) / count
    max_lat = max(latencies)
    min_lat = min(latencies)

    print("-" * 40)
    print("Python CSV Parsing Summary")
    print("-" * 40)
    print(f"Total Records: {count}")
    print(f"{'Metric':<10} | {'Value':<10} | {'Latency':<10}")
    print("-" * 40)
    print(f"{'Mean':<10} | {mean_val:<10.2f} | {mean_lat:<10.3f}")
    print(f"{'Max':<10} | {max_val:<10.2f} | {max_lat:<10.3f}")
    print(f"{'Min':<10} | {min_val:<10.2f} | {min_lat:<10.3f}")
    print("-" * 40)

if __name__ == "__main__":
    main()
