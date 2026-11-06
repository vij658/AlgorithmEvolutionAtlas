# 108. The arithmetic of agents

*Part 6 — The machinery of modern AI (entries 101–108)* · [All programs](../../README.md) · [Part 6 plan](../../../../book/principles-catalog/part-6-status-and-plan.md)

## What hurt?

An agent is a model in a loop: read the conversation, choose a tool call, run it, append the result, repeat. Demos with three steps look magical. Real tasks take 20 or 200 steps, call real systems over real networks, and re-read an ever-growing history at every step. What is impressive at three steps becomes unreliable, expensive and dangerous at fifty, for reasons that are plain arithmetic.

## How it works

Five pieces of arithmetic:

1. **Errors compound.** n steps that are each right with probability p are all right with probability pⁿ: 95% per step is 36% over 20 steps.
2. **Verification is the multiplier.** A checker that catches a fraction d of bad steps, plus a retry, lifts the step success from p towards 1 − (1 − p)^attempts. Going from d = 0 to d = 0.9 matters far more than a slightly better model. This is why tests, type checkers and validators make agents work.
3. **Voting helps only with independent errors.** Taking the most common of k sampled answers (self-consistency) helps when the right answer is more common than any single wrong one, hurts when the model is usually wrong the same way, and cannot fix a shared blind spot.
4. **Tool calls are remote calls.** A timeout does not tell you whether the action happened. Retrying a payment without an idempotency key (entry 60) pays twice.
5. **Context grows quadratically.** Re-sending the whole history at each step means the total tokens read grow like n². Caching the shared prefix turns most of it into reuse; summarizing or trimming history bounds it.

## What the program shows

- pⁿ against simulation: 0.99 × 10 steps = 0.904; 0.99 × 100 = 0.366; 0.95 × 20 = 0.358; 0.9 × 20 = 0.122; 0.999 × 1,000 = 0.368.
- p = 0.9 per step, 20 steps, up to 3 attempts: the chain succeeds 0.122 with no checker, 0.338 with d = 0.5, 0.790 with d = 0.9, 0.959 with d = 0.99, at only 1.05–1.11 attempts per step.
- Binary majority vote: right 60% of the time → 0.648, 0.683, 0.753, 0.846 for k = 3, 5, 11, 25; right 40% → 0.352 … 0.154. Boyer–Moore agreed with the count in every run.
- Right 40% of the time, wrong answers spread over 5 options: plurality of 45 samples is right 0.988 of the time. With a 25% shared blind spot it stalls at 0.753 (ceiling 0.75, plus sampling noise).
- 100,000 payments over a network losing 5% of requests and 5% of responses: 1.108 attempts each; without idempotency keys 5,186 duplicate charges (5.19%; formula 0.05/0.95 = 5.26%); with keys, 0.
- Tokens read with a 5,000-token start and 1,500 new tokens per step: 117,500 for 10 steps, 2,087,500 for 50, 30,850,000 for 200, of which only 303,500 are new (102 times reuse).

## Full circle

- [Entry 60, idempotency keys](../../part-3-performance-and-distributed-systems/60-idempotency/README.md): unchanged, and more important than ever: agents retry.
- [Entry 53, retry budgets](../../part-3-performance-and-distributed-systems/53-retry-amplification-and-budgets/README.md), [entry 52, backoff and jitter](../../part-3-performance-and-distributed-systems/52-exponential-backoff-and-jitter/README.md), [entry 54, circuit breakers](../../part-3-performance-and-distributed-systems/54-circuit-breaker/README.md) and [entry 55, rate limiting](../../part-3-performance-and-distributed-systems/55-rate-limiting/README.md): a model API is a slow, rate-limited, sometimes-overloaded dependency.
- [Entry 49, tail latency and fan-out](../../part-3-performance-and-distributed-systems/49-tail-latency-and-fan-out/README.md): an orchestrator waiting on ten parallel sub-agents waits for the slowest.
- [Entry 56, cache stampede](../../part-3-performance-and-distributed-systems/56-cache-stampede/README.md): prompt and response caches have stampedes too.
- [Entry 28, Boyer–Moore majority vote](../../part-2-paradigms-and-classics/28-kadane-and-boyer-moore-majority/README.md): voting in one pass.

## Your turn

Do these yourself, without asking an AI to do them for you. Predict the answer on paper before you run anything.

1. Before running: an agent with 98% per-step success must finish 40-step tasks 90% of the time. What detection rate d, with 3 attempts, gets it there?
2. Add a checker with false alarms (it rejects a good step with probability f). Where does the benefit of checking disappear?
3. Write a real agent loop in Java against a model API, with a retry budget, a circuit breaker and idempotency keys on every side-effecting tool call. Reuse entries 52–55 and 60.
4. Measure the tokens your real agent reads per task, and how many prompt caching saves.

## Run it

```
cd code/principles/part-6-the-machinery-of-ai/108-agent-reliability
java AgentReliability.java
```

JDK 17 or newer, no build step. It prints 400048 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
all steps right: 0.99 per step x 10 steps = 0.904 (simulated 0.904); 0.99 per step x 100 steps = 0.366 (simulated 0.365); 0.95 per step x 20 steps = 0.358 (simulated 0.355); 0.9 per step x 20 steps = 0.122 (simulated 0.122); 0.999 per step x 1000 steps = 0.368 (simulated 0.365);
p = 0.9 per step, 20 steps, up to 3 attempts, checker catches a fraction d of bad steps: d=0.0: step 0.9000, chain 0.122 (simulated 0.121), 1.000 attempts per step; d=0.5: step 0.9473, chain 0.338 (simulated 0.335), 1.053 attempts per step; d=0.9: step 0.9883, chain 0.790 (simulated 0.790), 1.098 attempts per step; d=0.99: step 0.9979, chain 0.959 (simulated 0.961), 1.109 attempts per step; d=1.0: step 0.9990, chain 0.980 (simulated 0.980), 1.110 attempts per step;
majority of k samples, two possible answers: right 60% of the time: k=1 0.600; k=3 0.648; k=5 0.683; k=11 0.753; k=25 0.846; right 40% of the time: k=1 0.400; k=3 0.352; k=5 0.317; k=11 0.247; k=25 0.154;
plurality of k samples, right 40% of the time, wrong answers spread over 5 options: k=1 0.402; k=5 0.581; k=15 0.828; k=45 0.988;
same, but 25% of questions are a shared blind spot where every sample gives the same wrong answer: k=1 0.402; k=5 0.580; k=15 0.726; k=45 0.753; (ceiling 0.75, up to sampling noise)
100,000 payments over a network that loses 5% of requests and 5% of responses: 1.108 attempts each; without idempotency keys 5,186 duplicate charges (5.19%, formula 0.05/0.95 = 5.26%); with keys 0
tokens read by an agent that re-sends its history (5,000-token start, 1,500 new per step): 10 steps: 117,500 read, of which 18,500 are new (6 times reuse); 50 steps: 2,087,500 read, of which 78,500 are new (27 times reuse); 200 steps: 30,850,000 read, of which 303,500 are new (102 times reuse);
AgentReliability: 400048 checks passed
```

## References

*Citations only; links will be added and checked when the book's reference catalog reaches these topics.*

- Marquis de Condorcet, *Essai sur l'application de l'analyse à la probabilité des décisions rendues à la pluralité des voix*, 1785 (the jury theorem).
- X. Wang et al., "Self-consistency improves chain of thought reasoning in language models", ICLR 2023.
- S. Yao et al., "ReAct: synergizing reasoning and acting in language models", ICLR 2023.
- E. Schluntz and B. Zhang, "Building effective agents", Anthropic, December 2024.
- Stripe's documentation on idempotent requests (as in entry 60).
