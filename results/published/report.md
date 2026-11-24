# local-llm-eval report

| tag | model | lang | trials | hidden_pass | lint_pass | pass_all_k | avg_out_tokens | avg_seconds | loop_suspect | status内訳 |
|---|---|---|---|---|---|---|---|---|---|---|
| cfg27b | claude-haiku-5-5 | csharp | 40 | 40/40 (100%, 91–100%) | 40/40 (100%, 91–100%) | 8/8 | 4572 | 20.7 | 0/40 | scope_violation:2, success:38 |
| cfg27b | claude-haiku-5-5 | python | 40 | 40/40 (100%, 91–100%) | 40/40 (100%, 91–100%) | 8/8 | 5151 | 19.0 | 0/40 | success:40 |
| haiku-pilot | claude-haiku-5-5 | python | 1 | 1/1 (100%, 21–100%) | 1/1 (100%, 21–100%) | 1/1 | 1668 | 11.3 | 0/1 | success:1 |
| cfg27b | claude-haiku-5-5 | ts | 40 | 40/40 (100%, 91–100%) | 38/40 (95%, 83–99%) | 7/8 | 5891 | 20.5 | 0/40 | scope_violation:5, success:35 |
| bonsai-retest | local-llm/bonsai2-27b | csharp | 8 | 7/8 (88%, 53–98%) | 8/8 (100%, 68–100%) | 3/4 | 4023 | 87.0 | 0/8 | scope_violation:1, success:7 |
| cfg27b | local-llm/bonsai2-27b | csharp | 17 | 6/17 (35%, 17–59%) | 17/17 (100%, 82–100%) | 1/4 | 2239 | 1258.1 | 0/17 | no_change:9, success:7, timeout:1 |
| cfg27b | qwen3.8-27b | csharp | 40 | 36/40 (90%, 77–96%) | 40/40 (100%, 91–100%) | 7/8 | 3363 | 72.8 | 0/40 | scope_violation:2, success:38 |
| cfg27b | qwen3.8-27b | python | 40 | 40/40 (100%, 91–100%) | 40/40 (100%, 91–100%) | 8/8 | 4401 | 87.8 | 0/40 | success:40 |
| cfg27b | qwen3.8-27b | ts | 40 | 39/40 (98%, 87–100%) | 40/40 (100%, 91–100%) | 7/8 | 3547 | 74.2 | 0/40 | scope_violation:8, success:32 |
| cfg27b | qwen3.8-27b-alt | csharp | 40 | 37/40 (92%, 80–97%) | 40/40 (100%, 91–100%) | 6/8 | 2774 | 61.9 | 0/40 | scope_violation:1, success:39 |
| cfg27b | qwen3.8-27b-alt | python | 40 | 40/40 (100%, 91–100%) | 40/40 (100%, 91–100%) | 8/8 | 2999 | 63.8 | 0/40 | success:40 |
| cfg27b | qwen3.8-27b-alt | ts | 40 | 40/40 (100%, 91–100%) | 40/40 (100%, 91–100%) | 8/8 | 2866 | 60.8 | 0/40 | scope_violation:2, success:38 |
| cfg27b | qwen3.8-27b-tuned | csharp | 40 | 35/40 (88%, 74–95%) | 40/40 (100%, 91–100%) | 5/8 | 1369 | 39.7 | 0/40 | success:40 |
| cfg27b | qwen3.8-27b-tuned | python | 40 | 40/40 (100%, 91–100%) | 40/40 (100%, 91–100%) | 8/8 | 1707 | 42.8 | 0/40 | success:40 |
| cfg27b | qwen3.8-27b-tuned | ts | 40 | 39/40 (98%, 87–100%) | 40/40 (100%, 91–100%) | 7/8 | 1302 | 36.3 | 0/40 | success:40 |
| cfg27b | strata/qwen3.8-flash-next | csharp | 40 | 32/40 (80%, 65–90%) | 40/40 (100%, 91–100%) | 4/8 | 4671 | 210.4 | 1/40 | no_change:1, scope_violation:1, success:38 |
| cfg27b | strata/qwen3.8-flash-next | python | 40 | 40/40 (100%, 91–100%) | 40/40 (100%, 91–100%) | 8/8 | 3058 | 115.8 | 1/40 | success:40 |
| cfg27b | strata/qwen3.8-flash-next | ts | 40 | 40/40 (100%, 91–100%) | 40/40 (100%, 91–100%) | 8/8 | 3240 | 141.4 | 0/40 | scope_violation:3, success:37 |
