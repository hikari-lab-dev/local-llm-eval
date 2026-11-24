#!/usr/bin/env bash
# 汎用作業（Web 調査・文書・推論・データ処理）の 4 モデル比較。結果は general/results/general1.jsonl。
set -euo pipefail
cd "$(dirname "$0")/../general"
python3 run_general.py --tag general1 --timeout 900 \
  --model qwen3.8-27b-tuned --model gemma4-31b --model gemma4-26b-a4b --model qwen3.6-35b-a3b
