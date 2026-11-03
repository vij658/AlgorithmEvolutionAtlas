# Era 9 — Learning at Scale (plan)

*2009 to 2026. Topic list in order of time, with the exceptions noted below. Dates were checked in the reference catalog; the catalog's certainty labels win where they differ.*

> **Field note from the visiting historian.** In the eighth era the species built a Web, read its genome and agreed on a ledger. In this one an old idea, the network that learns from examples, suddenly works at scale, and much of the era's algorithmic work goes into making that learning possible: units and optimizers that keep gradients alive, connections that let a signal through a hundred layers, tokens, attention, and attention computed without writing its table down. Alongside it the species prepares for computers that do not exist yet, computing on data it cannot read and replacing public-key methods a quantum computer would break. By the end its machines search for algorithms themselves.

| # | Topic | Working date | Where | What hurt | The step forward | Builds on |
|---|---|---|---|---|---|---|
| 1 | Fully homomorphic encryption | 2009; over the integers 2010 | Stanford University | Data had to be decrypted before anyone could compute with it | Noisy ciphertexts that can be added and multiplied; bootstrapping refreshes the noise | Public-key cryptography (Era 6, 10) |
| 2 | Deep convolutional networks | September 2012 | University of Toronto | Hand-made image features had stalled; deep nets trained slowly and overfitted | Convolutions on GPUs, rectified linear units, dropout | Backpropagation (Era 7, 7) |
| 3 | Word embeddings | January and October 2013 | Google | Words were symbols with nothing in common | Vectors trained to predict neighbours; negative sampling | Huffman's codes (Era 5, 3), for hierarchical softmax |
| 4 | Raft | June 2014 | Stanford | Paxos was correct but hard to understand and build | Terms, randomized elections, one leader's log | Paxos (Era 8, 8) |
| 5 | Adam | December 2014 | Amsterdam; Toronto | One learning rate for millions of different parameters | Running first and second moments, bias-corrected | Gradient descent and backpropagation (Era 7, 7) |
| 6 | Byte-pair encoding for words | August 2015 | Edinburgh | A fixed vocabulary cannot hold every word | Learned merges of frequent symbol pairs | Universal compression (Era 6, 12) |
| 7 | Residual networks | December 2015 | Microsoft Research | Deeper networks trained worse | Identity shortcuts: y = x + F(x) | LSTM (Era 8, 6) |
| 8 | Monte Carlo tree search and AlphaGo | 2006; 2016 | Google DeepMind | Go's tree is too large and its positions too hard to judge | Random playouts, UCT, and networks for moves and values | Monte Carlo (Era 4, 10); A* (Era 6, 4) |
| 9 | The Transformer | June 2017 | Google Brain, Google Research | Recurrent networks read word by word and forget | Scaled dot-product attention, heads, no recurrence | LSTM (Era 8, 6) |
| 10 | Lattice cryptography and ML-KEM | Kyber 2017; FIPS 203, August 2024 | Designers from Europe and North America; NIST | A quantum computer would break RSA and Diffie–Hellman | Module learning with errors; the number-theoretic transform | Public-key cryptography (Era 6, 10); Shor (Era 7, 11) |
| 11 | Diffusion models | March 2015; June 2020 | UC Berkeley (2020) | Generative models were unstable or blurry | Learn to remove noise, one small step at a time | Markov chains (Era 4, 3) |
| 12 | FlashAttention | May 2022 | Stanford; Buffalo | Attention's n × n table and its memory traffic | Tiling with an online softmax: exact, linear memory | The Transformer (9) |
| 13 | Algorithms that find algorithms | October and December 2022; May 2025 | DeepMind; Linz | Faster matrix multiplication had been searched for by hand for fifty years | Tensor decompositions found by learning and by random flips, checked exactly | Strassen (Era 6, 5); AlphaZero (8) |

## Decisions after the reference catalog

- The era runs from 2009 (Gentry's dissertation) to 2025 (AlphaEvolve), with the 2026 result on the exponent of matrix multiplication recorded in Era 6; the topics are ordered by the year each development first appeared in public, except where noted.
- Fully homomorphic encryption (1) is placed by Gentry's 2009 work; the 2010 scheme over the integers, which the program follows, shares the page.
- Word embeddings (3) are placed by the January 2013 arXiv paper; negative sampling (October 2013) shares the page.
- Raft (4) is placed by its June 2014 publication, before Adam (5), first posted in December 2014.
- Byte-pair encoding (6) is placed by the first arXiv version (August 2015), before residual networks (7, December 2015) and AlphaGo (8, January 2016). Gage's 1994 compressor shares the page.
- Monte Carlo tree search (8) is placed by AlphaGo (2016); the 2006 algorithm and the 1987 idea share the page.
- Lattice cryptography (10) is placed by Kyber's 2017 submission; the 2024 standard shares the page.
- Diffusion models (11) are placed by the 2020 paper that made them work; the 2015 paper that proposed them shares the page.
- Algorithms that find algorithms (13) is placed by AlphaTensor (2022); the flip graphs of the same year and AlphaEvolve (2025) share the page.
- The learning programs are small: a few thousand parameters, drawn shapes, made-up sentences, points in a plane. They show each mechanism and check it; the scale is the papers'.
- Every program prints only plain ASCII and uses fixed seeds, so the outputs are the same on every machine.

The [reference catalog](reference-catalog.md) holds the links (every one opened before it was listed) and the evidence for each topic.
