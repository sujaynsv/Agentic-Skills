# ROIC Calculation Reference

Return on Invested Capital (ROIC) is the most important capital efficiency metric. This document explains the step-by-step calculation for both Indian and global stocks.

---

## Formula

```
ROIC = NOPAT / Invested Capital × 100

Where:
  NOPAT          = EBIT × (1 − Effective Tax Rate)
  Invested Capital = Total Equity + Total Debt − Cash & Cash Equivalents
```

---

## Step-by-Step Calculation

### Step 1: Find EBIT
```
EBIT = Operating Profit = Revenue − COGS − Operating Expenses
     = Net Income + Tax Expense + Interest Expense
```

**Where to get it:**
- Indian (Groww MCP): `fetch_stocks_fundamental_data` → financial_items → `ebit` or `operatingProfit`
- Global (Alpha Vantage): `INCOME_STATEMENT` → `ebit` field in annual report

**Fallback:** If EBIT not directly available:
```
EBIT = Revenue × EBIT Margin (if EBIT Margin known)
     = Net Income + Income Tax + Interest Expense
```

---

### Step 2: Calculate NOPAT (Net Operating Profit After Tax)
```
NOPAT = EBIT × (1 − Tax Rate)
```

**Tax Rate to use:**
| Company Type | Default Tax Rate |
|---|---|
| Indian listed company | 25.17% (standard post-2019 rate) |
| Indian company with MAT | 15% (check notes) |
| US company | 21% (post-2017 TCJA rate) |
| UK company | 25% |
| Other global | 25% (conservative estimate) |

**Best practice:** Use actual effective tax rate from income statement if available:
```
Effective Tax Rate = Income Tax Expense / Pre-Tax Income
```
Only use defaults when the actual rate is unavailable.

**Example:**
```
EBIT = ₹1,000 Cr
Tax Rate = 25%
NOPAT = ₹1,000 × (1 - 0.25) = ₹750 Cr
```

---

### Step 3: Calculate Invested Capital
```
Invested Capital = Total Equity + Total Debt − Cash & Cash Equivalents
```

**Where to get it:**
- Indian (Groww MCP): `fetch_stocks_fundamental_data` → financial_items:
  - `totalEquity` or `shareholdersEquity`
  - `totalDebt` or `longTermDebt + shortTermDebt`
  - `cash` or `cashAndEquivalents`
- Global (Alpha Vantage): `BALANCE_SHEET` → latest annual report:
  - `totalShareholderEquity`
  - `shortLongTermDebtTotal` or `longTermDebt + currentLongTermDebt`
  - `cashAndCashEquivalentsAtCarryingValue`

**Why subtract cash?**
Cash held is not "invested" in the business — it's a liquid asset that could be returned to shareholders. Subtracting it gives a cleaner picture of capital actually deployed in operations.

**Example:**
```
Total Equity = ₹5,000 Cr
Total Debt   = ₹2,000 Cr
Cash         = ₹500 Cr
Invested Capital = 5,000 + 2,000 − 500 = ₹6,500 Cr
```

---

### Step 4: Compute ROIC
```
ROIC = NOPAT / Invested Capital × 100
     = ₹750 / ₹6,500 × 100
     = 11.54%
```

---

## Complete Worked Example

**Company: Hypothetical Indian Manufacturing Co.**

| Line Item | Value |
|---|---|
| Revenue | ₹10,000 Cr |
| Operating Profit (EBIT) | ₹1,500 Cr |
| Tax Rate | 25% |
| NOPAT | ₹1,125 Cr |
| Total Equity | ₹6,000 Cr |
| Total Debt | ₹2,500 Cr |
| Cash & Equivalents | ₹800 Cr |
| Invested Capital | ₹7,700 Cr |
| **ROIC** | **14.6%** |

**Verdict:** ROIC of 14.6% is just below the 15% benchmark (🔴 Fail) — but close. Mention that it's near the threshold.

---

## Edge Cases

### When `roic` stat is directly available from Groww MCP
Prefer the pre-computed `roic` value — it's calculated from audited financial data.  
Only compute manually if:
1. The stat is missing/null
2. The value seems anomalous (e.g., > 100% or negative with profitable operations)

### Negative Invested Capital
If `Total Equity + Total Debt − Cash < 0` (e.g., company with more cash than all debt + equity, or negative equity):
- Mark ROIC as 🟡 N/A
- Note: "Negative invested capital — ROIC calculation not meaningful. Company may be asset-light or highly cash-generative."

### Financial Companies (Banks, NBFCs, Insurance)
- ROIC is **not applicable** for financial companies — their "debt" is their product (deposits, bonds).
- Mark as 🟡 N/A and use **ROE** as the capital efficiency proxy for these companies instead.
- Apply ROE benchmark > 15% in place of ROIC.

### Loss-Making Companies (Negative EBIT)
- NOPAT is negative → ROIC is negative → Mark as 🔴 Fail
- Display the negative value: e.g., `ROIC: −4.2% 🔴`
- Do not mark as N/A (negative ROIC is meaningful information)

---

## Quick Cheat Sheet

```
ROIC > 20%   → 🏆 Excellent (likely economic moat)
ROIC 15–20%  → ✅ Good (passes benchmark)
ROIC 10–15%  → ⚠️ Average (below benchmark, depends on WACC)
ROIC < 10%   → 🔴 Poor (likely destroying capital)
ROIC < 0%    → 🔴 Negative (loss-making operations)
```

**Context:** Compare ROIC against the company's WACC (Weighted Average Cost of Capital). If ROIC > WACC, the company is creating value. Typical WACC for Indian companies: 10–13%. For US companies: 7–10%.
