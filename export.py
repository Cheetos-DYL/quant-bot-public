#!/usr/bin/env python3
"""Export 3-bot Alpaca paper leaderboard → quant-bot-public/data.json (GitHub Pages).

No Toss, no IBKR, no real accounts — Alpaca paper only. Read-only snapshot.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

PUBLIC_DIR = Path.home() / "quant-bot-public"
sys.path.insert(0, str(Path.home() / "quant-bot"))

from leaderboard import snapshot  # noqa: E402

data = {
    "leaderboard": snapshot(),
    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
(PUBLIC_DIR / "data.json").write_text(json.dumps(data, indent=2, default=str))
print("OK —", ", ".join(f"{b['name']} ${b['value']:,.2f}" for b in data["leaderboard"]))
