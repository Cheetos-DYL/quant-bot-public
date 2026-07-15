#!/usr/bin/env python3
"""Export QuantBot state to quant-bot-public/data.json (IBKR paper)."""
import json, os, sys
from datetime import datetime
from pathlib import Path

PUBLIC_DIR = Path.home() / "quant-bot-public"
sys.path.insert(0, str(Path.home() / "quant-bot"))

os.environ.setdefault("BROKER", "ibkr")
os.environ.setdefault("BOT_MODE", "paper")

def screen_candidates():
    """Stock screen: FTNT profile — margin > 20%, P/E < 40."""
    import yfinance as yf
    tickers = ['ADBE','INTU','MA','V','META','GOOGL','MSFT','NVDA',
               'CRM','NOW','ANET','FTNT','PANW','ISRG','VRTX',
               'AMAT','KLAC','CAT','UNH','COST','AZO','ORLY',
               'HD','TJX','NKE','LOW']
    results = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            pe = info.get('trailingPE')
            margin = info.get('profitMargins')
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            if price and margin and pe and pe > 0 and pe < 40 and margin > 0.20:
                results.append({
                    "symbol": t,
                    "price": round(price, 2),
                    "pe": round(pe, 1),
                    "fwd_pe": round(info.get('forwardPE', 0) or 0, 1),
                    "peg": round(info.get('pegRatio', 0) or 0, 1),
                    "margin": round(margin * 100, 1),
                    "roe": round((info.get('returnOnEquity', 0) or 0) * 100, 0),
                    "rev_growth": round((info.get('revenueGrowth', 0) or 0) * 100, 1),
                    "beta": round(info.get('beta', 0) or 0, 1),
                })
        except Exception:
            pass
    results.sort(key=lambda x: x["margin"], reverse=True)
    return results

def main():
    if os.getenv("BROKER", "toss") == "toss":
        from exchange_toss import Exchange
    else:
        from exchange_ibkr import Exchange
    from risk import RiskManager

    try:
        e = Exchange()
        r = RiskManager()
        cash = e.get_account_balance("USD")
        pv = e.get_portfolio_value()
        pos = e.get_positions()
        stats = r.get_stats()
    except Exception as exc:
        cash, pv, pos = 0, 0, {}
        print(f"Warning: broker offline — {exc}", file=sys.stderr)
        from risk import RiskManager
        r = RiskManager()
        stats = r.get_stats()

    public_pos = {}
    for sym, p in pos.items():
        public_pos[sym] = {
            "symbol": sym,
            "qty": round(p.get("qty", 0), 0),
            "avg_entry_price": round(p.get("avg_entry_price", 0), 2),
            "market_value": round(p.get("market_value", 0), 2),
            "unrealized_plpc": round(p.get("unrealized_plpc", 0), 2),
            "currency": p.get("currency", "USD"),
        }

    data = {
        "portfolio_value": round(pv, 2),
        "cash": round(cash, 2),
        "daily_pnl": round(stats.get("daily_pnl", 0), 2),
        "total_trades": stats.get("total_trades", 0),
        "win_rate": stats.get("win_rate", 0),
        "consecutive_losses": stats.get("consecutive_losses", 0),
        "open_positions": stats.get("open_positions", 0),
        "positions": public_pos,
        "candidates": screen_candidates(),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M KST"),
    }

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    (PUBLIC_DIR / "data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"OK — portfolio ${data['portfolio_value']:,.2f}")

if __name__ == "__main__":
    main()
