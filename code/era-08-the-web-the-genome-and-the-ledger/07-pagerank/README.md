# PageRank: the program

*Era 8 · topic 7 · 1998* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/07-pagerank/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/07-pagerank/pagerank.html) · [All era 8 programs](../README.md)

## How it works

```text
A page is important if important pages link to it. Write PR(u) for page u's rank; a page v with L(v) outgoing links
passes PR(v) / L(v) along each of them. With N pages and a damping factor d (0.85):
    PR(u) = (1 - d) / N + d * sum over pages v linking to u of PR(v) / L(v).
This is one equation per page, all at once. Brin and Page read it as a random surfer: at each step, with
probability d follow a random link of the current page, otherwise jump to a page chosen at random. PR(u) is the
long-run share of time spent on u. Pages without links ("dangling") send the surfer to a random page.
The power method: start with every page at 1/N and apply the right-hand side again and again. Each round shrinks
the remaining error by a factor of at most d, so at most about 150 rounds bring it below 10^-10 for d = 0.85,
however many pages there are (on a well-connected web, far fewer); each round costs one pass over the links.
Brin and Page's paper writes PR(u) = (1 - d) + d * sum ..., which is the same ranking multiplied by N.
Kleinberg's HITS gives each page two scores: a good hub links to good authorities, a good authority is linked
from good hubs; alternate the two updates and normalize.
```

## What the program does

```text
1. A made-up web of 10,000 pages that grows by preferential attachment (new pages tend to link to pages that are
   already well linked), 10% of them dangling. The power method, its rounds and its rate.
2. A web of 500 pages solved exactly by Gaussian elimination, against the power method and against a random
   surfer who takes 4,000,000 steps.
3. Rounds needed for d = 0.5, 0.85, 0.95 and 0.99.
4. A link farm: k new pages that all link to one page, and what they buy it.
5. HITS on the same 500 pages.
6. An 8-page web for the book's widget: the first rounds of the power method.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java PageRank.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [How Google Finds Your Needle in the Web's Haystack](https://www.ams.org/featurecolumn/archive/pagerank.html) — D. Austin, AMS Feature Column (2006) | The random surfer and the power method, from first principles |
| Deeper | [PageRank](https://en.wikipedia.org/wiki/PageRank) — Wikipedia | History, the normalized formula, dangling pages and convergence |
| Deeper | [HITS algorithm](https://en.wikipedia.org/wiki/HITS_algorithm) — Wikipedia | Hubs and authorities, the query-time alternative |
| Scholar | [The Anatomy of a Large-Scale Hypertextual Web Search Engine](https://www.ics.uci.edu/~djp3/classes/2008_01_01_INF141/Materials/brin1998.pdf) — S. Brin, L. Page (1998), on a UC Irvine course page | The formula, d = 0.85, and the prototype of Google |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
