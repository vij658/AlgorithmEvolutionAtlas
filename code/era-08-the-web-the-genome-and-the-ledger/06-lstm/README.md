# Long Short-Term Memory: the program

*Era 8 · topic 6 · 1997* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/06-lstm/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/06-lstm/lstm.html) · [All era 8 programs](../README.md)

## How it works

```text
A recurrent network reads a sequence one step at a time and carries a hidden state h from step to step:
h_t = tanh(W [x_t, h_{t-1}] + b). Backpropagation through time sends the error back along the same chain, and at
every step it is multiplied by W and by the slope of tanh. After many steps that product has either shrunk to
nothing or blown up, so the network cannot learn that something it saw long ago matters now.
An LSTM cell keeps a separate memory c, changed only by adding: c_t = f * c_{t-1} + i * g, where g is a proposed
new value and i, f, o are gates between 0 and 1 computed from the input and the previous output: i lets new
content in, f keeps (1) or forgets (0) the old, o decides how much of tanh(c) to show as the output h. While f
stays near 1 and i near 0 the memory, and the error flowing back through it, pass unchanged: Hochreiter and
Schmidhuber's "constant error carousel". (Their 1997 cell had no forget gate, f = 1 always; the gate was added in
1999, and is used here.)
```

## What the program does

```text
1. Checks both networks' backpropagation through time against finite differences for every weight.
2. The task: a sequence of T steps; at step 0 one input carries a sign (+1 or -1), afterwards it is 0 while a second
   input carries random noise; at the last step the network must say which sign it saw. Both networks, with 4
   hidden units, are trained by Adam for T = 5, 10, 20, 40 and 80, then tested on 1,000 new sequences.
3. How much the first input still moves the final answer: the difference in the output when only the first sign
   is flipped.
4. How the error signal decays on its way back through time in the untrained networks.
5. The trained LSTM's weights for T = 30, printed for the book's widget, with one sequence's memory values.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java LongShortTermMemory.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Long Short-Term Memory (LSTM)](https://d2l.ai/chapter_recurrent-modern/lstm.html) — *Dive into Deep Learning*, section 10.1 | The gates, with equations and code |
| Deeper | [Long short-term memory](https://en.wikipedia.org/wiki/Long_short-term_memory) — Wikipedia | From the 1991 thesis to the forget gate and wide use |
| Scholar | [Long Short-Term Memory](https://papers.baulab.info/papers/Hochreiter-1997.pdf) — S. Hochreiter, J. Schmidhuber, *Neural Computation* (1997) | The constant error carousel and the long-lag experiments |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
