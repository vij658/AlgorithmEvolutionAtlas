# Word Embeddings: the program

*Era 9 · topic 3 · 2013* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/03-word-embeddings/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/03-word-embeddings/word-embeddings.html) · [All era 9 programs](../README.md)

## How it works

```text
Give every word two vectors of d numbers: one for when it is the centre word (v) and one for when it is a
neighbour (u). The skip-gram model asks the centre word to predict the words around it. The full model would
compute a softmax over the whole vocabulary for every pair, which is slow; negative sampling replaces it by a
simpler question: for a real pair (centre w, neighbour c), push sigma(v_w . u_c) towards 1, and for k random
"noise" words n, push sigma(v_w . u_n) towards 0. The noise words are drawn in proportion to (count)^(3/4).
Very frequent words ("the", "is") are thrown away at random, in proportion to how frequent they are.
Nothing tells the model what a word means; words that appear in similar company end up with similar vectors,
and consistent differences in company become consistent directions: v(paris) - v(france) is nearly the same
vector as v(rome) - v(italy), so v(paris) - v(france) + v(italy) lands near v(rome).
```

## What the program does

```text
1. Writes a small corpus from sentence patterns about 8 countries, their capitals and languages, and 6 pairs of
   words that differ by gender (king and queen, ...). The patterns are known, so the program can check what the
   vectors learn; real word2vec learns from billions of words of ordinary text.
2. Checks the gradient of the negative-sampling loss against finite differences.
3. Trains skip-gram with negative sampling (d = 32, window 3, k = 5) and reports nearest neighbours.
4. Analogy tests "a is to b as c is to ?", answered by the word nearest to v(b) - v(a) + v(c): every
   country-capital, country-language and male-female combination, against random vectors.
5. The cost of a full softmax against negative sampling, per training pair.
6. Prints the vectors of the 42 content words and a two-dimensional view (principal components) for the widget.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java WordEmbeddings.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Word Embedding and Word2Vec, Clearly Explained!!!](https://www.youtube.com/watch?v=viZrOnJclY0) — StatQuest with Josh Starmer | Words to vectors, slowly and with pictures |
| Start | [Word2vec](https://en.wikipedia.org/wiki/Word2vec) — Wikipedia | The two models and the two training tricks |
| Deeper | [Stanford CS224N: NLP with Deep Learning \| Winter 2021 \| Lecture 1 - Intro & Word Vectors](https://www.youtube.com/watch?v=rmVRLeJRkl4) — Stanford Online | The first lecture of Stanford's course, on word vectors |
| Scholar | [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781) — T. Mikolov, K. Chen, G. Corrado, J. Dean (2013) | The two architectures |
| Scholar | [Distributed Representations of Words and Phrases and their Compositionality](https://ar5iv.arxiv.org/html/1310.4546) — T. Mikolov, I. Sutskever, K. Chen, G. Corrado, J. Dean (2013) | Negative sampling and subsampling |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
