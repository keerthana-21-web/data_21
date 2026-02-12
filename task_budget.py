import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# STEP 1: SCRAPE 200 CRYPTO COINS (CoinGecko – Free API)
# =====================================================

url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 200,
    "page": 1,
    "sparkline": False,
    "price_change_percentage": "1h,24h,7d"
}

data = requests.get(url, params=params).json()

df = pd.DataFrame(data)[[
    "name","symbol","current_price",
    "price_change_percentage_1h_in_currency",
    "price_change_percentage_24h_in_currency",
    "price_change_percentage_7d_in_currency",
    "total_volume","market_cap","circulating_supply"
]]

df.columns = [
    "CoinName","Symbol","Price",
    "Change_1h","Change_24h","Change_7d",
    "Volume24h","MarketCap","CirculatingSupply"
]

print("✅ Data Loaded :", len(df), "Coins")

# =====================================================
# COMMON CALCULATIONS
# =====================================================

# Price Range (Slicer logic)
def price_range(p):
    if 0 <= p < 0.05: return "0-0.05"
    elif p < 0.5: return "0.05-0.5"
    elif p < 5: return "0.5-5"
    elif p < 50: return "5-50"
    else: return ">50"

df["PriceRange"] = df["Price"].apply(price_range)

# Average Downfall %
df["Avg_Downfall"] = df[["Change_1h","Change_24h","Change_7d"]].abs().mean(axis=1)

# Previous prices
df["Prev_1h"]  = df["Price"] / (1 + df["Change_1h"]/100)
df["Prev_24h"] = df["Price"] / (1 - df["Change_24h"]/100)
df["Prev_7d"]  = df["Price"] / (1 + df["Change_7d"]/100)

# =====================================================
# TASK 1: KPI – LOW BUDGET MAX PROFIT
# =====================================================

selected_range = "0.5-5"   # slicer simulation
filt = df[df["PriceRange"] == selected_range]

best = filt.sort_values("Avg_Downfall").iloc[0]

print("\n--- TASK 1 KPI ---")
print("Coin Name :", best["CoinName"])
print("Symbol    :", best["Symbol"])
print("Price     :", best["Price"])
print("Avg Downfall % :", round(best["Avg_Downfall"],2))
print("Total Coins Selected :", len(filt))

# =====================================================
# TASK 2: TOP 10 (0–5$) – 7D vs 24H PRICE CHART
# =====================================================

range_0_5 = df[(df["Price"]>=0) & (df["Price"]<=5)]
top10_1h  = range_0_5.sort_values("Prev_1h", ascending=False).head(10)

plt.figure(figsize=(12,6))
plt.bar(top10_1h["CoinName"], top10_1h["Prev_7d"], label="7 Days Before")
plt.bar(top10_1h["CoinName"], top10_1h["Prev_24h"],
        bottom=top10_1h["Prev_7d"], label="24 Hours Before")
plt.xticks(rotation=45)
plt.title("Top 10 Coins (0–5$) – Historical Prices")
plt.legend()
plt.show()

# =====================================================
# TASK 3: PRICE INCREASE – TOP 10 (1 HOUR)
# =====================================================

df["PriceChange_1h"] = df["Price"] - df["Prev_1h"]
df["PriceCategory"] = np.where(df["Price"]>=10, ">=10", "<10")

selected_cat = "<10"
top10_change = df[df["PriceCategory"]==selected_cat] \
               .sort_values("PriceChange_1h", ascending=False) \
               .head(10)

plt.figure(figsize=(10,6))
plt.plot(top10_change["CoinName"], top10_change["Price"],
         marker='o', label="Current Price")
plt.plot(top10_change["CoinName"], top10_change["Prev_1h"],
         marker='o', label="1 Hour Before")
plt.xticks(rotation=45)
plt.title("Top 10 Coins – 1 Hour Price Change")
plt.legend()
plt.show()

print("\n--- PRICE CHANGE TABLE ---")
print(top10_change[["Symbol","PriceChange_1h"]])

# =====================================================
# TASK 4: VOWELS + B C D COINS – LIQUIDITY
# =====================================================

df["AllowedCoins"] = df["CoinName"].str.upper().str.startswith(
    tuple("AEIOUBCD")
)

allowed = df[df["AllowedCoins"]]
top10_liq = allowed.sort_values("Volume24h", ascending=False).head(10)

plt.figure(figsize=(10,6))
plt.bar(top10_liq["CoinName"], top10_liq["Volume24h"])
plt.xticks(rotation=45)
plt.title("Top 10 Liquidity Coins (Volume 24h)")
plt.show()

# =====================================================
# TASK 5: COIN COMPARISON
# =====================================================

def compare_coins(c1, c2):
    a = df[df["CoinName"].str.lower()==c1.lower()].iloc[0]
    b = df[df["CoinName"].str.lower()==c2.lower()].iloc[0]

    print("\n--- COIN COMPARISON ---")
    print("\n",a["CoinName"])
    print(a[["Symbol","Price","Volume24h","MarketCap","CirculatingSupply"]])
    print("\n",b["CoinName"])
    print(b[["Symbol","Price","Volume24h","MarketCap","CirculatingSupply"]])

    print("\n--- KPI DIFFERENCE ---")
    print("Volume Diff :", abs(a["Volume24h"]-b["Volume24h"]))
    print("MarketCap Diff :", abs(a["MarketCap"]-b["MarketCap"]))
    print("Circulating Supply Diff :", abs(a["CirculatingSupply"]-b["CirculatingSupply"]))

compare_coins("bitcoin","ethereum")

# =====================================================
# TASK 6: LIQUIDITY PIE – TOP 5 + OTHERS
# =====================================================

price_filt = df[df["Price"]<=50]
top5 = price_filt.sort_values("Volume24h", ascending=False).head(5)

others = price_filt["Volume24h"].sum() - top5["Volume24h"].sum()

labels = list(top5["CoinName"]) + ["Others"]
sizes  = list(top5["Volume24h"]) + [others]

plt.figure(figsize=(8,8))
plt.pie(sizes, labels=labels, autopct="%1.1f%%")
plt.title("Liquidity Distribution (Volume 24h)")
plt.show()
