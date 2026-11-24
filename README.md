# local-llm-eval

ローカル LLM（llama.cpp と llama-swap で動かすモデル）とクラウドのモデルを、同じ課題・同じ採点で比べるための評価ハーネスと課題集です。
採点は人や別のモデルの判断に頼らず、隠しテストの終了コードと、正解データとの項目ごとの照合だけで行います。

## 何を測るか

| 種類 | 内容 | 採点 |
| --- | --- | --- |
| コード課題 24 問 | Python・TypeScript・C# の各 8 問。実装、バグ修正、機能追加、リファクタリング | モデルに見せない隠しテストの合否。既存テストの改変や許可外のファイルの変更も記録 |
| 事務作業と Web 調査 17 問 | 基本 10 問、難しめ 7 問。議事録の抜き出し、請求と入金の突き合わせ、Web での最新情報の調査など | 成果物を正解と項目ごとに照らし合わせ、項目数を満点とする |

公開版の事務作業は、測定に使った 18 問から 1 問（英文の翻訳）を除いた 17 問です。第三者の文章を含む可能性を否定できない課題データは、出どころを確かめられないものとして外しています。

実際のリポジトリの改修を任せる評価（実課題）も行いましたが、課題データは非公開のため含めていません。集計値だけ `results/published/` に置いています。

## 同梱物だけで動く範囲と、自分で用意が要る範囲

| 範囲 | 必要なもの | 同梱物だけで動くか |
| --- | --- | --- |
| 課題の品質チェック（`eval.py selfcheck`）、単体テスト、同梱の結果の集計 | Python、pytest、Node.js、.NET SDK | 動く |
| 事務作業と Web 調査をモデルに解かせる（`general/run_general.py`） | OpenCode、llama-swap と動かすモデル（クラウドのモデルなら `claude` CLI）。一部の Web 課題の採点に `gh` とネットワーク | 動く（実行役は不要） |
| コード課題をモデルに解かせる（`eval.py run`） | 上に加えて、後述の契約を満たす「実行役」の CLI と、必要なら採点用の lint スクリプト | 動かない。実行役は同梱していない |
| 実課題（実際のリポジトリの改修）、判定モデルの評価 | - | 含めていない |

## 必要なもの

- Python 3.11 以上（3.12 で確認）、git
- コード課題の採点: Python 課題は pytest、TypeScript 課題は Node.js 24 以上、C# 課題は .NET SDK 10
- 実際にモデルを動かすとき: llama.cpp、llama-swap、OpenCode
- クラウドのモデル（`claude-` で始まるモデル名）を動かすとき: Claude Code の CLI（`claude`）
- Web 調査の一部の採点には、GitHub CLI（`gh`）とインターネット接続が要ります（最新版を調べる課題の正解をその場で取るため）

Node.js と .NET は、PATH に無い場合は環境変数 `NODE_BIN`・`DOTNET_BIN` に実行ファイルのパスを入れます（課題の `verify` / `grade` がこれを参照します）。
TypeScript 課題の lint を使う場合は、biome 2.5.14 を導入して `CLAUDE_BIOME` にそのパスを入れます。

## 最短の動かし方

### 事務作業と Web 調査をモデルに解かせる

OpenCode から llama-swap のモデルを呼べるようにします。`examples/opencode.json` が設定の例です（provider 名 `local-llm`、モデル名は llama-swap の設定と合わせます）。

```bash
cd general
python3 run_general.py --tag mytest --model qwen3.8-27b --task minutes --task notice
python3 run_general.py --tag mytest --model qwen3.8-27b --suite hard
python3 summarize.py results/mytest.jsonl
```

環境変数で差し替えられるもの:

| 変数 | 既定 | 用途 |
| --- | --- | --- |
| `OPENCODE_BIN` | PATH 上の `opencode` | OpenCode の実行ファイル |
| `OPENCODE_PROVIDER` | `local-llm` | `opencode.json` の provider 名 |
| `LLAMA_SWAP_URL` | `http://127.0.0.1:8080/v1/chat/completions` | モデルを先に読み込む（ウォームアップ）ための要求先 |
| `EVAL_RUNS_DIR` | `~/.local-eval/general-runs` | 課題ごとの作業フォルダ |
| `GPU_LOCK_FILE` | `~/.local-eval/gpu.lock` | 同じ GPU を使う別の実行と取り合わないためのロック |

`claude-` で始まるモデル名を渡すと、OpenCode の代わりに Claude の CLI で動きます。

### モデルを動かさずに確かめる

```bash
python3 -m venv .venv
.venv/bin/pip install pytest
export PATH="$PWD/.venv/bin:$PATH"

# 課題の品質チェック: 初期状態では隠しテストが失敗し、参照解を当てると成功することを確かめる
python3 eval.py selfcheck
python3 eval.py selfcheck --tasks "python/*"

# ハーネス自体の単体テスト
python3 -m pytest -q

# 同梱の測定結果を集計する
EVAL_RESULTS_PATH=results/published/results.jsonl python3 eval.py report
```

### コード課題をモデルに解かせる（実行役が必要）

`eval.py run` は、課題の一時コピーを作ってモデルに編集させる部分を、外部の「実行役」に任せる作りです。実行役はこのリポジトリに含めていません（「含めていないもの」を参照）。次の契約を満たす CLI を用意し、`LOCAL_AGENT_SCRIPT`（または `--local-agent-script`）でパスを渡すと動きます。

```bash
export LOCAL_AGENT_SCRIPT=/path/to/local_agent.py
python3 eval.py run --models qwen3.8-27b --trials 1 --tasks python/01-interval-merge
python3 eval.py run --models qwen3.8-27b,gemma4-26b-a4b --trials 5 --tag mytag
python3 eval.py report --tag mytag
```

実行役が受け取る引数:

```text
<script> run --repo <git リポジトリ> --spec <spec.md> --verify <検証コマンド> --agent worker \
         --model <モデル名> --out <出力先> [--timeout 秒] [--lint] [--profile <設定の場所>] \
         [--editable <glob>]... [--protected <glob>]...
<script> cleanup <job_id>
```

`run` は `<出力先>/summary.json` を書きます。ハーネスが読む項目は次のとおりです。

| キー | 内容 |
| --- | --- |
| `status` | `success` / `scope_violation` / `no_change` / `verify_failed` / `timeout` / `infra_error` など |
| `worktree`, `base_commit`, `branch` | 編集後の作業ツリー、編集前のコミット、`local/<job_id>` 形式のブランチ名 |
| `attempts[]` | 試行ごとの `step_count`, `tool_call_count`, `tool_error_count`, `tool_call_leak_count` |
| `diff_stat`, `tokens`, `total_seconds` | `git diff --stat` の出力、トークン数（input / output / reasoning）、所要秒 |
| `length_stop_count`, `max_repeat_tool_streak`, `cost_usd` | ループの兆候、費用（任意） |

ハーネスは、`summary.json` の作業ツリーに `hidden_tests/` をコピーして `grade` を実行し、隠しテストの合否を決めます。
実行役が `--editable` / `--protected` の範囲外の変更を検出したら `scope_violation` として記録します。

採点用の lint は、`LINT_SCRIPT` に指定したスクリプトを `<script> --repo <作業ツリー> <変更ファイル>...` の形で呼びます（終了コード 0 が合格、2 が検証不能）。未設定なら `lint_pass` は記録されません。
`claude-` で始まるモデル名をコード課題で動かす経路は、実行役の内部関数（作業ツリーの作成など）を import して使うため、実行役がその関数を持っている必要があります。

## 課題の一覧

### コード課題

各課題は `tasks/<言語>/<課題名>/` にあり、仕様書 `spec.md`、初期状態の `repo/`、隠しテスト `hidden_tests/`、参照解 `solution/`、設定 `task.json` からなります。難しさは作成時に 5 段階で付けたものです。

| 難しさ | Python | TypeScript | C# |
| --- | --- | --- | --- |
| easy | 01-interval-merge | 01-format-duration | 01-roman-numerals |
| easy-medium | 05-parse-config | 05-parse-cookies | |
| medium | 02-fix-inventory-bug, 03-add-todo-filter | 02-fix-library-fees, 03-add-expense-filter | 02-fix-parking-fees, 03-add-ledger-budget, 05-parse-csv-line |
| medium-hard | 04-refactor-report | 04-refactor-orders | 04-refactor-shipping-fee |
| hard | 11-loyalty-tier-discount, 12-fix-region-report-cache, 13-invoice-consolidation | 11-group-size-discount, 12-fix-session-throttle, 13-leaderboard-ranking | 11-calendar-day-proration, 12-fix-reservation-cache, 13-billing-cycle-dates |

`task.json` の主な項目は次のとおりです。

- `verify`: モデルに見せる検証コマンド（`repo/` 直下で実行）
- `grade`: 採点コマンド。`hidden_tests/` をコピーしたあと同じ場所で実行
- `editable` / `protected`: 変更してよいファイルと、変えてはいけないファイル（既存テストなど）の glob
- `timeout`: 1 試行の上限秒（任意）

課題を足したら `python3 eval.py selfcheck` を実行し、「初期状態は失敗、参照解を当てると成功」を確かめます。

注意点:

- TypeScript は `package.json` も `node_modules` も置かず、Node の組み込みテストランナー（`node --test`）と型の除去だけで動かします。`enum`・`namespace`・コンストラクタのパラメータプロパティは使えません。型チェックはしません
- C# は、参照解の上書き後に古いビルド成果物が使われないよう、`verify` と `grade` の先頭で `.cs` の更新時刻を更新しています

### 事務作業と Web 調査

`general/tasks/<課題名>/` に、問題文 `prompt.md`、添付ファイル `files/`、正解 `truth.json` があります。採点の規則は `general/checks.py`（基本）と `general/checks_hard.py`（難しめ）です。

| 区分 | 課題 |
| --- | --- |
| 基本（10 問） | `minutes`（議事録から宿題を抜き出す）、`schedule`（部屋割り）、`notice`（体裁の規則つきの文書の書き直し）、`email`（予定表を見て返信を書く）、`receipts`（レシートのリネームと一覧）、`expenses`（経費の集計）、`web_gemma`、`web_release`、`web_pypi`、`web_report`（Web 調査） |
| 難しめ（7 問） | `long_minutes`（50 回分の会議記録の読解）、`reconcile`（請求と入金の消し込み）、`rehearsal`（練習計画）、`notes_index`（メモのタグ・リンク整理）、`web_multi`、`web_jp`、`web_mtp`（複数サイトにまたがる Web 調査） |

添付ファイルの一部（`make_fixtures.py`・`make_fixtures_hard.py` が生成するもの）は決定的に作り直せます。人名・会社名・店名・金額はすべて架空です。

## 採点と結果の読み方

- コード課題の `hidden_pass` は隠しテストの合否です。`lint_pass` は変更ファイルへの lint の合否で、実行役か `LINT_SCRIPT` が無いと記録されません
- `eval.py report` は、タグ・モデル・言語ごとに、合格数と 95% の信頼区間（Wilson 法）、全試行が通った課題の数（`pass_all_k`）、平均トークン数・平均秒数、ループの疑いを表にします
- `worker_status` の `scope_violation` は、変えてはいけないファイルや許可外のファイルを変更した試行です。`hidden_pass` は隠しテストだけの結果で、`scope_violation` でも隠しテストが通れば真になります。`report` の「status内訳」の列で数えます
- 事務作業と Web 調査は、`score / max` が項目単位の得点率です。`general/summarize.py` がモデルごとに合計します

同梱している測定結果（`results/published/`）:

| ファイル | 内容 |
| --- | --- |
| `results.jsonl`, `report.md` | コード課題の全試行の記録（タグ別。数値だけで、モデルの出力や作業ツリーは含まない）と、その集計 |
| `general/general1.csv`, `general/hard1.csv` | 事務作業と Web 調査の基本・難しめの、課題ごとの得点と所要秒。英文の翻訳の行は除いてあるため、基本の合計は 10 問・63 点満点になる |
| `realtask-*.csv` | 実課題の集計値（課題の中身は含まない。課題は `I01` などの通し番号） |

コード課題のタグ `cfg27b` が、モデルと設定を比べた主な測定です。`eval.py report --tag cfg27b` で同じ表を再現できます（`EVAL_RESULTS_PATH` に `results/published/results.jsonl` を指定）。

## 含めていないもの

- 実課題の課題データと実行ログ。非公開リポジトリのコードや差分を含むためです。`results/published/realtask-*.csv` に集計値だけ置いています
- 実行役（`local_agent.py` 相当）と、モデルに渡す設定の一式（規約と lint をまとめたプロファイル）。コード課題の測定には、それらを使った条件が含まれます。同じ数値を再現するには、同等のものを自分で用意する必要があります
- モデルの生の出力、1 試行ごとのログ、作業フォルダ
- 判定専用モデルの検証用データ（個人の記録や非公開コードから作ったため）
- モデルの重みと llama-swap の設定

## 測定の限界

- 課題は作者が作った小さなものです。難しめの課題でも、強いモデルは満点に近く、モデル間の差が出にくい作りです
- 事務作業と Web 調査は 1 課題 1 回の測定で、試行のばらつきは見ていません。コード課題も 1 課題あたり 5 回までです
- Web 調査のうち `web_release`・`web_pypi`・`web_multi` は、採点時に最新の情報を取りに行くため、時間が経つと正解が変わります。`web_gemma`・`web_jp` の正解は測定時点の値で固定しています。いずれも、時間が経った環境の得点は同梱の結果と比べられません
- 速度は測定した環境（GPU の VRAM 16GB 1 枚）での値で、他の環境では変わります
- `email`・`long_minutes`・`receipts`・`reconcile` は、同梱の測定結果で使った課題と、人名・会社名・店名だけが異なります。採点の規則は同じです

## 記事との対応

| 記事の数値 | 出せるか | どこから |
| --- | --- | --- |
| コード課題 24 問の得点・時間・既存テストの改変（114/120 など） | 出せる | `results/published/results.jsonl` と `report.md`（タグ `cfg27b`） |
| 事務作業と Web 調査の得点・時間 | 難しめの 7 問は出せる。基本は 1 問を除いた値になる | `results/published/general/*.csv`。基本の合計は 18 問版（67 点満点）から 63 点満点になり、記事の値とは合わない |
| 実際の改修 19 件の合否・時間・費用・差分の大きさ | 集計値のみ出せる | `results/published/realtask-refactor*.csv`。記事の合格の定義との照合は、CSV の列だけでは完結しない |
| 過去の小さな修正 2 件 | 集計値のみ出せる | `results/published/realtask-small.csv` |
| Clef の判定評価（F1、AUROC、確信度の閾値による自動判定） | 出せない | 含めていない |
| 実際の改修の本文（課題・差分・出力） | 出せない | 含めていない |
| 16GB に載せる設定、速度（tok/s）、VRAM | 出せない | 記事の記述による。ハーネスは設定を記録しない |

判定モデルの評価と実際の改修の本文は、非公開のコードとやりとりに由来するため含めていません。
