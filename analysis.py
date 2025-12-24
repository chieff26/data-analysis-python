import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Farm Sales Data Analysis (cleaning + stats + charts).")
    parser.add_argument("--input", default="data/farm_sales.csv", help="Path to input CSV")
    parser.add_argument("--outdir", default="outputs", help="Output folder for cleaned data and charts")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # Load
    df = pd.read_csv(args.input)

    # Basic cleaning
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "crop", "area_ha", "input_cost_tzs", "yield_kg", "price_per_kg_tzs"])

    # Remove duplicates (same date + crop + yield)
    df = df.drop_duplicates(subset=["date", "crop", "yield_kg"])

    # Feature engineering
    df["revenue_tzs"] = df["yield_kg"] * df["price_per_kg_tzs"]
    df["profit_tzs"] = df["revenue_tzs"] - df["input_cost_tzs"]
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Save cleaned data
    cleaned_path = os.path.join(args.outdir, "cleaned_farm_sales.csv")
    df.to_csv(cleaned_path, index=False)

    # Summary
    print("\n=== DATA SUMMARY ===")
    print(f"Rows: {len(df)}")
    print("\nColumns:")
    print(", ".join(df.columns))

    print("\n=== OVERALL STATS (TZS) ===")
    print(f"Total input cost: {df['input_cost_tzs'].sum():,.0f}")
    print(f"Total revenue   : {df['revenue_tzs'].sum():,.0f}")
    print(f"Total profit    : {df['profit_tzs'].sum():,.0f}")

    print("\n=== PROFIT BY CROP (TZS) ===")
    by_crop = df.groupby("crop")[["profit_tzs", "revenue_tzs", "input_cost_tzs", "yield_kg"]].sum().sort_values("profit_tzs", ascending=False)
    print(by_crop.to_string())

    # Chart 1: Profit by crop (bar)
    chart1_path = os.path.join(args.outdir, "profit_by_crop.png")
    by_crop["profit_tzs"].plot(kind="bar")
    plt.title("Profit by Crop (TZS)")
    plt.xlabel("Crop")
    plt.ylabel("Profit (TZS)")
    plt.tight_layout()
    plt.savefig(chart1_path)
    plt.close()

    # Chart 2: Monthly revenue trend (line)
    monthly = df.groupby("month")[["revenue_tzs", "profit_tzs"]].sum()
    chart2_path = os.path.join(args.outdir, "monthly_revenue_profit.png")
    monthly.plot(kind="line", marker="o")
    plt.title("Monthly Revenue & Profit (TZS)")
    plt.xlabel("Month")
    plt.ylabel("TZS")
    plt.tight_layout()
    plt.savefig(chart2_path)
    plt.close()

    # Chart 3: Yield distribution (hist)
    chart3_path = os.path.join(args.outdir, "yield_distribution.png")
    df["yield_kg"].plot(kind="hist", bins=8)
    plt.title("Yield Distribution (kg)")
    plt.xlabel("Yield (kg)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(chart3_path)
    plt.close()

    print("\n✅ Saved outputs:")
    print(f"- Cleaned data: {cleaned_path}")
    print(f"- Chart: {chart1_path}")
    print(f"- Chart: {chart2_path}")
    print(f"- Chart: {chart3_path}")

if __name__ == "__main__":
    main()
