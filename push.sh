#!/bin/bash
set -e
cd /home/don/quant-bot && source venv/bin/activate
python /home/don/quant-bot-public/export.py
cd /home/don/quant-bot-public
git add data.json
git diff --cached --quiet && exit 0
git commit -m "IBKR paper snapshot $(date '+%Y-%m-%d %H:%M')"
git push origin main
