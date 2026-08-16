# EPS CAGR Calculation Reference

EPS CAGR (Earnings Per Share Compound Annual Growth Rate) measures how fast a company's per-share earnings have grown over time. This document covers the formula, data sourcing, and every edge case.

---

## Formula

```
EPS CAGR (N years) = (EPS_current / EPS_N_years_ago)^(1/N) − 1
```

Expressed as a percentage:
```
EPS CAGR % = [(EPS_current / EPS_base)^(1/N) − 1] × 100
```

---

## Standard Timeframes

Always compute **both** for the scorecard:

| Timeframe | Formula | Label in Output |
|---|---|---|
| **5-Year (Primary)** | `(EPS_FY_now / EPS_FY-5)^(1/5) - 1` | EPS CAGR (5yr) |
| **3-Year (Secondary)** | `(EPS_FY_now / EPS_FY-3)^(1/3) - 1` | EPS CAGR (3yr) |

**Why both?**
- 5-year is more reliable — smooths anomaly years and captures a full business cycle
- 3-year shows recent momentum — useful when 5yr is anchored to a recession/COVID year
- If they diverge significantly (e.g., 5yr = 8%, 3yr = 18%), the business is accelerating — mention this

---

## Data Sources

### Indian Stocks (Groww MCP)
```
Call: fetch_stocks_fundamental_data(
  symbol = <symbol>,
  view = 'all',
  financial_items = ['eps', 'netIncome', 'sharesOutstanding']
)
```

Returns: Annual financial statements → extract `eps` for each fiscal year (FY25, FY24, FY23, FY22, FY21, FY20).

**Indian Fiscal Year mapping:**
- FY25 = April 2024 – March 2025 = current year (if after Apr 2025)
- FY20 = April 2019 – March 2020 = 5 years ago from FY25

### Global Stocks (Alpha Vantage)
```
Call: Alpha Vantage INCOME_STATEMENT(symbol = <ticker>)
```

Returns: Array of annual reports. Extract `reportedEPS` field from each year.

**Note:** Alpha Vantage free tier returns the last 5 annual reports — exactly what we need.

---

## Step-by-Step Calculation

### Step 1: Extract EPS for Required Years

For 5yr CAGR, you need:
- `EPS_current` = most recent completed fiscal year EPS
- `EPS_5yr_ago` = EPS from 5 fiscal years before current

For 3yr CAGR, you need:
- `EPS_current` = same
- `EPS_3yr_ago` = EPS from 3 fiscal years before current

**Example data (Indian company):**
| Fiscal Year | EPS (₹) |
|---|---|
| FY25 (current) | 85.40 |
| FY24 | 72.10 |
| FY23 | 58.30 |
| FY22 | 45.60 |
| FY21 | 38.20 |
| FY20 | 31.50 |

### Step 2: Compute CAGR

**5-Year CAGR (FY25 vs FY20):**
```
EPS CAGR (5yr) = (85.40 / 31.50)^(1/5) − 1
               = (2.7111)^(0.2) − 1
               = 1.2199 − 1
               = 0.2199
               = 21.99% ≈ 22.0% → 🟢 Pass
```

**3-Year CAGR (FY25 vs FY22):**
```
EPS CAGR (3yr) = (85.40 / 45.60)^(1/3) − 1
               = (1.8728)^(0.333) − 1
               = 1.2338 − 1
               = 0.2338
               = 23.38% ≈ 23.4% → 🟢 Pass
```

---

## Edge Cases

### Case 1: Company Listed < 5 Years (IPO)

**Rule:**
- If < 5 years of data: compute only 3yr CAGR (if available) or use available years
- Mark 5yr CAGR as "N/A — Listed [X] years ago"
- Use 3yr as primary for scoring

**Output example:**
```
| 4 | EPS CAGR (5yr) | N/A — IPO 2022 | > 10%  | 🟡 |
|   | EPS CAGR (3yr) | 18.4%          | > 10%  | 🟢 |
```
Score on 3yr.

---

### Case 2: Negative Base EPS (Loss in Base Year, Profit Now)

**Rule:** CAGR formula breaks when base is negative (produces non-real number). Do not compute.

**Display:**
```
EPS CAGR (5yr): N/A — Base year EPS was negative (company was loss-making in FY20)
```

**Alternative metric to show:** Absolute EPS improvement:
```
EPS improvement: From ₹-12.30 (FY20) to ₹28.50 (FY25) — turned profitable
```
Mark as 🟢 if company has clearly turned profitable with positive trajectory.

---

### Case 3: Negative Current EPS (Currently Loss-Making)

**Rule:** EPS is currently negative → company is loss-making.

**Display:**
```
EPS CAGR (5yr): N/A — Current EPS is negative (₹-8.40)
EPS CAGR (3yr): N/A — Current EPS is negative
```
Mark both as 🔴 Fail.

Also check whether EPS is improving (less negative over time) — if yes, add a note:
"EPS is improving: from ₹-22.10 (FY22) to ₹-8.40 (FY25) — on path to profitability."

---

### Case 4: Both Base and Current EPS Negative

**Rule:** Cannot compute meaningful CAGR.
- Mark as 🔴 Fail
- Show trend: "EPS deteriorating: ₹-5.2 (FY20) → ₹-14.8 (FY25)" or "EPS improving: ₹-18.5 (FY20) → ₹-4.2 (FY25)"

---

### Case 5: Base Year EPS is Zero

Rare but possible (company had no EPS or was exactly breakeven).
- Mark as 🟡 N/A
- Note: "EPS was zero in base year — CAGR undefined. Compute from the first year with non-zero EPS."
- Recompute with adjusted base year (e.g., use FY21 instead of FY20 as base).

---

### Case 6: COVID Year Anomaly

FY21 (Apr 2020 – Mar 2021) or FY22 may show distorted EPS for many companies (lockdowns).

**Rule:** If 5yr CAGR base year = FY20 or FY21 and EPS was unusually low/high due to COVID:
- Compute the standard 5yr CAGR normally
- Add a note: "*5yr CAGR base (FY20) includes COVID impact. 3yr CAGR (post-COVID) may be more representative.*"

This is informational — score normally based on the computed values.

---

### Case 7: Adjusted vs Reported EPS

Some companies report adjusted/normalised EPS excluding one-time items. When available:
- Prefer **reported (GAAP/IndAS) EPS** for consistency
- If only adjusted EPS is available, note: "*Adjusted EPS used — excludes one-time items*"

For Indian companies: use **Basic EPS** (not diluted) from audited annual results.

---

## Quick Reference

```python
# EPS CAGR computation (pseudocode)
def eps_cagr(eps_current, eps_base, years):
    if eps_base <= 0 or eps_current < 0:
        return None  # Handle as edge case above
    return ((eps_current / eps_base) ** (1 / years) - 1) * 100

# 5yr and 3yr
cagr_5yr = eps_cagr(eps_fy25, eps_fy20, 5)
cagr_3yr = eps_cagr(eps_fy25, eps_fy22, 3)
```

---

## EPS CAGR Interpretation

| CAGR | Label | Verdict |
|---|---|---|
| > 25% | 🚀 Hypergrowth | Well above benchmark |
| 15–25% | ✅ Strong Growth | Passes comfortably |
| 10–15% | ✅ Solid Growth | Passes benchmark |
| 5–10% | ⚠️ Below Benchmark | Fails — below 10% |
| 0–5% | 🔴 Stagnant | Fails |
| Negative | 🔴 Earnings Declining | Fails |
| N/A | 🟡 N/A | See edge case rules |

**Benchmark: > 10% → 🟢 Pass**

---

## Display Format in Scorecard

```
| 4 | EPS CAGR (5yr) | 22.0%  | > 10% | 🟢 |
|   | EPS CAGR (3yr) | 23.4%  | > 10% | 🟢 |
```

Both rows share metric number 4. Score based on 5yr (primary). 
If 5yr fails but 3yr passes → still 🔴 overall, but mention: "Recent acceleration (3yr CAGR 12%) suggests improving trend."
If 5yr N/A → score on 3yr as primary.
