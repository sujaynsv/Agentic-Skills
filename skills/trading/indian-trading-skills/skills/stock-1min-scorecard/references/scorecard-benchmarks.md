# Scorecard Benchmarks Reference

This document defines the benchmark thresholds for the 7-metric stock quality scorecard, with rationale for each.

---

## The 7 Metrics & Benchmarks

### 1. P/E Ratio — Price-to-Earnings Ratio

| Result | Condition |
|---|---|
| 🟢 Pass | P/E < 20 |
| 🔴 Fail | P/E ≥ 20 |
| 🟡 N/A | Negative EPS (loss-making) |

**Rationale:** A P/E below 20 historically represents fair-to-undervalued pricing relative to earnings power. The long-run average P/E of the S&P 500 is ~15–17x; Nifty 50 long-run average is ~20x. Threshold of 20 acts as a conservative screening filter.

**Sector Adjustments:**
- **Banking/NBFC:** P/E < 15 is ideal; < 20 is still acceptable
- **IT/Tech:** A P/E of 20–30 is common; penalize only above 35
- **FMCG/Consumer Staples:** Premium P/E (20–30) is often justified by consistent growth; note but don't fail below 30
- **Cyclicals (Metal, Auto):** P/E can be deceptively low at cycle peak; check EV/EBITDA

**Formula:** `P/E = Market Price Per Share / Earnings Per Share (TTM)`

---

### 2. ROIC — Return on Invested Capital

| Result | Condition |
|---|---|
| 🟢 Pass | ROIC > 15% |
| 🔴 Fail | ROIC ≤ 15% |
| 🟡 N/A | Negative NOPAT or Invested Capital ≤ 0 |

**Rationale:** ROIC measures how efficiently a company uses all capital (debt + equity) to generate after-tax operating profit. > 15% indicates the company earns well above its typical cost of capital (WACC ~8–12%). Warren Buffett and Charlie Munger consistently cited high ROIC as the hallmark of a quality business.

**Interpretation:**
- ROIC > 20%: Excellent — likely a moat-driven business
- ROIC 15–20%: Good — capital-efficient
- ROIC 10–15%: Average — depends on sector and growth
- ROIC < 10%: Poor — destroys shareholder value if WACC > ROIC

**Note for Financial Companies (Banks, NBFCs, Insurance):** ROIC is not standard. Use **ROE > 15%** as the primary filter and skip ROIC (set to 🟡 N/A).

**Full formula:** See `roic-calculation.md`

---

### 3. D/E Ratio — Debt to Equity

| Result | Condition |
|---|---|
| 🟢 Pass | D/E < 1 |
| 🔴 Fail | D/E ≥ 1 |
| 🟡 N/A | Financial companies (use adjusted benchmark) |

**Rationale:** D/E < 1 means the company finances itself more with equity than debt, reducing bankruptcy risk and interest burden. Companies with D/E > 2 are highly leveraged — any revenue shortfall can threaten solvency.

**Sector-Adjusted Benchmarks:**
| Sector | Benchmark | Reason |
|---|---|---|
| General | < 1 | Standard conservative filter |
| Indian Banks/NBFCs | < 8 | Leverage is core to their business model |
| US Banks | < 10 | Basel III allows higher leverage |
| Real Estate / Infrastructure | < 2 | Capital-intensive by nature |
| Capital Goods / Manufacturing | < 1.5 | Moderate leverage acceptable |

**Red Flags:**
- D/E > 3 with falling profits: debt spiral risk
- D/E > 2 with rising interest rates: interest coverage risk
- Indian stocks: also check Promoter Pledge % (see india-stock-analysis skill)

---

### 4. EPS CAGR — Earnings Per Share Compound Annual Growth Rate

| Result | Condition |
|---|---|
| 🟢 Pass | EPS CAGR > 10% (5yr primary, 3yr secondary) |
| 🔴 Fail | EPS CAGR ≤ 10% |
| 🟡 N/A | Negative base EPS, recent IPO (<3yr data) |

**Rationale:** 10% EPS CAGR is approximately the long-run nominal GDP growth rate of developed + emerging economies combined. A company growing earnings faster than 10% consistently is compounding shareholder wealth above baseline. This is Peter Lynch's core filter for growth investing.

**EPS CAGR Tiers:**
| Range | Label |
|---|---|
| > 25% | 🚀 High growth |
| 15–25% | ✅ Strong growth |
| 10–15% | ✅ Solid growth (passes) |
| 5–10% | ⚠️ Below benchmark |
| < 5% | 🔴 Stagnant |
| Negative | 🔴 Declining earnings |

**Timeframes — always report both:**
- **5-Year CAGR** (primary): more reliable, smooths out one-off years
- **3-Year CAGR** (secondary): useful for recently listed companies or to show recent acceleration/deceleration

**Full formula:** See `eps-cagr-calculation.md`

---

### 5. ROE — Return on Equity

| Result | Condition |
|---|---|
| 🟢 Pass | ROE > 15% |
| 🔴 Fail | ROE ≤ 15% |
| 🟡 N/A | Negative equity (highly indebted companies) |

**Rationale:** ROE measures how much profit a company generates per rupee/dollar of shareholder equity. > 15% indicates the business creates meaningful returns for owners. The DuPont framework breaks this into: Net Margin × Asset Turnover × Leverage.

**Important Caveat — Debt-Inflated ROE:**
High ROE (> 40%) paired with high D/E (> 2) may be misleading — the company is using debt to inflate equity returns. Always cross-check ROE against ROIC and D/E simultaneously.

**Benchmark by Sector:**
| Sector | Expected ROE |
|---|---|
| Technology / IT | > 20% |
| FMCG / Consumer | > 20% |
| Banking | 12–18% |
| Manufacturing | 12–18% |
| Infrastructure | 8–12% |

---

### 6. EBIT Margin — Earnings Before Interest & Tax Margin

| Result | Condition |
|---|---|
| 🟢 Pass | EBIT Margin > 10% |
| 🔴 Fail | EBIT Margin ≤ 10% |
| 🟡 N/A | Financial companies (use NIM substitute) |

**Rationale:** EBIT Margin shows operating profitability before financing costs and taxes. > 10% means the core business generates meaningful operating cash before capital structure effects. It's a cleaner measure of business quality than Net Margin (which varies with tax and interest).

**Benchmark by Sector:**
| Sector | Typical EBIT Margin |
|---|---|
| Software / SaaS | 20–35% |
| FMCG / Consumer | 15–25% |
| Pharma | 15–25% |
| Telecom | 10–20% |
| Manufacturing | 8–15% |
| Retail / FMCG Distribution | 5–10% |
| Airlines | 2–8% |

**Note:** If EBIT Margin is between 5–10%, add a note: "Below benchmark but sector-typical — consider sector-adjusted view."

---

### 7. Gross Margin — Gross Profit Margin

| Result | Condition |
|---|---|
| 🟢 Pass | Gross Margin > 40% |
| 🔴 Fail | Gross Margin ≤ 40% |
| 🟡 N/A | Financial companies, service companies (no COGS) |

**Rationale:** Gross Margin reveals pricing power and business model quality. > 40% indicates the company retains a significant portion of revenue after direct costs, leaving room for R&D, marketing, and operating expenses while still being profitable. Warren Buffett uses gross margin as a primary moat indicator.

**Gross Margin by Business Model:**
| Gross Margin | Interpretation |
|---|---|
| > 60% | 🏆 Strong pricing power (software, luxury, pharma) |
| 40–60% | ✅ Good margins — passes benchmark |
| 25–40% | ⚠️ Average — commodity or competitive market |
| < 25% | 🔴 Low margin — price taker or commodity business |
| < 10% | 🚫 Very low — pure distribution or commodity play |

**When to mark 🟡 N/A:**
- Banks, NBFCs, insurance companies (no COGS concept)
- Pure service companies where all costs are labour (use EBIT Margin instead)
- Trading companies / distributors (gross margin < 5% is by design)

---

## Composite Scoring Guide

| Score | Grade | Meaning |
|---|---|---|
| 7/7 | ⭐⭐⭐ Exceptional | All filters passed — rare, high-conviction quality |
| 6/7 | ⭐⭐⭐ Exceptional | Near-perfect — one minor miss |
| 5/7 | ⭐⭐ High Quality | Strong business, one or two areas to monitor |
| 4/7 | ⭐ Moderate Quality | Mixed signals — sector context matters |
| 3/7 | ⭐ Moderate Quality | More misses than passes — proceed with caution |
| 1–2/7 | ⚠️ Low Quality | Multiple red flags — high-risk investment |
| 0/7 | 🚫 Poor Quality | Avoid — fundamental quality is weak across all dimensions |

**N/A handling in scoring:** 🟡 N/A metrics are excluded from the denominator. A score of 5/6 (one metric N/A) is displayed as "5/6" not "5/7".

---

## Benchmark Sources
- Benjamin Graham: *The Intelligent Investor* (P/E < 15, D/E < 1)
- Warren Buffett: ROIC > cost of capital, Gross Margin as moat indicator
- Peter Lynch: EPS CAGR > 10% for growth investing
- Aswath Damodaran: Sector-adjusted benchmarks (NYU Stern data)
- NSE/BSE historical data: Indian market-specific adjustments
