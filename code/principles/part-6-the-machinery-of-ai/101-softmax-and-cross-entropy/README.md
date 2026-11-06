# 101. Softmax, log-sum-exp and cross-entropy

*Part 6 — The machinery of modern AI (entries 101–108)* · [All programs](../../README.md) · [Part 6 plan](../../../../book/principles-catalog/part-6-status-and-plan.md)

## What hurt?

A network ends with one raw score per possible answer (for a language model, one per token: tens of thousands). Scores are not probabilities: they can be negative and do not add up to 1. Turning them into probabilities with the textbook formula `exp(z) / Σ exp(z)` works on paper and fails in a computer: a score of 1000 makes `exp` overflow to infinity, and the answer becomes `NaN`. In 32-bit floats, which GPUs use, it already fails at 89.

## How it works

Softmax is shift-invariant: adding the same constant to every score changes nothing. So subtract the largest score first; every exponent is then ≤ 0, nothing overflows, and the largest term is exactly 1. The same trick gives *log-sum-exp*, `log Σ exp(z) = m + log Σ exp(z − m)`.

Training minimizes **cross-entropy**, the average of `−log p(correct token)`. Never compute it as `−log(softmax(z)[t])`: if that probability rounds to 0 you get infinity. Compute `logsumexp(z) − z[t]` instead; it never forms the tiny probability. Two facts make cross-entropy the natural loss: it equals entropy plus KL divergence, `H(p, q) = H(p) + KL(p‖q)`, so minimizing it pulls the model's distribution `q` towards the data's `p`; and its gradient with respect to the scores is just `softmax(z) − onehot(t)`: predicted minus actual.

**Perplexity** is `exp(cross-entropy)`: a model with perplexity 50 is as unsure as a uniform choice among 50 tokens. **Temperature** divides the scores by `T` before softmax: small `T` sharpens towards the top answer, large `T` flattens towards uniform.

## What the program shows

- `softmax([1, 2, 3]) = [0.090031, 0.244728, 0.665241]`.
- `exp(x)` overflows above x = 709.78 in double and above x = 88.72 in float.
- Logits `[1000, 0]`: the naive softmax gives `NaN`; the stable one gives `[1.0, 0.0]`. Cross-entropy when the right token is 1000 below the best: naive `Infinity`, stable exactly `1000.0`.
- On 500 random vectors the stable and naive versions agree to a relative 4.7e-15 wherever the naive one works; shifting the logits by up to ±10,000 changes nothing.
- `H(p, q) = H(p) + KL(p‖q)` and `KL ≥ 0` on 300 random pairs; the gradient `softmax − onehot` matches finite differences to 1.8e-10 on 200 random cases.
- One confident mistake is expensive: probability 0.9 on the right token costs 0.105 nats, 0.01 costs 4.605, 0.0001 costs 9.210.
- A uniform guess over 50,000 tokens: cross-entropy 10.8198 nats (15.61 bits), perplexity exactly 50,000.

## Full circle

- [Entry 16, Shannon entropy](../../part-1-distances-and-number-theory/16-shannon-entropy/README.md): cross-entropy is Shannon's entropy measured with the wrong distribution; the extra cost is the KL divergence.
- [Entry 18, Kahan summation](../../part-1-distances-and-number-theory/18-kahan-and-neumaier-summation/README.md) and [entry 19, comparing floats](../../part-1-distances-and-number-theory/19-comparing-floats-and-money/README.md): the same lesson. The formula is right; the float arithmetic needs care.
- [Entry 41, Newton's method](../../part-2-paradigms-and-classics/41-newtons-method/README.md): training is iterated improvement along a derivative; entry 102 shows how the derivative is computed.

## Your turn

Do these yourself, without asking an AI to do them for you. Predict the answer on paper before you run anything.

1. Before running: what does the naive softmax return for `[89, 0]` in `float`? In `double`? Write the float version and check.
2. Prove the shift invariance on paper in two lines. Then prove that the gradient of `logsumexp(z) − z[t]` is `softmax(z) − onehot(t)`.
3. A model's cross-entropy on a test set is 2.3 nats per token. What is its perplexity? What if it were measured in bits?
4. Write `logSoftmax(z)` returning all the log-probabilities at once, stably, and add checks for it.

## Run it

```
cd code/principles/part-6-the-machinery-of-ai/101-softmax-and-cross-entropy
java SoftmaxAndCrossEntropy.java
```

JDK 17 or newer, no build step. It prints 2121 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
softmax([1, 2, 3]) = [0.090031, 0.244728, 0.665241]
exp(x) overflows above x = 709.78 in double and x = 88.72 in float (32-bit)
logits [1000, 0]: naive softmax [NaN, 0.0], stable softmax [1.0, 0.0]
cross-entropy when the correct token's logit is 1000 below the best: naive Infinity, stable 1000.0
500 random logit vectors with sd 10: stable and naive softmax agree to a relative 4.7e-15
200 random cases: gradient softmax - onehot matches finite differences to 1.8e-10
loss for one token when the model gives the right answer probability 0.9: 0.105 nats; 0.5: 0.693 nats; 0.1: 2.303 nats; 0.01: 4.605 nats; 0.0001: 9.210 nats;
uniform guess over 50,000 tokens: cross-entropy 10.8198 nats = 15.6096 bits, perplexity 50000.0
temperature on logits [2, 1, 0.5, 0]: T=0.01 top 1.0000 entropy 0.0000; T=0.25 top 0.9793 entropy 0.1098; T=0.5 top 0.8310 entropy 0.5951; T=1.0 top 0.5793 entropy 1.1098; T=2.0 top 0.4087 entropy 1.3139; T=10.0 top 0.2790 entropy 1.3835; T=1000.0 top 0.2503 entropy 1.3863;
SoftmaxAndCrossEntropy: 2121 checks passed
```

## References

*Citations only; links will be added and checked when the book's reference catalog reaches these topics.*

- J. S. Bridle, "Probabilistic interpretation of feedforward classification network outputs, with relationships to statistical pattern recognition", in *Neurocomputing*, Springer, 1990 (the name *softmax*).
- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, MIT Press, 2016, section 4.1 (overflow, underflow and the stable softmax).
- G. Hinton, O. Vinyals and J. Dean, "Distilling the knowledge in a neural network", 2015 (temperature and soft targets).
