"""
Scorecard Engine
Detects stock type, fetches fundamentals, computes 7-metric scorecard.
Global stocks: Alpha Vantage REST API
Indian stocks: Screener.in (no-auth scrape, fallback for headless env)
"""

import asyncio
import aiohttp
import re
from datetime import datetime, timezone

ALPHA_VANTAGE_KEY = None  # Injected from config
SCREENER_BASE = "https://www.screener.in/company"

# Known Indian exchange suffixes / tickers
INDIAN_SUFFIXES = {".NS", ".BO", ".NSE", ".BSE"}
KNOWN_INDIAN_TICKERS = {
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "WIPRO", "BAJFINANCE",
    "HINDUNILVR", "KOTAKBANK", "LT", "ASIANPAINT", "MARUTI", "TITAN", "NESTLEIND",
    "ULTRACEMCO", "SUNPHARMA", "ONGC", "NTPC", "POWERGRID", "SBIN", "AXISBANK",
    "BHARTIARTL", "ITC", "M&M", "TATAMOTORS", "TATASTEEL", "HCLTECH", "TECHM",
    "DRREDDY", "CIPLA", "DIVISLAB", "BAJAJFINSV", "EICHERMOT", "GRASIM",
    "HINDALCO", "JSWSTEEL", "COALINDIA", "BPCL", "INDUSINDBK", "ADANIENT",
}

BENCHMARKS = {
    "pe":           {"threshold": 20,  "op": "lt", "label": "< 20"},
    "roic":         {"threshold": 15,  "op": "gt", "label": "> 15%"},
    "de":           {"threshold": 1,   "op": "lt", "label": "< 1"},
    "eps_cagr_5yr": {"threshold": 10,  "op": "gt", "label": "> 10%"},
    "eps_cagr_3yr": {"threshold": 10,  "op": "gt", "label": "> 10%"},
    "roe":          {"threshold": 15,  "op": "gt", "label": "> 15%"},
    "ebit_margin":  {"threshold": 10,  "op": "gt", "label": "> 10%"},
    "gross_margin": {"threshold": 40,  "op": "gt", "label": "> 40%"},
}


def detect_stock_type(ticker: str) -> str:
    """Returns 'INDIAN' or 'GLOBAL'."""
    t = ticker.upper().strip()
    for suffix in INDIAN_SUFFIXES:
        if t.endswith(suffix):
            return "INDIAN"
    if t in KNOWN_INDIAN_TICKERS:
        return "INDIAN"
    return "GLOBAL"


async def fetch_global_data(session: aiohttp.ClientSession, ticker: str) -> dict:
    """Fetch OVERVIEW + INCOME_STATEMENT + BALANCE_SHEET from Alpha Vantage."""
    base = "https://www.alphavantage.co/query"
    key = ALPHA_VANTAGE_KEY

    async def get(func):
        async with session.get(base, params={"function": func, "symbol": ticker, "apikey": key}) as r:
            return await r.json(content_type=None)

    overview, income, balance = await asyncio.gather(
        get("OVERVIEW"), get("INCOME_STATEMENT"), get("BALANCE_SHEET")
    )
    return {"overview": overview, "income": income, "balance": balance}


async def fetch_indian_data(session: aiohttp.ClientSession, ticker: str) -> dict:
    """Scrape Screener.in for fundamentals (no auth needed)."""
    url = f"{SCREENER_BASE}/{ticker}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ScorecarBot/1.0)"}
    async with session.get(url, headers=headers) as r:
        html = await r.text()
    return {"html": html, "ticker": ticker}


def _safe_float(val, default=None):
    try:
        f = float(str(val).replace(",", "").replace("%", "").strip())
        return f if f == f else default  # NaN guard
    except (TypeError, ValueError):
        return default


def compute_global_scorecard(raw: dict, ticker: str) -> dict:
    """Extract and compute all 7 metrics from Alpha Vantage data."""
    ov = raw.get("overview", {})
    inc = raw.get("income", {})
    bal = raw.get("balance", {})

    annual_income = inc.get("annualReports", [])
    annual_balance = bal.get("annualReports", [])

    # --- Metric 1: P/E ---
    pe = _safe_float(ov.get("PERatio"))

    # --- Metric 5: ROE ---
    roe = _safe_float(ov.get("ReturnOnEquityTTM"))
    if roe is not None:
        roe *= 100  # Alpha Vantage returns as decimal

    # --- Metric 6: EBIT Margin ---
    ebit_margin = _safe_float(ov.get("OperatingMarginTTM"))
    if ebit_margin is not None:
        ebit_margin *= 100

    # --- Metric 7: Gross Margin ---
    rev_ttm = _safe_float(ov.get("RevenueTTM"))
    gp_ttm = _safe_float(ov.get("GrossProfitTTM"))
    gross_margin = (gp_ttm / rev_ttm * 100) if rev_ttm and gp_ttm else None

    # --- Metrics from annual reports ---
    roic = de = eps_cagr_5yr = eps_cagr_3yr = None

    if annual_income and annual_balance:
        latest_i = annual_income[0]
        latest_b = annual_balance[0]

        ebit = _safe_float(latest_i.get("ebit") or latest_i.get("operatingIncome"))
        total_debt = _safe_float(latest_b.get("shortLongTermDebtTotal"))
        equity = _safe_float(latest_b.get("totalShareholderEquity"))
        cash = _safe_float(latest_b.get("cashAndCashEquivalentsAtCarryingValue"))

        # Metric 3: D/E
        if equity and equity != 0 and total_debt is not None:
            de = total_debt / equity

        # Metric 2: ROIC
        if ebit and equity is not None and total_debt is not None and cash is not None:
            nopat = ebit * (1 - 0.21)  # US corporate tax default
            invested_capital = equity + total_debt - cash
            if invested_capital > 0:
                roic = (nopat / invested_capital) * 100

        # Metric 4: EPS CAGR — derive from netIncome / shares
        shares = _safe_float(ov.get("SharesOutstanding"))
        if shares and shares > 0:
            eps_series = []
            for report in annual_income[:6]:  # up to 5 years back
                ni = _safe_float(report.get("netIncome"))
                if ni is not None:
                    eps_series.append(ni / shares)

            if len(eps_series) >= 2:
                eps_now = eps_series[0]
                # 5yr CAGR
                if len(eps_series) >= 6 and eps_series[5] > 0 and eps_now > 0:
                    eps_cagr_5yr = ((eps_now / eps_series[5]) ** (1 / 5) - 1) * 100
                elif len(eps_series) >= 5 and eps_series[4] > 0 and eps_now > 0:
                    eps_cagr_5yr = ((eps_now / eps_series[4]) ** (1 / 4) - 1) * 100
                # 3yr CAGR
                if len(eps_series) >= 4 and eps_series[3] > 0 and eps_now > 0:
                    eps_cagr_3yr = ((eps_now / eps_series[3]) ** (1 / 3) - 1) * 100

    # Price + cap
    price = _safe_float(ov.get("Price") or ov.get("200DayMovingAverage"))
    # Alpha Vantage OVERVIEW doesn't return live price; use 50-day as proxy label
    market_cap = _safe_float(ov.get("MarketCapitalization"))
    name = ov.get("Name", ticker)
    exchange = ov.get("Exchange", "NASDAQ")
    currency = ov.get("Currency", "USD")
    analyst_target = _safe_float(ov.get("AnalystTargetPrice"))

    # ROE debt inflation flag
    roe_flag = "🚩" if (roe is not None and roe > 50 and de is not None and de > 2) else ""

    return {
        "ticker": ticker, "name": name, "exchange": exchange, "currency": currency,
        "market_cap": market_cap, "analyst_target": analyst_target,
        "pe": pe, "roic": roic, "de": de,
        "eps_cagr_5yr": eps_cagr_5yr, "eps_cagr_3yr": eps_cagr_3yr,
        "roe": roe, "roe_flag": roe_flag,
        "ebit_margin": ebit_margin, "gross_margin": gross_margin,
        "stock_type": "GLOBAL",
    }


def _parse_screener_metric(html: str, label: str) -> float | None:
    """Simple regex scrape of a metric value from Screener.in HTML."""
    pattern = rf'{re.escape(label)}[^<]*</span>[^<]*<span[^>]*>([0-9.,%-]+)'
    m = re.search(pattern, html, re.IGNORECASE)
    if m:
        return _safe_float(m.group(1))
    return None


def compute_indian_scorecard(raw: dict) -> dict:
    """Parse Screener.in HTML for the 7 metrics."""
    html = raw.get("html", "")
    ticker = raw.get("ticker", "UNKNOWN")

    # Extract company name
    name_m = re.search(r'<h1[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)', html, re.IGNORECASE)
    name = name_m.group(1).strip() if name_m else ticker

    pe = _parse_screener_metric(html, "Stock P/E") or _parse_screener_metric(html, "P/E")
    roe = _parse_screener_metric(html, "Return on equity") or _parse_screener_metric(html, "ROE")
    de = _parse_screener_metric(html, "Debt to equity") or _parse_screener_metric(html, "D/E")
    ebit_margin = _parse_screener_metric(html, "OPM") or _parse_screener_metric(html, "Operating Profit Margin")
    gross_margin = _parse_screener_metric(html, "Gross Profit")
    roic = _parse_screener_metric(html, "ROCE")  # Screener shows ROCE, close proxy

    roe_flag = "🚩" if (roe is not None and roe > 50 and de is not None and de > 2) else ""

    return {
        "ticker": ticker, "name": name, "exchange": "NSE/BSE", "currency": "INR",
        "market_cap": None, "analyst_target": None,
        "pe": pe, "roic": roic, "de": de,
        "eps_cagr_5yr": None, "eps_cagr_3yr": None,  # Needs multi-year EPS, skipped in scrape
        "roe": roe, "roe_flag": roe_flag,
        "ebit_margin": ebit_margin, "gross_margin": gross_margin,
        "stock_type": "INDIAN",
    }


def _score(metric_key: str, value) -> str:
    if value is None:
        return "🟡"
    b = BENCHMARKS.get(metric_key)
    if not b:
        return "🟡"
    if b["op"] == "lt":
        return "🟢" if value < b["threshold"] else "🔴"
    else:
        return "🟢" if value > b["threshold"] else "🔴"


def _fmt(value, suffix="", decimals=1) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}{suffix}"


def _fmt_cap(cap) -> str:
    if cap is None:
        return "N/A"
    if cap >= 1e12:
        return f"${cap/1e12:.2f}T"
    if cap >= 1e9:
        return f"${cap/1e9:.1f}B"
    return f"${cap/1e6:.0f}M"


def format_scorecard(data: dict) -> str:
    """Format the computed scorecard as Telegram MarkdownV2-safe plain text."""
    now = datetime.now(timezone.utc).strftime("%b %d, %Y %H:%M UTC")
    cur = data.get("currency", "USD")
    sym = "$" if cur == "USD" else "₹" if cur == "INR" else cur + " "

    # Score count
    metrics = ["pe", "roic", "de", "eps_cagr_5yr", "roe", "ebit_margin", "gross_margin"]
    scores = [_score(m, data.get(m)) for m in metrics]
    green = sum(1 for s in scores if s == "🟢")
    total = sum(1 for s in scores if s != "🟡")

    if green == 7:
        grade = "⭐⭐⭐ Exceptional Quality"
    elif green >= 5:
        grade = "⭐⭐ High Quality"
    elif green >= 3:
        grade = "⭐ Moderate Quality"
    elif green >= 1:
        grade = "⚠️ Low Quality — Caution"
    else:
        grade = "🚫 Poor Quality — Avoid"

    # Analyst target
    tgt = f"{sym}{data['analyst_target']:.2f}" if data.get("analyst_target") else "N/A"
    cap = _fmt_cap(data.get("market_cap"))

    lines = [
        f"📊 *1-Min Scorecard: {data['name']} ({data['exchange']}: {data['ticker']})*",
        f"🕐 {now}  |  Cap: {cap}  |  Target: {tgt}",
        "",
        "```",
        f"{'#':<3}{'Metric':<18}{'Value':<12}{'Bench':<8}{'Result'}",
        "-" * 48,
        f"{'1':<3}{'P/E Ratio':<18}{_fmt(data.get('pe')):<12}{'<20':<8}{_score('pe', data.get('pe'))}",
        f"{'2':<3}{'ROIC':<18}{_fmt(data.get('roic'), '%'):<12}{'>15%':<8}{_score('roic', data.get('roic'))}",
        f"{'3':<3}{'D/E Ratio':<18}{_fmt(data.get('de')):<12}{'<1':<8}{_score('de', data.get('de'))}",
        f"{'4':<3}{'EPS CAGR 5yr':<18}{_fmt(data.get('eps_cagr_5yr'), '%'):<12}{'>10%':<8}{_score('eps_cagr_5yr', data.get('eps_cagr_5yr'))}",
        f"{'  ':<3}{'EPS CAGR 3yr':<18}{_fmt(data.get('eps_cagr_3yr'), '%'):<12}{'>10%':<8}{_score('eps_cagr_3yr', data.get('eps_cagr_3yr'))}",
        f"{'5':<3}{'ROE':<18}{_fmt(data.get('roe'), '%'):<12}{'>15%':<8}{_score('roe', data.get('roe'))} {data.get('roe_flag','')}",
        f"{'6':<3}{'EBIT Margin':<18}{_fmt(data.get('ebit_margin'), '%'):<12}{'>10%':<8}{_score('ebit_margin', data.get('ebit_margin'))}",
        f"{'7':<3}{'Gross Margin':<18}{_fmt(data.get('gross_margin'), '%'):<12}{'>40%':<8}{_score('gross_margin', data.get('gross_margin'))}",
        "```",
        "",
        f"*Score: {green}/{total} — {grade}*",
        "",
    ]

    # Strengths and weaknesses
    strength_map = {
        "roic": f"ROIC {_fmt(data.get('roic'), '%')} — exceptional capital efficiency",
        "gross_margin": f"Gross Margin {_fmt(data.get('gross_margin'), '%')} — strong pricing power",
        "ebit_margin": f"EBIT Margin {_fmt(data.get('ebit_margin'), '%')} — healthy operating leverage",
        "eps_cagr_5yr": f"5yr EPS CAGR {_fmt(data.get('eps_cagr_5yr'), '%')} — consistent compounder",
        "roe": f"ROE {_fmt(data.get('roe'), '%')} — strong equity returns",
        "de": f"D/E {_fmt(data.get('de'))} — low financial risk",
        "pe": f"P/E {_fmt(data.get('pe'))} — attractively priced",
    }
    weakness_map = {
        "pe": f"P/E {_fmt(data.get('pe'))} — priced for perfection",
        "de": f"D/E {_fmt(data.get('de'))} — leverage above threshold",
        "roic": f"ROIC {_fmt(data.get('roic'), '%')} — below 15% hurdle",
        "eps_cagr_5yr": f"5yr EPS CAGR {_fmt(data.get('eps_cagr_5yr'), '%')} — slow earnings growth",
        "roe": f"ROE {_fmt(data.get('roe'), '%')} — weak equity returns",
        "ebit_margin": f"EBIT Margin {_fmt(data.get('ebit_margin'), '%')} — thin operating margins",
        "gross_margin": f"Gross Margin {_fmt(data.get('gross_margin'), '%')} — below 40% threshold",
    }

    strengths = [strength_map[m] for m in metrics if _score(m, data.get(m)) == "🟢" and m in strength_map][:3]
    weaknesses = [weakness_map[m] for m in metrics if _score(m, data.get(m)) == "🔴" and m in weakness_map][:3]

    if strengths:
        lines.append("✅ *Strengths:*")
        for s in strengths:
            lines.append(f"• {s}")
        lines.append("")

    if weaknesses:
        lines.append("⚠️ *Weaknesses:*")
        for w in weaknesses:
            lines.append(f"• {w}")
        lines.append("")

    lines.append("_This scorecard is for educational purposes only. Not investment advice._")

    return "\n".join(lines)


async def run_scorecard(ticker: str, av_key: str) -> str:
    """Main entry point: detect, fetch, compute, format."""
    global ALPHA_VANTAGE_KEY
    ALPHA_VANTAGE_KEY = av_key

    stock_type = detect_stock_type(ticker)
    ticker_clean = ticker.upper().strip()

    async with aiohttp.ClientSession() as session:
        if stock_type == "INDIAN":
            raw = await fetch_indian_data(session, ticker_clean)
            data = compute_indian_scorecard(raw)
        else:
            raw = await fetch_global_data(session, ticker_clean)
            data = compute_global_scorecard(raw, ticker_clean)

    return format_scorecard(data)
