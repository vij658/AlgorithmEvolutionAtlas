# Monte Carlo Tree Search and AlphaGo: the program

*Era 9 · topic 8 · 2006–2016* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/08-monte-carlo-tree-search/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/08-monte-carlo-tree-search/monte-carlo-tree-search.html) · [All era 9 programs](../README.md)

## How it works

```text
To judge a position without any knowledge of the game, play it out to the end with random moves, many times,
and count the wins. Monte Carlo tree search grows a tree of positions from such playouts. Each round has four
steps:
  selection       from the root, repeatedly choose the child with the largest UCB1 score
                    wins/visits + c * sqrt(ln(parent visits) / visits)
                  a high win rate attracts the search, and so does having been tried only a few times;
  expansion       add one untried move as a new node;
  simulation      play randomly from there to the end of the game;
  backpropagation add the result to every node on the path.
The move played is the root's most visited child. With more rounds UCT's choice converges to the best move.
AlphaGo replaced the uniform choice of new moves with a policy network's probabilities and the random playouts
partly with a value network; this program uses no networks, only a hand-written prior to show the idea.
```

## What the program does

```text
1. Solves tic-tac-toe exactly (minimax over every position) and asks UCT for a move in 600 random positions,
   with 30, 300 and 3,000 rounds: how often is its move one of the best?
2. Plays Connect Four: UCT against random moves, and UCT with 4 times as many rounds against UCT.
3. A prior that prefers central columns (a stand-in for AlphaGo's policy network) against plain UCT with the
   same number of rounds.
4. The root's visit counts and win rates in one Connect Four position, for the page.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java MonteCarloTreeSearch.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [AlphaGo - The Movie \| Full award-winning documentary](https://www.youtube.com/watch?v=WXuK6gekU1Y) — Google DeepMind | The Lee Sedol match, on DeepMind's own channel |
| Start | [AlphaGo: Mastering the ancient game of Go with Machine Learning](https://research.google/blog/alphago-mastering-the-ancient-game-of-go-with-machine-learning/) — D. Silver, D. Hassabis, Google Research blog (2016) | The announcement |
| Deeper | [Monte Carlo Tree Search](https://www.youtube.com/watch?v=UXW2yZndl7U) — John Levine | The four steps and UCT, worked on a whiteboard |
| Deeper | [Monte Carlo tree search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search) — Wikipedia | History from 1987, the four steps and UCT |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
