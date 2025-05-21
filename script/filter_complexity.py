import pandas as pd
import sys

OUTPUT_CSV = "./high-low-ccn-modules.csv"

def selection(input_path):
    # Load CSV
    df = pd.read_csv(input_path)
    df.columns = ["root_dir", "project", "class", "avg_ccn", "grade", "status"]
    df["avg_ccn"] = pd.to_numeric(df["avg_ccn"], errors="coerce")

    # Remove non valid values
    df = df[(df["avg_ccn"] != 0) & (df["avg_ccn"] != 99999999)]
    df = df.dropna(subset=["avg_ccn"])

    # Calculate thresholds
    ccn_threshold_high = df["avg_ccn"].quantile(0.97)
    ccn_threshold_low = df["avg_ccn"].quantile(0.4)

    # Filter classes
    high_ccn_classes = df[df["avg_ccn"] >= ccn_threshold_high].copy()
    low_ccn_classes = df[df["avg_ccn"] <= ccn_threshold_low].sample(n=288, random_state=42).copy()

    high_ccn_classes["ccn_group"] = "High"
    low_ccn_classes["ccn_group"] = "Low"

    # Concatenate the two DataFrames
    selected_classes = pd.concat([high_ccn_classes, low_ccn_classes], ignore_index=True)
    selected_classes["module"] = selected_classes["project"].astype(str) + "/" + selected_classes["class"].astype(str)

    # Save to CSV
    selected_classes[["root_dir", "module", "avg_ccn", "ccn_group"]].to_csv(OUTPUT_CSV, index=False)
    print(f"Done. Selected modules written to: {OUTPUT_CSV}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 filter_complexity.py /path/to/complexity-results.csv")
        sys.exit(1)

    input_path = sys.argv[1]
    selection(input_path)
