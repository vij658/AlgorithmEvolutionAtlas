# Era 9 — Learning at Scale

*2009 to 2026* · [Book contents](../README.md) · [Interactive edition](index.html) · [Reference catalog](reference-catalog.md) · [Programs](../../code/era-09-learning-at-scale/README.md)

> **Field note from the visiting historian.** In the eighth era, the species built a Web, read its genome and agreed on a ledger. In this one an old idea, the network that learns from examples, suddenly works at scale, and much of the era's algorithmic work goes into making that learning possible; alongside it the species learns to compute on data it cannot read, prepares its cryptography for quantum computers, and sets its machines to search for algorithms.

## When

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/era-timeline-dark.svg">
  <img src="assets/era-timeline-light.svg" alt="Era 9: Learning at Scale, from 2009 to 2026">
</picture>

## How the ideas combined

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/era-map-dark.svg">
  <img src="assets/era-map-light.svg" alt="How the ideas of Era 9 combined: Learning at Scale">
</picture>

*Dashed lines join related developments; none of them is a claim that one inventor learned from the other. Most boxes build on earlier eras: homomorphic encryption and ML-KEM on public-key cryptography (Era 6) and learning with errors; AlexNet, Adam and residual networks on backpropagation (Era 7) and the LSTM (Era 8); word vectors on Huffman's codes (Era 5) for their hierarchical softmax; Raft on Paxos (Era 8); byte-pair encoding on universal compression (Era 6); Monte Carlo tree search on Monte Carlo (Era 4); diffusion models on Markov chains (Era 4); the search for matrix multiplication algorithms on Strassen (Era 6).*

## The topics

| # | Topic | When | What hurt | Read |
|---|---|---|---|---|
| 1 | **Fully Homomorphic Encryption** | 2009; over the integers 2010 | Encrypted data had to be decrypted before anyone could compute with it | [page](01-homomorphic-encryption/README.md) · [interactive](01-homomorphic-encryption/homomorphic-encryption.html) · [program](../../code/era-09-learning-at-scale/01-homomorphic-encryption/README.md) |
| 2 | **Deep Convolutional Networks** | September 2012 | Hand-made image features had stalled; deep networks were too slow to train | planned · [references](reference-catalog.md#2-deep-convolutional-networks) |
| 3 | **Word Embeddings** | January and October 2013 | Words were symbols with no notion of likeness | planned · [references](reference-catalog.md#3-word-embeddings) |
| 4 | **Raft** | 2014 | Paxos was correct but hard to understand and to build | planned · [references](reference-catalog.md#4-raft) |
| 5 | **Adam** | December 2014 | One learning rate for millions of very different parameters | planned · [references](reference-catalog.md#5-adam) |
| 6 | **Byte-Pair Encoding for Words** | August 2015 | A fixed vocabulary cannot hold every word a translator will meet | planned · [references](reference-catalog.md#6-byte-pair-encoding-for-words) |
| 7 | **Residual Networks** | December 2015 | Deeper networks trained worse, not better | planned · [references](reference-catalog.md#7-residual-networks) |
| 8 | **Monte Carlo Tree Search and AlphaGo** | 2006; January and March 2016 | Go's game tree is too large to search, and its positions too hard to judge | planned · [references](reference-catalog.md#8-monte-carlo-tree-search-and-alphago) |
| 9 | **The Transformer** | June 2017 | Recurrent networks read one word at a time and forget the start of a sentence | planned · [references](reference-catalog.md#9-the-transformer) |
| 10 | **Lattice Cryptography and ML-KEM** | Kyber 2017; FIPS 203, 13 August 2024 | A quantum computer would break RSA and Diffie–Hellman | planned · [references](reference-catalog.md#10-lattice-cryptography-and-ml-kem) |
| 11 | **Diffusion Models** | March 2015; June 2020 | Generating images by learning to destroy them | planned · [references](reference-catalog.md#11-diffusion-models) |
| 12 | **FlashAttention** | May 2022 | Attention's table grows with the square of the text, and memory traffic, not arithmetic, was the bottleneck | planned · [references](reference-catalog.md#12-flashattention) |
| 13 | **Algorithms That Find Algorithms** | October and December 2022; May 2025 | People had searched for faster matrix multiplication by hand for fifty years | planned · [references](reference-catalog.md#13-algorithms-that-find-algorithms) |

The interactive edition is a single HTML file per topic: download it and open it in a browser, or use the published copy linked from the [book contents](../README.md).
