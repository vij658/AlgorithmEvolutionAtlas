# Part 6 — The machinery of modern AI: status and plan

*Companion volume, Part 6 (entries 101–108).* Eight programs are written and verified; **the page text is not written yet.** Each entry's folder has a README with the pain that forced the idea, how it works, what the program shows, links back to earlier entries, exercises, and sources.

Entries are numbered from 101 so that Parts 4 and 5 can still take 63–100. Renumber freely when those parts are planned.

## Why this part exists

The book's timeline ends with "transformers and the algorithms of 2026". Most explanations of that era start from Python libraries, which hide the parts that matter. This part rebuilds those parts from nothing, in the same single-file Java style as Parts 1–3, so every claim can be run and every number comes from a program's output. It is also the bridge from the earlier parts: almost every idea here is an older entry used in a new place.

| Piece | Entries | State | Checks passed |
|---|---|---|---|
| Part 6: the machinery of modern AI | 101–108 | **Programs verified; page not written** | 422,233 |

Counts are from runs on OpenJDK 21.0.12 (`java File.java`, exit status 0 for every program).

## The entries

| # | Entry | Headline result from the program's output |
|---|---|---|
| [101](../../code/principles/part-6-the-machinery-of-ai/101-softmax-and-cross-entropy/README.md) | Softmax, log-sum-exp and cross-entropy | Naive softmax of `[1000, 0]` is `NaN`, stable is `[1, 0]`; exp overflows above 88.72 in float; the gradient `softmax − onehot` matches finite differences to 1.8e-10 |
| [102](../../code/principles/part-6-the-machinery-of-ai/102-backpropagation-and-gradient-descent/README.md) | Backpropagation and gradient descent | 1,000 inputs: one backward pass against 2,000 forward passes for finite differences; a 33-weight network learns XOR (loss 5.389 → 0.0035) |
| [103](../../code/principles/part-6-the-machinery-of-ai/103-byte-pair-encoding/README.md) | Byte-pair encoding | `" strawberry"` is 1 token, `" STRAWBERRY"` 10; the same sentence costs 9 tokens in English and 80 in Hindi with an English-trained tokenizer |
| [104](../../code/principles/part-6-the-machinery-of-ai/104-attention-and-the-kv-cache/README.md) | Attention, the causal mask and the KV cache | The cache is bit-for-bit equal to recomputation and 11.9 times cheaper at 24 tokens; 4 GiB of cache per 8,192-token conversation, 1 GiB with grouped-query attention |
| [105](../../code/principles/part-6-the-machinery-of-ai/105-sampling-and-decoding/README.md) | Greedy, temperature, top-k, top-p, beam search | The same 4,096 numbers summed in two orders differ in 1,964 of 2,000 trials (why "temperature 0" still varies); greedy finds the most likely sequence in 128 of 300 toy models, beam 8 in 293 |
| [106](../../code/principles/part-6-the-machinery-of-ai/106-vector-search/README.md) | Vector search: exact, IVF, SimHash | IVF recall@10 is 0.977 for 8.8% of the work; P(hyperplane splits) = θ/π checked from 10° to 170° |
| [107](../../code/principles/part-6-the-machinery-of-ai/107-eval-statistics/README.md) | Eval statistics: Wilson, McNemar, pass@k | On 1,000 shared questions a paired test detects 80% vs 82% in 80.6% of evals; separate question sets of 1,000 each would detect it in about 21% |
| [108](../../code/principles/part-6-the-machinery-of-ai/108-agent-reliability/README.md) | The arithmetic of agents | 0.9 per step over 20 steps is 0.122; a checker catching 90% of bad steps lifts it to 0.790; without idempotency keys 5.19% of retried payments are duplicated |

## The bridge: Part 3 is the operations manual for LLM systems

A model API is a slow, expensive, rate-limited, sometimes-overloaded remote dependency whose answers are random. Every entry of Part 3 has a direct job in a system built on one.

| Part 3 entry | Where it shows up in an LLM system |
|---|---|
| 45 Little's law, 46 queueing delay | Concurrent requests = arrival rate × generation time; GPU servers batch requests, and latency explodes near full utilization |
| 47 Zipf and cache sizing, 48 LRU | Prompt caches, response caches and KV-cache eviction under memory pressure |
| 49 Tail latency and fan-out | An orchestrator waiting on ten parallel sub-agents or retrieval calls waits for the slowest |
| 50 Percentiles | Time to first token and time per output token are distributions; report p50/p99, not averages |
| 51 Power of two choices | Routing requests across model replicas by picking the less loaded of two |
| 52 Backoff and jitter, 53 retry budgets | HTTP 429 and overload responses from model APIs; a retry storm from many agents can keep a provider overloaded |
| 54 Circuit breaker | Falling back to another model or a cached answer when a provider is down |
| 55 Rate limiting | Limits are in requests *and* tokens per minute; a token bucket that charges by tokens |
| 56 Cache stampede | A popular prompt expiring from a cache while a thousand users ask for it |
| 60 Idempotency | Agents retry tool calls after timeouts; every side-effecting tool needs a key (entry 108) |
| 39 Consistent hashing | Sending each conversation to the replica that already holds its KV cache |

## What is left for Part 6

1. Write the page text in the style of Parts 1 and 2, then build it with the [page builder](../../code/tools/README.md).
2. Planned entries (not yet written):
   - **109 A tiny GPT, end to end:** combine 101–105 into a character-level transformer trained in Java on a small text, with a loss curve and sampled text.
   - **110 Speculative decoding:** a small model drafts, the large model verifies; check that the accept/reject rule leaves the output distribution exactly unchanged.
   - **111 Quantization:** int8 and int4 weights, measured error in logits and in cross-entropy; why outliers break naive scaling.
   - **112 Low-rank adaptation (LoRA) and the SVD:** fine-tuning by training a rank-r update; the parameter count and what rank r can and cannot represent.
   - **113 Rotary position embeddings:** relative position from rotations; the permutation check of entry 104 now fails, as it should.
   - **114 Continuous batching:** a queueing simulation of an LLM server (entries 45–46) with prefill and decode phases; throughput against latency.
   - **115 MinHash deduplication of training data:** entry 7's Jaccard index, estimated at scale.
   - **116 Prompt injection as a confused-deputy problem:** an agent that reads untrusted text and holds tools; least privilege and allowlists as the fix (a bridge to Part 4, security).
3. References: every source is cited by title and year; links will be added and checked when the book's reference catalog reaches these topics.
