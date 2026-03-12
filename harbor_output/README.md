# cvdp_v1.0.4_agentic_code_generation_no_commercial

Converted from `full_dataset/cvdp_v1.0.4_agentic_code_generation_no_commercial.jsonl` into Harbor task format.

- Version: `1.0`
- Tasks: `92`
- Source format: `CVDP agentic JSONL`

Local Harbor usage:

```bash
harbor run \
  --registry-path /home/saketh/research/cvdp_benchmark/harbor_output/registry.local.json \
  --dataset cvdp_v1.0.4_agentic_code_generation_no_commercial@1.0 \
  --agent oracle \
  --n-concurrent 1
```

Remote registry submission:

- Fill in `registry.remote.template.json` with the final git URL and commit.
- Publish the generated task directories in a git repository.
