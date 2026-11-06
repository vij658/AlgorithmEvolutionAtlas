# 102. Backpropagation and gradient descent

*Part 6 — The machinery of modern AI (entries 101–108)* · [All programs](../../README.md) · [Part 6 plan](../../../../book/principles-catalog/part-6-status-and-plan.md)

## What hurt?

To improve a model you need to know, for every one of its weights, which way to nudge it. With finite differences (nudge one weight, rerun, compare) that costs two full runs per weight. A model with a billion weights would need two billion runs for a single step of improvement. Training large networks was impossible until the derivatives could be had for the price of about one extra run.

## How it works

Make every computed number a node that remembers its inputs and the local derivative of its operation. Sort the nodes so each comes after its inputs (a topological sort, entry 36). Set the output's gradient to 1 and walk the list backwards; each node passes `its gradient × local derivative` to each input. That is the chain rule applied one operation at a time, and it is called *reverse-mode automatic differentiation*, or backpropagation.

Two details matter. When a value is used twice, its gradient is the **sum** of both uses, so gradients are added with `+=`, never assigned. And gradients must be reset to zero before each step, or each step uses the sum of all past gradients.

**Gradient descent** then moves every weight against its gradient: `w ← w − lr · ∂loss/∂w`. The learning rate decides everything: on `x²`, the update is `x ← (1 − 2·lr)·x`, which converges only for `0 < lr < 1` and lands exactly at the minimum in one step at `lr = 0.5`, which is Newton's step (entry 41).

## What the program shows

- `f = a·b + c` at `(2, −3, 10)`: f = 4 and the gradients are −3, 2, 1.
- `d(x·x)/dx` at x = 3 is 6 with `+=`, and 3 if gradients are assigned instead of added: the classic bug.
- 500 random expression graphs: backpropagation matches central finite differences to a relative 2.7e-10.
- With 1,000 inputs, one forward pass is 3,000 operations and one backward pass visits 5,001 nodes; finite differences would need 2,000 forward passes (6,000,000 operations).
- Gradient descent on `x²` for 50 steps: lr 0.1 → 1.43e-05; lr 0.5 → exactly 0; lr 0.9 → 1.43e-05 (oscillating); lr 1.0 → stuck at ±1; lr 1.1 → 9,100 (diverged).
- A 2-8-1 tanh network (33 weights) learns XOR: loss 5.389 at step 0, 0.251 at step 50, 0.0035 at step 1,000.
- Forgetting to reset gradients is not always fatal: on XOR it acted like momentum and happened to work, but on `x²` with lr 0.1 the value still swings up to |x| = 1.019 after 150 steps. A bug that sometimes works is the dangerous kind.

## Full circle

- [Entry 36, topological sort](../../part-2-paradigms-and-classics/36-topological-sort/README.md): backpropagation is a topological sort followed by one backwards sweep.
- [Entry 23, dynamic programming](../../part-2-paradigms-and-classics/23-dynamic-programming/README.md): reverse mode reuses each node's gradient for all of its inputs, the way DP reuses subproblem answers.
- [Entry 41, Newton's method](../../part-2-paradigms-and-classics/41-newtons-method/README.md): gradient descent with `lr = 1/f''` is Newton's method.

## Your turn

Do these yourself, without asking an AI to do them for you. Predict the answer on paper before you run anything.

1. Add `relu`, `log` and division to `Value`, with their backward rules, and extend the random finite-difference test to cover them.
2. Change the XOR network to 2-2-1. Does it still learn? Try five seeds. What does that tell you about initialization?
3. Implement momentum (`v ← βv + g; w ← w − lr·v`) and compare the XOR loss curve with plain gradient descent.
4. Explain on paper why forgetting to zero the gradients equals momentum with β = 1.
5. Then follow Karpathy's *micrograd* lecture and compare his Python with this Java line by line.

## Run it

```
cd code/principles/part-6-the-machinery-of-ai/102-backpropagation-and-gradient-descent
java Backpropagation.java
```

JDK 17 or newer, no build step. It prints 1515 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
f = a*b + c at (2, -3, 10): f = 4, df/da = -3, df/db = 2, df/dc = 1
d(x*x)/dx at x = 3: 6 with +=, 3 if gradients are assigned instead of added
500 random expression graphs: backpropagation matches finite differences to a relative 2.7e-10
1,000 inputs: one forward pass is 3,000 operations, one backward pass visits 5,001 nodes (the operations plus inputs and constants); central finite differences would need 2,000 forward passes (6,000,000 operations)
gradient descent on x^2 from x = 1, 50 steps: lr 0.1 -> x = 1.43e-05; lr 0.5 -> x = 0.00; lr 0.9 -> x = 1.43e-05; lr 1.0 -> x = 1.00; lr 1.1 -> x = 9.10e+03;
XOR, 2-8-1 tanh network, learning rate 0.05, loss at step 0: 5.38859; 50: 0.25096; 100: 0.07365; 200: 0.02621; 500: 0.00795; 1000: 0.00347;
without resetting gradients: XOR loss at step 1000 is 0.00000 (it acts like momentum and happens to work), but on x^2 with lr 0.1 |x| still reaches 1.019 in steps 150-199 (it never settles)
Backpropagation: 1515 checks passed
```

## References

*Citations only; links will be added and checked when the book's reference catalog reaches these topics.*

- S. Linnainmaa, *The representation of the cumulative rounding error of an algorithm as a Taylor expansion of the local rounding errors*, master's thesis, University of Helsinki, 1970 (reverse-mode differentiation).
- D. E. Rumelhart, G. E. Hinton and R. J. Williams, "Learning representations by back-propagating errors", *Nature* 323, 533–536 (1986).
- A. G. Baydin, B. A. Pearlmutter, A. A. Radul and J. M. Siskind, "Automatic differentiation in machine learning: a survey", *Journal of Machine Learning Research* 18 (2018).
- A. Karpathy, *micrograd* (a scalar autograd engine in about 100 lines of Python) and the lecture series *Neural Networks: Zero to Hero*.
