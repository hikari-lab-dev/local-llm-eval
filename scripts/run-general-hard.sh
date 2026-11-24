#!/usr/bin/env bash
# 汎用作業の難しめの課題（長文読解・消込・計画・メモ整理・複数サイト調査）の 4 モデル比較。結果は general/results/hard1.jsonl。
set -euo pipefail
cd "$(dirname "$0")/../general"
python3 run_general.py --tag hard1 --suite hard --timeout 1500 \
  --model qwen3.8-27b-tuned --model gemma4-31b --model gemma4-26b-a4b --model qwen3.6-35b-a3b
