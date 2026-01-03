# IS Gap Management Tool
import pandas as pd

buckets = ["0-30 days", "31-90 days", "91-365 days", ">1 year"]
is_assets = [1200, 1400, 400, 1250] # FRM Example data
is_liabilities = [1900, 500, 500, 1350] # FRM Example data
#is_liabilities = [800, 500, 500, 1350] -- Alternative data for testing

# Building the IS Gap table with sensitivity and cumulative gap
def build_is_gap_table(buckets, is_assets, is_liabilities):

    df = pd.DataFrame({
        "IS Assets": is_assets,
        "IS Liabilities": is_liabilities
    }, index=buckets)

    df["IS Gap"] = df["IS Assets"] - df["IS Liabilities"]

    df["Sensitivity"] = df["IS Gap"].apply(
        lambda x: "Asset-sensitive" if x > 0 else
                  "Liability-sensitive" if x < 0 else
                  "Neutral"
    )

    df["Cumulative IS Gap"] = df["IS Gap"].cumsum()

    return df
print("Interest Sensitivity Gap Management Tool")


# Applying interest rate shock and compute Delta NII
def apply_rate_shock(is_gap_df, rate_shock):

    df = is_gap_df.copy()
    df["Delta NII"] = df["IS Gap"] * rate_shock
    total_delta_nii = df["Delta NII"].sum()

    return df, total_delta_nii


def generate_summary(is_gap_df, total_delta_nii, rate_shock):
    shock_bps = int(rate_shock * 10000)

    short_term = is_gap_df.iloc[0]["Sensitivity"]
    medium_term = is_gap_df.iloc[1]["Sensitivity"]  

    # Determining overall sensitivity profile
    if total_delta_nii > 0:
        overall = "Asset-sensitive overall"
    elif total_delta_nii < 0:
        overall = "Liability-sensitive overall"
    else:
        overall = "Broadly neutral overall"
    
    # Determining key driver based on short-term and medium-term gaps
    short_term_impact = is_gap_df.iloc[0]["IS Gap"] * rate_shock
    medium_term_impact = is_gap_df.iloc[1]["IS Gap"] * rate_shock

    if short_term_impact * medium_term_impact < 0:
        driver = "Short-term and medium-term repricing effects offset each other, resulting in a muted aggregate NII impact."
    else:
        driver = "Repricing effects across buckets reinforce each other, amplifying the overall NII sensitivity."

    print("\n-------------------------------")
    print("IS GAP SUMMARY (1-Year Horizon)")
    print("-------------------------------")
    print(f"Rate Shock Applied    : {shock_bps:+} bps")
    print(f"Short-term Profile    : {short_term}")
    print(f"Medium-term Profile   : {medium_term}")
    print(f"Overall ΔNII Impact   : {total_delta_nii:.2f}")
    print("\nKey Driver:")
    print(f"• {driver}")
    print("-------------------------------")


# User input for interest rate shock
user_bps = float(input("Enter interest rate shock in basis points (e.g. 100 or -100): "))
rate_shock = user_bps / 10000

# Build IS Gap table (do NOT print)
is_gap_df = build_is_gap_table(buckets, is_assets, is_liabilities)

# Apply user-defined rate shock and print final table
df_scenario, total_delta_nii = apply_rate_shock(is_gap_df, rate_shock)
print(df_scenario)

# Generate summary
generate_summary(df_scenario, total_delta_nii, rate_shock)