---
name: stock-1min-scorecard
description: Use when a user wants a quick stock quality check, 1-minute analysis, scorecard, or instant rating for any stock — Indian (NSE/BSE) or global. Fetches live fundamentals and scores 7 key metrics: P/E Ratio, ROIC, D/E Ratio, EPS CAGR, ROE, EBIT Margin, and Gross Margin against institutional benchmarks. Returns a structured scorecard with a pass/fail verdict per metric and a composite quality grade.
---

# Stock 1-Min Scorecard Skill

Produce a rapid 7-metric quality scorecard for any publicly listed stock — Indian or global — using live fundamental data. No API keys are required for Indian stocks. The scorecard is designed for quick investment screening, not a full recommendation.

> **Related skill:** For a deep-dive report (technical analysis, valuation bands, peer comparison, shareholding patterns), use the `india-stock-analysis` skill after running this scorecard.

---

## Data Sources by Stock Type

### Indian Stocks (NSE / BSE)
**Primary: Groww MCP** — use these tools:
- `curate_symbols` or `search_stock_and_others_symbol` — resolve ticker symbol and exchange
- `fetch_stocks_fundamental_data` with `view='stats_only'` — P/E, D/E, ROE, ROIC, margins
- `fetch_stocks_fundamental_data` with `view='all'` and `financial_items=['*']` — income statement data for Gross Margin and EPS history

**Fallback (if Groww MCP unavailable):** Use web search to find data from Screener.in, Tickertape, or MoneyControl for the same metrics.

### Global Stocks (US, Europe, Other)
**Primary: Alpha Vantage MCP** — use these tools:
- `SYMBOL_SEARCH` — resolve ticker symbol from company name
- `OVERVIEW` — P/E, EPS, ROE, D/E, Profit Margin, EBIT, Revenue, Gross Profit
- `INCOME_STATEMENT` — 5-year EPS history for CAGR calculation
- `BALANCE_SHEET` — Total Debt, Total Equity, Cash for ROIC calculation

**Fallback (if Alpha Vantage unavailable):** Use web search → Yahoo Finance or Macrotrends.

---

## Scorecard Workflow

### Step 1: Detect Stock Type and Resolve Symbol

1. Determine if the stock is **Indian** (NSE/BSE listed) or **Global** based on user input.
   - If unsure, check if the name sounds Indian or is a known Indian company → treat as Indian first.
   - If the user provides a US ticker (e.g., AAPL, MSFT, TSLA) → treat as global.

2. **For Indian stocks:** Call `curate_symbols` with the company name/ticker to get the exact NSE/BSE symbol.
3. **For global stocks:** Call Alpha Vantage `SYMBOL_SEARCH` to confirm the ticker and exchange.

4. Note the current timestamp from the system — include it in the output header.

---

### Step 2: Fetch All Fundamental Data (Parallel Calls)

**Make these calls simultaneously to save time.**

#### For Indian Stocks — call both in parallel:
```
Call A: fetch_stocks_fundamental_data(
  symbol = <resolved_symbol>,
  view = 'stats_only',
  stats = ['peRatio', 'roic', 'debtToEquity', 'epsTtm', 'returnOnEquity',
           'operatingProfitMargin', 'netProfitMargin', 'marketCap',
           'industryPe', 'sectorRoe']
)

Call B: fetch_stocks_fundamental_data(
  symbol = <resolved_symbol>,
  view = 'all',
  financial_items = ['revenue', 'grossProfit', 'ebit', 'netIncome',
                     'totalDebt', 'totalEquity', 'cash', 'eps',
                     'sharesOutstanding']
)
```

#### For Global Stocks — call both in parallel:
```
Call A: Alpha Vantage OVERVIEW(symbol = <ticker>)
  → Returns: PERatio, EPS, ReturnOnEquityTTM, DebtToEquityRatio,
             OperatingMarginTTM, GrossProfitTTM, RevenueTTM, EBITDA

Call B: Alpha Vantage INCOME_STATEMENT(symbol = <ticker>)
  → Returns: Annual reports with EPS for last 5 years

Call C: Alpha Vantage BALANCE_SHEET(symbol = <ticker>)
  → Returns: TotalAssets, TotalLiabilities, TotalShareholderEquity,
             CashAndCashEquivalentsAtCarryingValue
```

---

### Step 3: Compute the 7 Metrics

Use data from Step 2 to compute each metric. See `references/roic-calculation.md` and `references/eps-cagr-calculation.md` for detailed formulas.

#### Metric 1: P/E Ratio
```
PE = Current Market Price / EPS (TTM)
```
- **Indian:** Use `peRatio` from stats directly.
- **Global:** Use `PERatio` from OVERVIEW.
- If PE is negative (company losing money), display as `N/A (Negative EPS)`.

#### Metric 2: ROIC (Return on Invested Capital)
```
NOPAT = EBIT × (1 − Effective Tax Rate)
Invested Capital = Total Equity + Total Debt − Cash & Equivalents
ROIC = NOPAT / Invested Capital × 100
```
- **Indian:** Use `roic` stat if available directly. Otherwise compute from `ebit`, `totalDebt`, `totalEquity`, `cash`.
- **Global:** Compute from INCOME_STATEMENT + BALANCE_SHEET data.
- Effective Tax Rate: Use 25% for Indian companies (standard corporate tax), 21% for US companies. Adjust if actual rate is available.
- See `references/roic-calculation.md` for step-by-step.

#### Metric 3: D/E Ratio (Debt to Equity)
```
D/E = Total Debt / Total Shareholders' Equity
```
- **Indian:** Use `debtToEquity` stat directly.
- **Global:** Use `DebtToEquityRatio` from OVERVIEW, or compute from BALANCE_SHEET.
- For banks and NBFCs: D/E is naturally high (>1). Add a note: *"Banking/NBFC sector — D/E benchmark adjusted to < 8"* and use that threshold instead.

#### Metric 4: EPS CAGR
```
EPS CAGR (5yr) = (EPS_current / EPS_5yr_ago)^(1/5) − 1
EPS CAGR (3yr) = (EPS_current / EPS_3yr_ago)^(1/3) − 1
```
- Always compute **both** 5yr and 3yr.
- If 5yr data not available (e.g., IPO < 5 years old): use 3yr as primary and note "5yr CAGR N/A — company listed < 5 years".
- If EPS was negative in base year but positive now: flag as "Turned profitable — CAGR not meaningful".
- If EPS is negative in current year: flag as "EPS Loss — CAGR N/A".
- See `references/eps-cagr-calculation.md` for edge case handling.

#### Metric 5: ROE (Return on Equity)
```
ROE = Net Income / Total Shareholders' Equity × 100
```
- **Indian:** Use `returnOnEquity` stat directly.
- **Global:** Use `ReturnOnEquityTTM` from OVERVIEW.
- Note: Very high ROE (>50%) with high debt may indicate debt-inflated ROE — flag this if D/E > 2.

#### Metric 6: EBIT Margin
```
EBIT Margin = EBIT / Revenue × 100
```
- **Indian:** Use `operatingProfitMargin` (a close proxy). If EBIT is available directly from financials, prefer that.
- **Global:** Use `OperatingMarginTTM` from OVERVIEW.
- For financial companies (banks, NBFCs, insurance): EBIT is not standard. Use Net Interest Margin (NIM) or Pre-Tax Profit Margin as substitute and note the substitution.

#### Metric 7: Gross Margin
```
Gross Margin = (Revenue − COGS) / Revenue × 100
             = Gross Profit / Revenue × 100
```
- **Indian:** Compute from `grossProfit / revenue` using financial statement data. If grossProfit not available, derive: `grossProfit = revenue − COGS`.
- **Global:** Use `GrossProfitTTM / RevenueTTM` from OVERVIEW.
- For service companies and banks: Gross Margin is not a standard metric. Note: *"Service company — Gross Margin not applicable; EBIT Margin used as quality proxy."* Score EBIT Margin in its place.

---

### Step 4: Score Each Metric

For each metric, compare against the benchmark from `references/scorecard-benchmarks.md`:

| Metric | Benchmark | Score |
|---|---|---|
| P/E Ratio | < 20 | 🟢 Pass / 🔴 Fail |
| ROIC | > 15% | 🟢 Pass / 🔴 Fail |
| D/E Ratio | < 1 (< 8 for banks) | 🟢 Pass / 🔴 Fail |
| EPS CAGR | > 10% (5yr primary, 3yr secondary) | 🟢 Pass / 🔴 Fail |
| ROE | > 15% | 🟢 Pass / 🔴 Fail |
| EBIT Margin | > 10% | 🟢 Pass / 🔴 Fail |
| Gross Margin | > 40% | 🟢 Pass / 🔴 Fail |

Special cases → use 🟡 (Not Applicable):
- Loss-making company: P/E = 🟡 N/A, EPS CAGR = 🟡 N/A
- Banking/NBFC: Gross Margin = 🟡 N/A (substituted)
- Service company: Gross Margin = 🟡 N/A (substituted)

Composite Score: Count all 🟢 (including substituted passes). Max score = 7.

---

### Step 5: Determine Quality Grade

| Score | Grade | Label |
|---|---|---|
| 7/7 | ⭐⭐⭐ | **Exceptional Quality** |
| 5–6/7 | ⭐⭐ | **High Quality** |
| 3–4/7 | ⭐ | **Moderate Quality** |
| 1–2/7 | ⚠️ | **Low Quality — Caution** |
| 0/7 | 🚫 | **Poor Quality — Avoid** |

---

### Step 6: Generate Output

Produce the scorecard in this exact format:

```
## 📊 1-Min Scorecard: [COMPANY NAME] ([EXCHANGE]: [SYMBOL])

🕐 [Date], [Time] [TZ]  |  CMP: [Currency][Price]  |  Market Cap: [Value]

| # | Metric         | Value      | Benchmark | Result |
|---|----------------|------------|-----------|--------|
| 1 | P/E Ratio      | [value]    | < 20      | 🟢/🔴/🟡 |
| 2 | ROIC           | [value]%   | > 15%     | 🟢/🔴/🟡 |
| 3 | D/E Ratio      | [value]    | < 1       | 🟢/🔴/🟡 |
| 4 | EPS CAGR (5yr) | [value]%   | > 10%     | 🟢/🔴/🟡 |
|   | EPS CAGR (3yr) | [value]%   | > 10%     | 🟢/🔴/🟡 |
| 5 | ROE            | [value]%   | > 15%     | 🟢/🔴/🟡 |
| 6 | EBIT Margin    | [value]%   | > 10%     | 🟢/🔴/🟡 |
| 7 | Gross Margin   | [value]%   | > 40%     | 🟢/🔴/🟡 |

**Score: [X]/7 [grade emoji] — [Grade Label]**

**Strengths:** [2–3 bullet points on what passes]
**Weaknesses:** [2–3 bullet points on what fails]

**One-line verdict:** [Plain English summary — e.g., "Fairly valued, capital-efficient business with weak gross margins typical of an IT services firm."]

---
💡 *For a full investment report with technicals, peer comparison, and shareholding: say "full analysis [SYMBOL]"*
⚠️ *This scorecard is for educational purposes only and does not constitute investment advice.*
```

---

## India-Specific Adjustments

- All prices in **INR (₹)**. Market cap in **Crores (Cr)** or **Lakh Crores (L Cr)**.
- Fiscal year: **April–March** (FY25 = Apr 2024–Mar 2025).
- For EPS CAGR: use FY-end EPS figures (not calendar year).
- Promoter pledge > 20%: add a 🚩 flag note below the scorecard.
- If F&O segment stock: mention lot size.
- Market hours: 9:15 AM–3:30 PM IST. Outside hours → label data as "Previous Close / EOD".

## Global Stock Adjustments

- Currency: USD for US stocks, GBP for UK, EUR for EU, etc.
- Fiscal year: varies — Alpha Vantage OVERVIEW shows `FiscalYearEnd`.
- P/E benchmark of < 20 applies to most sectors. Tech stocks: note that a PE > 20 is common — flag but do not penalize if ROIC + EPS CAGR are strong.
- For US banks: D/E benchmark is < 10 (not < 1).

---

## Error Handling

| Error | Action |
|---|---|
| Groww MCP unavailable | Fall back to web search (Screener.in, Tickertape) for Indian stocks |
| Alpha Vantage rate limit (25/day) | Use web search → Yahoo Finance / Macrotrends for global stocks |
| Symbol not found | Ask user to confirm the NSE/BSE symbol or exact ticker |
| Insufficient historical data | Use available years, clearly note the limitation |
| All metrics N/A (e.g., startup, pre-revenue) | Inform user: "Insufficient fundamental data — scorecard cannot be generated" |
