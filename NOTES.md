# Eval Analysis Notes — 2026-03-13

## 3-Model Eval Run (2026-03-12)

Models: GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro Preview
Agent: terminus-2, 8 concurrent trials per model

### Results

| Model              | Pass Rate | Passes | Genuine Fails | Infra Errors |
|--------------------|-----------|--------|---------------|--------------|
| Claude Opus 4.6    | 81.5%     | 75/92  | 5             | 15 (timeouts) |
| GPT-5.4            | 66.3%     | 61/92  | 18            | 15 (API errors + timeouts) |
| Gemini 3.1 Pro     | 54.3%     | 50/92  | 15            | 27 (rate limits + timeouts) |

### Issue 1: Gemini Rate Limiting

17 Gemini trials failed with `RateLimitError` — Google's API quota is 250 requests/day for gemini-3.1-pro via OpenRouter. With 8 concurrent trials this was exhausted mid-run. Gemini's true pass rate is likely higher than 54%.

### Issue 2: OpenRouter API Errors (GPT-5.4)

11 GPT-5.4 trials hit `litellm.APIError: OpenrouterException - Internal Server Error`. Backend failures on OpenRouter's side.

### Issue 3: 5 Tasks Errored on ALL Models

ethernet_mii_0006, hdbn_codec_0001, jpeg_runlength_enc_0001, phase_rotation_0015, poly_decimator_0001 — all failed across every model. Root cause is **transient infrastructure** (OpenRouter 500s, rate limits, timeouts), NOT broken tasks. Should succeed on re-run.

### Issue 4: Broken `cocotb_tools` Import in 79/92 Tasks

**This is the biggest finding.** `universal_shift_reg_0001` fails on all 3 models with reward=0.0 and no exceptions. Root cause: its `test_runner.py` imports `from cocotb_tools.runner import get_runner` — a module that doesn't exist. The correct import is `from cocotb.runner import get_runner`.

**Scope:** 79 of 92 tasks have this broken import. Only 16 tasks have the correct import. Many broken tasks still pass because the agent notices and fixes the import during execution, but this wastes agent turns and causes some tasks to fail when the agent doesn't catch it.

**Origin:** The bug is in the upstream CVDP dataset (`full_dataset/cvdp_v1.0.4_agentic_code_generation_no_commercial.jsonl`). Two different harness versions were merged:
- **Type A (16 tasks, correct):** Use `docker-compose.yml` with `build: .`, import `from cocotb.runner`
- **Type B (79 tasks, broken):** Use `docker-compose.yml` with `image: __OSS_SIM_IMAGE__`, import `from cocotb_tools.runner`

The Harbor conversion tool (`tools/convert_cvdp_to_harbor.py`) copies files verbatim, propagating the bug.

**Fix:** Add a post-processing fixup in `tools/convert_cvdp_to_harbor.py` that replaces `cocotb_tools.runner` → `cocotb.runner` in generated `environment/src/*.py` files, then regenerate `harbor_output/`.
