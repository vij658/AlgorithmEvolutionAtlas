# Era 9 — Learning at Scale: from fully homomorphic encryption to algorithms found by machines

*Reference catalog. Thirteen developments, from 2009 to 2025, with a note on 2026.*

> **Field note from the visiting historian.** In the eighth era the species built a Web, read its genome and agreed on a ledger. In this one its machines become large enough, and its data plentiful enough, that an old idea, the network that learns from examples (Eras 5 and 7), suddenly works: it recognizes photographs, places words in a space where meaning has a direction, plays Go better than any person, translates, and paints pictures out of noise. Much of the era's algorithmic work is about making that learning possible at all: optimizers that adjust themselves, connections that let a signal pass through a hundred layers, tokenizers that cut text into pieces, attention computed without ever writing the full table to memory. Alongside it, the species prepares for computers that do not exist yet: it learns to compute on data it cannot read, and it replaces public-key methods that a quantum computer would break. By the end, its machines are searching for algorithms themselves, and the historian's own subject begins to be written by its subjects.

## How to use this catalog

Every link was opened before it was listed. Links are tagged by level, so a high-school reader and a PhD scholar can both find their way in:

| Tag | Meaning |
|---|---|
| **Start** | No background needed. Watch or read this first. |
| **Deeper** | University level: the mechanism, the proof, the analysis. |
| **Scholar** | Primary sources and research papers: the evidence itself, and the arguments about it. |

Each claim also carries a certainty label:

- **Documented**: stated by the primary text, the holding archive, or standard scholarship.
- **Conjecture**: a reasonable reading that the evidence does not settle.
- **Disputed**: scholars, or the opened sources, disagree; the positions are given.

The **Atlas** lines will point to the matching chapters of *The Evolutionary Atlas of Algorithms and Data Structures* once mapped. The **Code** lines point to the tested Java programs.

A note on videos: YouTube's watch pages could not be opened from the environment used to build this catalog, but YouTube's own oEmbed lookup could, and it returns each video's real title and channel. Every video listed here was confirmed that way on 3 November 2026; the title and channel are copied from the lookup. The lookup does not show the video itself, so a video is described by its title, its channel and what the channel is, never by claims about its contents.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [Fully homomorphic encryption](#1-fully-homomorphic-encryption) | 2009; over the integers 2010 | Encrypted data had to be decrypted before anyone could compute with it |
| 2 | [Deep convolutional networks](#2-deep-convolutional-networks) | September 2012 | Hand-made image features had stalled; deep networks were too slow to train |
| 3 | [Word embeddings](#3-word-embeddings) | January and October 2013 | Words were symbols with no notion of likeness |
| 4 | [Raft](#4-raft) | 2014 | Paxos was correct but hard to understand and to build |
| 5 | [Adam](#5-adam) | December 2014 | One learning rate for millions of very different parameters |
| 6 | [Byte-pair encoding for words](#6-byte-pair-encoding-for-words) | August 2015 | A fixed vocabulary cannot hold every word a translator will meet |
| 7 | [Residual networks](#7-residual-networks) | December 2015 | Deeper networks trained worse, not better |
| 8 | [Monte Carlo tree search and AlphaGo](#8-monte-carlo-tree-search-and-alphago) | 2006; January and March 2016 | Go's game tree is too large to search, and its positions too hard to judge |
| 9 | [The Transformer](#9-the-transformer) | June 2017 | Recurrent networks read one word at a time and forget the start of a sentence |
| 10 | [Lattice cryptography and ML-KEM](#10-lattice-cryptography-and-ml-kem) | Kyber 2017; FIPS 203, 13 August 2024 | A quantum computer would break RSA and Diffie–Hellman |
| 11 | [Diffusion models](#11-diffusion-models) | March 2015; June 2020 | Generating images by learning to destroy them |
| 12 | [FlashAttention](#12-flashattention) | May 2022 | Attention's table grows with the square of the text, and memory traffic, not arithmetic, was the bottleneck |
| 13 | [Algorithms that find algorithms](#13-algorithms-that-find-algorithms) | October and December 2022; May 2025 | People had searched for faster matrix multiplication by hand for fifty years |

## 1. Fully homomorphic encryption

**When / where:** Ronald Rivest, Leonard Adleman and Michael Dertouzos asked for such a scheme in 1978 ("On data banks and privacy homomorphisms"); Craig Gentry, Stanford University, the first plausible construction (2009; dissertation *A Fully Homomorphic Encryption Scheme*, September 2009, adviser Dan Boneh); Marten van Dijk, Craig Gentry, Shai Halevi and Vinod Vaikuntanathan, "Fully Homomorphic Encryption over the Integers" (Cryptology ePrint 2009/616, received 14 December 2009; Eurocrypt 2010).
**Atlas:** to be mapped · **Code:** [`FullyHomomorphic.java`](../../code/era-09-learning-at-scale/01-homomorphic-encryption/) · **Page:** [topic 1](01-homomorphic-encryption/README.md)

> **Field note.** A year after RSA (Era 6), three of the species' cryptographers asked for something stranger: a way to hand encrypted data to a stranger's computer, have it add and multiply the numbers inside, and get back an encrypted answer, without the stranger ever seeing anything. For thirty years every scheme could do one operation or the other, never both without limit. In 2009 a doctoral student at Stanford found the way through. Each encrypted number carries a little noise; adding and multiplying make the noise grow, until it drowns the message. Gentry's trick was to have the scheme run its own decryption, encrypted, on a noisy ciphertext: the result is the same message with fresh, small noise. A year later he and three colleagues showed the same idea with nothing but integers: a secret odd number p, and a message hidden as a near-multiple of it.

**What hurt:** to compute on data you had to decrypt it, so a cloud computer, or anyone running the computation, saw everything; schemes that allowed computing on ciphertexts allowed only additions or only multiplications, or only a few of them.
**The step forward:** a somewhat homomorphic scheme whose noise grows with each operation, made fully homomorphic by bootstrapping: evaluating the decryption circuit homomorphically to refresh the noise.

**Evidence and certainty**

- "The problem of constructing a fully homomorphic encryption scheme was first proposed in 1978, within a year of publishing of the RSA scheme" (the reference is Rivest, Adleman and Dertouzos, "On data banks and privacy homomorphisms"); Gentry, "using lattice-based cryptography, described the first plausible construction for a fully homomorphic encryption scheme in 2009", starting "from a somewhat homomorphic encryption scheme"; the noise "grows as one adds and multiplies ciphertexts" until it "makes the resulting ciphertext indecipherable"; bootstrapping "effectively 'refreshes' the ciphertext by applying to it the decryption procedure homomorphically"; a 2010 scheme by van Dijk, Gentry, Halevi and Vaikuntanathan "does not require ideal lattices"; later generations: BGV (2011), GSW (2013), CKKS (2016, approximate numbers), and "All the second-generation cryptosystems still follow the basic blueprint of Gentry's original construction." **Documented** ([Wikipedia, Homomorphic encryption](https://en.wikipedia.org/wiki/Homomorphic_encryption))
- Gentry's dissertation, Stanford University, Department of Computer Science, September 2009, adviser Dan Boneh: "We propose the first fully homomorphic encryption scheme, solving a central open problem in cryptography. Such a scheme allows one to compute arbitrary functions over encrypted data without the decryption key"; the construction "begins with a somewhat homomorphic 'boostrappable' encryption scheme" (the misspelling is in the abstract). **Documented** ([Gentry 2009, Stanford Applied Cryptography Group](https://crypto.stanford.edu/craig/craig-thesis.pdf))
- van Dijk, Gentry, Halevi and Vaikuntanathan: "We describe a very simple 'somewhat homomorphic' encryption scheme using only elementary modular arithmetic, and use Gentry's techniques to convert it into a fully homomorphic scheme"; security rests on "finding an approximate integer gcd — i.e., given a list of integers that are near-multiples of a hidden integer, output that hidden integer". Received 14 December 2009, published at Eurocrypt 2010. **Documented** ([Cryptology ePrint Archive, Paper 2009/616](https://eprint.iacr.org/2009/616))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [How To Compute With Encrypted Data](https://www.youtube.com/watch?v=fLjPGhCDzKY) | TechTechPotato (Ian Cutress) | An introduction for a general audience |
| Deeper | [Introduction to FHE (Fully Homomorphic Encryption) - Pascal Paillier, FHE.org Meetup](https://www.youtube.com/watch?v=aruz58RarVA) | Zama | A talk by the inventor of the Paillier cryptosystem |
| Scholar | [A Decade (or so) of fully homomorphic encryption, by Craig Gentry](https://www.youtube.com/watch?v=487AjvFW1lk) | IACR | The inventor, on the channel of the International Association for Cryptologic Research |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Homomorphic encryption](https://en.wikipedia.org/wiki/Homomorphic_encryption) | Wikipedia | The 1978 question, the noise, bootstrapping and the generations of schemes |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A Fully Homomorphic Encryption Scheme](https://crypto.stanford.edu/craig/craig-thesis.pdf) | C. Gentry (2009), dissertation, Stanford | The first construction, and bootstrapping |
| Scholar | [Fully Homomorphic Encryption over the Integers](https://eprint.iacr.org/2009/616) | M. van Dijk, C. Gentry, S. Halevi, V. Vaikuntanathan (2009–2010) | The same idea with integers only; the scheme the program follows |

**Gaps:** Gentry's STOC 2009 paper and the 1978 paper by Rivest, Adleman and Dertouzos were not opened. The program implements a symmetric version of the integer scheme with toy sizes and shows bootstrapping's purpose (the noise limit), not bootstrapping itself, which needs far larger parameters.

## 2. Deep convolutional networks

**When / where:** Alex Krizhevsky, Ilya Sutskever and Geoffrey Hinton, University of Toronto: entry to the ImageNet Large Scale Visual Recognition Challenge, submitted 30 September 2012; "ImageNet Classification with Deep Convolutional Neural Networks", NIPS 2012. The network became known as AlexNet. Earlier convolutional networks: Fukushima's neocognitron (1980); LeCun and colleagues' LeNet (from 1989).
**Atlas:** to be mapped · **Code:** [`ConvNet.java`](../../code/era-09-learning-at-scale/02-deep-convolutional-networks/) · **Page:** [topic 2](02-deep-convolutional-networks/README.md)

> **Field note.** Convolutional networks were old: a small filter slides over an image and responds wherever a pattern appears, and layers of such filters, trained by backpropagation (Era 7), had read handwritten digits since the late 1980s. What they had never done was beat the hand-made features of computer vision on real photographs. In 2012 a team in Toronto trained one with sixty million parameters on a million labelled photographs, on two gaming graphics cards, for five or six days. They replaced the smooth sigmoid with a unit that is simply max(0, x), which trained several times faster; they switched off half the units at random while training, so that none could rely on another; and they won the ImageNet challenge by more than ten percentage points. The field changed direction within a year.

**What hurt:** hand-designed image features had stopped improving; deep networks trained slowly, because sigmoid and tanh units saturate and pass back vanishing error signals, and they overfitted.
**The step forward:** a deep convolutional network trained on graphics processors, with rectified linear units, dropout and data augmentation.

**Evidence and certainty**

- Krizhevsky, Sutskever and Hinton (University of Toronto): on ILSVRC-2010 the network achieved "top-1 and top-5 error rates of 37.5% and 17.0%"; in ILSVRC-2012 "a winning top-5 test error rate of 15.3%", against 26.2% for the second-best entry; the network "has 60 million parameters and 650,000 neurons"; "non-saturating neurons" and "dropout"; on CIFAR-10, rectified linear units reach "a 25% training error rate on CIFAR-10 six times faster" than tanh units; "Our network takes between five and six days to train on two GTX 580 3GB GPUs." **Documented** ([Krizhevsky, Sutskever and Hinton 2012, on a Duke University course page](https://courses.cs.duke.edu/fall16/compsci527/papers/Krizhevsky%20et%20al%20DNN%20ImageNet%202012.pdf))
- AlexNet was developed in 2012 at the University of Toronto and submitted to ILSVRC on 30 September 2012; "top-5 error rate of 15.3% to win the contest, more than 10.8% points better than the runner-up"; trained "for 90 epochs over a period of five to six days using two Nvidia GTX 580 GPUs (3GB each)"; ReLU "trained better than tanh and sigmoid"; dropout with probability 0.5; Fukushima's neocognitron (1980) and LeNet (1989) came first; the paper had been cited over 198,000 times by early 2025. **Documented** ([Wikipedia, AlexNet](https://en.wikipedia.org/wiki/AlexNet))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [Neural Networks Part 8: Image Classification with Convolutional Neural Networks (CNNs)](https://www.youtube.com/watch?v=HGwBXDKFk9I) | StatQuest with Josh Starmer | Filters, pooling and classification, step by step |
| Deeper | [[Classic] ImageNet Classification with Deep Convolutional Neural Networks (Paper Explained)](https://www.youtube.com/watch?v=Nq3auVtvd9Q) | Yannic Kilcher | A walk through the 2012 paper |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [AlexNet](https://en.wikipedia.org/wiki/AlexNet) | Wikipedia | The network, the contest and what came before |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [ImageNet Classification with Deep Convolutional Neural Networks](https://courses.cs.duke.edu/fall16/compsci527/papers/Krizhevsky%20et%20al%20DNN%20ImageNet%202012.pdf) | A. Krizhevsky, I. Sutskever, G. Hinton (2012), on a Duke course page | The paper, with its ReLU and dropout experiments |

**Gaps:** the ImageNet challenge's own results pages, LeCun's papers and Fukushima's paper were not opened. Wikipedia gives the margin over the runner-up as 10.8 points; the paper gives the runner-up's error as 26.2%, which makes it 10.9. The program trains a small network on drawn shapes, not on photographs; its point is the mechanism (convolution, ReLU against sigmoid, dropout), not the scale.

## 3. Word embeddings

**When / where:** Tomas Mikolov, Kai Chen, Greg Corrado and Jeffrey Dean, Google, "Efficient Estimation of Word Representations in Vector Space" (arXiv, 16 January 2013); Mikolov, Ilya Sutskever, Chen, Corrado and Dean, "Distributed Representations of Words and Phrases and their Compositionality" (arXiv, October 2013; NIPS 2013), with negative sampling. The code was released as word2vec in 2013.
**Atlas:** to be mapped · **Code:** [`WordEmbeddings.java`](../../code/era-09-learning-at-scale/03-word-embeddings/) · **Page:** [topic 3](03-word-embeddings/README.md)

> **Field note.** To a computer a word was a symbol: "cat" and "kitten" were as different as "cat" and "carburettor". The species' linguists had long said that a word is known by the company it keeps, and in 2013 a team at Google took them literally. Give every word a list of a few hundred numbers, and train those numbers so that a word can predict the words around it. Nothing tells the program what any word means. Yet when the training is done, words used alike sit close together, and differences have directions: the step from a country to its capital points the same way for many countries. The trick that made it fast was to stop asking the model to choose the right neighbour out of the whole vocabulary, and ask it only to tell the real neighbour from a handful of random words.

**What hurt:** words as isolated symbols (one entry each in a huge vocabulary) share nothing, so nothing learned about one word carries to another; earlier neural language models learned word vectors but were slow to train.
**The step forward:** shallow models (continuous bag-of-words and skip-gram) trained on billions of words, with negative sampling and subsampling of frequent words, giving vectors in which similarity and analogy become geometry.

**Evidence and certainty**

- Mikolov, Chen, Corrado and Dean (submitted 16 January 2013): two new architectures; "it takes less than a day to learn high quality word vectors from a 1.6 billion words data set", with "state-of-the-art performance on our test set for measuring syntactic and semantic word similarities". **Documented** ([arXiv:1301.3781](https://arxiv.org/abs/1301.3781))
- Mikolov, Sutskever, Chen, Corrado and Dean (Google, 2013): subsampling of frequent words speeds training roughly 2 to 10 times; negative sampling, with 5 to 20 noise words for small datasets and 2 to 5 for large ones, drawn from the unigram distribution raised to the 3/4 power; phrases such as "New York Times" learned as single tokens; adding vectors combines meanings ("Russian" + "river" lands near "Volga River"). **Documented** ([arXiv:1310.4546, ar5iv edition](https://ar5iv.arxiv.org/html/1310.4546))
- Word2vec was introduced in two 2013 papers by Mikolov, Chen, Corrado, Sutskever and Dean at Google; the continuous bag-of-words model is "a 'fill in the blank' task", and in skip-gram "the model uses the current word to predict the surrounding window of context words"; hierarchical softmax "uses a Huffman tree" (compare Era 5, topic 3); the second paper "received the 2023 NeurIPS Test of Time Award". **Documented** ([Wikipedia, Word2vec](https://en.wikipedia.org/wiki/Word2vec))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [Word Embedding and Word2Vec, Clearly Explained!!!](https://www.youtube.com/watch?v=viZrOnJclY0) | StatQuest with Josh Starmer | Words to vectors, slowly and with pictures |
| Deeper | [Stanford CS224N: NLP with Deep Learning \| Winter 2021 \| Lecture 1 - Intro & Word Vectors](https://www.youtube.com/watch?v=rmVRLeJRkl4) | Stanford Online | The first lecture of Stanford's course, on word vectors |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Word2vec](https://en.wikipedia.org/wiki/Word2vec) | Wikipedia | The two models and the two training tricks |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781) | T. Mikolov, K. Chen, G. Corrado, J. Dean (2013) | The two architectures |
| Scholar | [Distributed Representations of Words and Phrases and their Compositionality](https://ar5iv.arxiv.org/html/1310.4546) | T. Mikolov, I. Sutskever, K. Chen, G. Corrado, J. Dean (2013) | Negative sampling and subsampling |

**Gaps:** the opened sources do not give the original wording of the "king − man + woman" example, so the page does not quote it; Firth's 1957 dictum was not opened. The program trains on a small generated corpus whose structure is known in advance, so it can check that the geometry appears; real embeddings are trained on billions of words.

## 4. Raft

**When / where:** Diego Ongaro and John Ousterhout, Stanford University, "In Search of an Understandable Consensus Algorithm", 2014 USENIX Annual Technical Conference, Philadelphia, June 2014 (Best Paper award).
**Atlas:** to be mapped · **Code:** [`Raft.java`](../../code/era-09-learning-at-scale/04-raft/) · **Page:** [topic 4](04-raft/README.md)

> **Field note.** Paxos (Era 8) let a group of computers agree in spite of lost messages and crashes, and it was correct, and almost nobody could explain it. Two systems researchers at Stanford set out to design a consensus algorithm whose first goal was to be understood. Raft splits the problem in three: elect one leader, let the leader copy its log to the others, and add a few rules that keep the logs safe when leaders change. Time is divided into numbered terms; a server that hears nothing from a leader for a random fraction of a second stands for election, and the randomness makes split votes rare. Then the authors tested their goal the way one tests a teaching method: they taught both algorithms to students, and gave them quizzes.

**What hurt:** Paxos was hard to understand and harder to turn into a working system; every real implementation filled gaps in its own way.
**The step forward:** a strong leader, randomized election timeouts, and a log that flows only from leader to followers, with five safety properties that hold whatever is lost or delayed.

**Evidence and certainty**

- Ongaro and Ousterhout, Stanford University, USENIX ATC '14 (June 2014), pages 305–319, "Awarded Best Paper!": Raft is "a consensus algorithm for managing a replicated log"; "It produces a result equivalent to (multi-)Paxos, and it is as efficient as Paxos"; it separates "leader election, log replication, and safety"; "Results from a user study demonstrate that Raft is easier for students to learn than Paxos." **Documented** ([USENIX, conference page](https://usenix.org/node/184041))
- The paper: "Unfortunately, Paxos is quite difficult to understand, in spite of numerous attempts to make it more approachable"; "Raft divides time into terms of arbitrary length"; "election timeouts are chosen randomly from a fixed interval (e.g., 150–300ms)"; Election Safety ("at most one leader can be elected in a given term"), Leader Append-Only, Log Matching (logs with an entry of the same index and term "are identical in all entries up through the given index"), Leader Completeness and State Machine Safety; in the user study, 43 students at Stanford and Berkeley scored 25.7 on the Raft quiz and 20.8 on the Paxos quiz (out of 60), 33 of the 43 scored higher on Raft, and 33 of 41 said Raft would be easier to implement. **Documented** ([Ongaro and Ousterhout 2014, on a Princeton course page](https://www.cs.princeton.edu/courses/archive/spring22/cos418/papers/raft.pdf))
- The Raft site: "Raft is a consensus algorithm that is designed to be easy to understand"; "Consensus is a fundamental problem in fault-tolerant distributed systems"; a cluster of 5 servers "can continue to operate even if 2 servers fail"; with RaftScope, an interactive visualization. **Documented** ([raft.github.io](https://raft.github.io/))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Deeper | [Distributed Systems 6.2: Raft](https://www.youtube.com/watch?v=uXEYuDwm7e4) | Martin Kleppmann | A lecture from Kleppmann's Cambridge course |
| Scholar | [Raft lecture (Raft user study)](https://www.youtube.com/watch?v=YbZ3zDzDnrw) | Diego Ongaro | The lecture recorded for the user study, by Raft's designer |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Raft Consensus Algorithm](https://raft.github.io/) | raft.github.io | An interactive cluster to break |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [In Search of an Understandable Consensus Algorithm](https://www.cs.princeton.edu/courses/archive/spring22/cos418/papers/raft.pdf) | D. Ongaro, J. Ousterhout (2014), on a Princeton course page | The algorithm, the safety properties and the user study |
| Scholar | [USENIX ATC '14 paper page](https://usenix.org/node/184041) | USENIX | Venue, pages and award |

**Gaps:** Ongaro's 2014 dissertation and the extended version of the paper were not opened. The program simulates Raft with messages that are lost, delayed and reordered, and crashes; it checks the safety properties in every run but does not prove them (the paper points to a formal proof).

## 5. Adam

**When / where:** Diederik P. Kingma (University of Amsterdam, OpenAI) and Jimmy Lei Ba (University of Toronto), "Adam: A Method for Stochastic Optimization", arXiv 22 December 2014; ICLR 2015, San Diego.
**Atlas:** to be mapped · **Code:** [`Adam.java`](../../code/era-09-learning-at-scale/05-adam/) · **Page:** [topic 5](05-adam/README.md)

> **Field note.** A network learns by gradient descent: nudge every weight a little against its gradient. But how big is "a little"? Some weights see large, steady gradients; others small, noisy, rare ones; a single step size is too large for the first and too small for the second. The species had tried several fixes: momentum (keep moving in the direction you were going), AdaGrad (divide each weight's step by the size of its past gradients), RMSProp (the same, but forgetting the distant past). Adam combines momentum with RMSProp, and adds a small correction for the fact that both running averages start at zero.

**What hurt:** one learning rate for millions of parameters whose gradients differ in size by orders of magnitude, with noise from small batches.
**The step forward:** per-parameter steps from running estimates of the gradient's first and second moments, corrected for their zero start.

**Evidence and certainty**

- Kingma and Ba, "Published as a conference paper at ICLR 2015": a method based on "adaptive estimates of lower-order moments"; it "has little memory requirements" and "is invariant to diagonal rescaling of the gradients"; suggested defaults α = 0.001, β₁ = 0.9, β₂ = 0.999, ε = 10⁻⁸; because the moving averages start at zero they are biased toward zero, and each is divided by (1 − βᵗ); "the name Adam is derived from adaptive moment estimation"; Adam combines AdaGrad's strength on sparse gradients with RMSProp's on non-stationary objectives, and RMSProp with momentum, lacking the bias correction, takes very large steps when β₂ is close to 1. **Documented** ([Kingma and Ba, arXiv:1412.6980 (PDF)](https://arxiv.org/pdf/1412.6980))
- First submitted on 22 December 2014; last revised (v9) on 30 January 2017; "Published as a conference paper at the 3rd International Conference for Learning Representations, San Diego, 2015". **Documented** ([arXiv:1412.6980](https://arxiv.org/abs/1412.6980))
- Robbins and Monro (1951) "introduced the earliest stochastic approximation methods"; momentum "appeared in Rumelhart, Hinton and Williams' paper on backpropagation learning"; AdaGrad was "first published in 2011"; RMSProp was "not published in an article but merely described in a Coursera lecture"; Adam is "a 2014 update to the RMSProp optimizer combining it with the main feature of the Momentum method"; "The initial proof establishing the convergence of Adam was incomplete", and "Adam does not converge for all convex objectives"; AMSGrad uses the "maximum of past squared gradients". **Documented** ([Wikipedia, Stochastic gradient descent](https://en.wikipedia.org/wiki/Stochastic_gradient_descent)); Adam's convergence guarantee as first published: **Disputed** (the article reports the proof incomplete).

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [Optimization for Deep Learning (Momentum, RMSprop, AdaGrad, Adam)](https://www.youtube.com/watch?v=NE88eqLngkg) | DeepBean | The four methods side by side |
| Deeper | [Adam Optimization Algorithm (C2W2L08)](https://www.youtube.com/watch?v=JXQT_vxqwIs) | DeepLearningAI | Andrew Ng's lecture in the Deep Learning Specialization |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Stochastic gradient descent](https://en.wikipedia.org/wiki/Stochastic_gradient_descent) | Wikipedia | From Robbins and Monro to Adam and AMSGrad |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Adam: A Method for Stochastic Optimization](https://arxiv.org/abs/1412.6980) | D. P. Kingma, J. Ba (2014; ICLR 2015) | The algorithm, the defaults and the bias correction |

**Gaps:** the AdaGrad paper, Hinton's RMSProp lecture and Reddi, Kale and Kumar's paper on Adam's convergence were not opened. The program reproduces the bias correction and compares the methods on test problems; it does not reproduce the paper's experiments.

## 6. Byte-pair encoding for words

**When / where:** Philip Gage, "A New Algorithm for Data Compression", *The C Users Journal* (1994); Rico Sennrich, Barry Haddow and Alexandra Birch, School of Informatics, University of Edinburgh, "Neural Machine Translation of Rare Words with Subword Units" (arXiv:1508.07909, first version 31 August 2015; revised 10 June 2016).
**Atlas:** to be mapped · **Code:** [`BytePairEncoding.java`](../../code/era-09-learning-at-scale/06-byte-pair-encoding/) · **Page:** [topic 6](06-byte-pair-encoding/README.md)

> **Field note.** A neural translator has a fixed vocabulary: perhaps fifty thousand words, each with its own row of numbers. Every other word, a name, a rare compound, a new coinage, becomes "unknown". A compression trick from 1994 offered a way out. Gage's byte-pair encoding finds the most frequent pair of adjacent symbols and replaces it with a new symbol, again and again. Sennrich, Haddow and Birch at Edinburgh applied it to words split into letters: frequent words grow into single symbols, rare words stay in pieces that the translator has seen before. Twenty thousand or sixty thousand merges, and the vocabulary is closed, yet every word can be written. A slightly changed version still cuts text into the "tokens" that today's language models read.

**What hurt:** a fixed vocabulary cannot contain every word, so rare words, names and compounds were lost; whole-word vocabularies grew without limit.
**The step forward:** learn a list of merges from data; segment any word into the longest learned pieces; a vocabulary of a fixed size that can still spell everything.

**Evidence and certainty**

- Sennrich, Haddow and Birch (School of Informatics, University of Edinburgh): translation is "an open-vocabulary problem"; byte-pair encoding is "a simple data compression technique" that repeatedly merges the most frequent pair of symbols; each word is ended with a "special end-of-word symbol" '·' so that the original words can be restored; the paper's Algorithm 1 is a minimal Python implementation; its Figure 1 learns merges from the toy dictionary {'low', 'lowest', 'newer', 'wider'} (first r ·, then l o, then lo w, then e r·); experiments used 59,500 merge operations (89,500 for a joint vocabulary); subword models improved over a back-off dictionary baseline "by up to 1.1 and 1.3 BLEU, respectively" for English→German and English→Russian. **Documented** ([Sennrich, Haddow and Birch, arXiv:1508.07909 (PDF, v5 of 10 June 2016)](https://arxiv.org/pdf/1508.07909))
- Byte-pair encoding was "first described in 1994 by Philip Gage" ("A New Algorithm for Data Compression", *The C User Journal*); the original "replaces the highest-frequency pair of bytes with a new byte that was not contained in the initial dataset", with a table to undo it (aaabdaaabac → ZabdZabac with Z = aa → ZYdZYac with Y = ab); "A slightly modified version of the algorithm is used in large language model tokenizers", producing tokens rather than maximal compression; byte-level BPE "converts the text into UTF-8 first", so any text can be encoded; GPT-3.5 and GPT-4 use a vocabulary of 100,258 tokens (100,000 learned plus 258 special). **Documented** ([Wikipedia, Byte-pair encoding](https://en.wikipedia.org/wiki/Byte-pair_encoding))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [Byte Pair Encoding Tokenization](https://www.youtube.com/watch?v=HEikzVL-lZU) | Hugging Face | A short lesson from the Hugging Face course |
| Deeper | [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) | Andrej Karpathy | A byte-level tokenizer written from scratch |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Byte-pair encoding](https://en.wikipedia.org/wiki/Byte-pair_encoding) | Wikipedia | The 1994 compressor and today's tokenizers |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/pdf/1508.07909) | R. Sennrich, B. Haddow, A. Birch (2015–2016) | Merges learned on words, and Algorithm 1 |

**Gaps:** Gage's 1994 article was not opened. The opened arXiv text does not name the conference, so the page does not either (it is widely cited as ACL 2016). The program learns merges from a small text written for it, not from a translation corpus.

## 7. Residual networks

**When / where:** Kaiming He, Xiangyu Zhang, Shaoqing Ren and Jian Sun, Microsoft Research, "Deep Residual Learning for Image Recognition", arXiv 10 December 2015 (CVPR 2016). First place in the ILSVRC 2015 classification task. Highway networks, a gated form of the same idea, appeared in 2015 too.
**Atlas:** to be mapped · **Code:** [`ResidualNetworks.java`](../../code/era-09-learning-at-scale/07-residual-networks/) · **Page:** [topic 7](07-residual-networks/README.md)

> **Field note.** After 2012 the species stacked more layers, and the networks got better, up to a point. Beyond about twenty layers they got worse, and not because they memorized the training data: they did worse on the training data itself. A deeper network could in principle copy a shallower one and set its extra layers to do nothing, yet training could not find that solution. A team at Microsoft Research made "doing nothing" the default: each block of layers computes a correction that is added to its input, y = x + F(x). If the correction is not needed it can shrink to zero. With this one change they trained networks of 152 layers, won the ImageNet challenge of 2015, and gave every later deep network, the transformers included, its backbone.

**What hurt:** deeper plain networks had higher training error than shallower ones (the degradation problem); signals and gradients faded or exploded through many layers.
**The step forward:** identity shortcuts: each block learns a residual F(x) added to its input, at no extra cost in parameters or computation.

**Evidence and certainty**

- He, Zhang, Ren and Sun, submitted 10 December 2015 ("Tech report."): networks of up to 152 layers, 8 times deeper than VGG nets but of lower complexity; an ensemble reached 3.57% error on the ImageNet test set and won first place in the ILSVRC 2015 classification task; a 28% relative improvement on COCO object detection. **Documented** ([arXiv:1512.03385](https://arxiv.org/abs/1512.03385v1))
- The paper (Microsoft Research): "with the network depth increasing, accuracy gets saturated (which might be unsurprising) and then degrades rapidly. Unexpectedly, such degradation is not caused by overfitting"; "we let the stacked nonlinear layers fit another mapping of F(x) := H(x)−x", so the block computes y = F(x) + x; "Identity shortcut connections add neither extra parameter nor computational complexity"; "the 34-layer plain net has higher training error throughout the whole training procedure"; top-1 error on ImageNet validation (10-crop): plain 18 layers 27.94%, plain 34 layers 28.54%, ResNet-18 27.88%, ResNet-34 25.03%. **Documented** ([He et al. 2015 (PDF)](https://arxiv.org/pdf/1512.03385))
- ResNet "was developed in 2015 for image recognition, and won the ImageNet Large Scale Visual Recognition Challenge" that year; the highway network (2015) applied the idea of an unrolled LSTM to feed-forward networks, and "ResNet is equivalent to an open-gated highway network"; an LSTM's cell state can "function as a generalized residual connection"; "All transformer architectures include residual connections", as do AlphaGo Zero, AlphaStar and AlphaFold; residual connections ease vanishing gradients "to some extent", though vanishing gradients are not the root cause of the degradation problem. **Documented** ([Wikipedia, Residual neural network](https://en.wikipedia.org/wiki/Residual_neural_network))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Deeper | [[Classic] Deep Residual Learning for Image Recognition (Paper Explained)](https://www.youtube.com/watch?v=GWt6Fu05voI) | Yannic Kilcher | A walk through the paper |
| Scholar | [Deep Residual Learning for Image Recognition](https://www.youtube.com/watch?v=C6tLw-rPQ2o) | ComputerVisionFoundation Videos | The conference talk, on the channel of the Computer Vision Foundation |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Residual neural network](https://en.wikipedia.org/wiki/Residual_neural_network) | Wikipedia | The degradation problem, highway networks and where residuals went next |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Deep Residual Learning for Image Recognition](https://arxiv.org/pdf/1512.03385) | K. He, X. Zhang, S. Ren, J. Sun (2015) | The degradation experiment and the residual block |

**Gaps:** the highway network paper was not opened. The oEmbed lookup does not name the speaker of the conference talk. The program shows the degradation problem and its fix on a small regression task with plain and residual networks of several depths; the ImageNet numbers are the paper's.

## 8. Monte Carlo tree search and AlphaGo

**When / where:** Bruce Abramson's random playouts (1987); Bernd Brügmann's Monte Carlo Go (1992–1993); Rémi Coulom named Monte Carlo tree search (2006); Levente Kocsis and Csaba Szepesvári, UCT (2006); David Silver, Demis Hassabis and colleagues, Google DeepMind, AlphaGo: announced 27 January 2016 (*Nature*), 5–0 against Fan Hui, then 4–1 against Lee Sedol in Seoul, March 2016; AlphaZero (2017).
**Atlas:** to be mapped · **Code:** [`MonteCarloTreeSearch.java`](../../code/era-09-learning-at-scale/08-monte-carlo-tree-search/) · **Page:** [topic 8](08-monte-carlo-tree-search/README.md)

> **Field note.** Chess fell to search: look ahead, score the positions, choose the best line. Go resisted, because a player has hundreds of moves at each turn and nobody could write a good scoring rule for a Go position. The first step around it was almost absurd: to judge a position, play the game out to the end many times with random moves, and count the wins. In 2006 two ideas made that into a search: grow a tree of positions from the playouts (Coulom), and choose which branch to explore next by a formula from the theory of gambling machines that balances a branch's win rate against how little it has been tried (Kocsis and Szepesvári). Ten years later DeepMind added two neural networks: one proposes moves, as a strong player would; the other judges positions, as no rule had. AlphaGo beat the European champion 5–0, and then Lee Sedol 4–1.

**What hurt:** Go's tree is far too large for exhaustive search, and no hand-written evaluation of a Go position was good enough.
**The step forward:** Monte Carlo tree search with UCT: random playouts as the evaluation, and an upper confidence bound that spends simulations where they are most informative; then neural networks to propose moves and judge positions.

**Evidence and certainty**

- Abramson's thesis (1987) combined minimax with an expected-outcome model based on random playouts; Brügmann used Monte Carlo methods in a Go program in 1992 (report 1993); in 2006 Coulom applied the Monte Carlo method to game-tree search and coined the name "Monte Carlo tree search"; Kocsis and Szepesvári developed UCT, upper confidence bounds applied to trees, from the UCB1 formula (2006); each round has four steps: selection, expansion, simulation and backpropagation; AlphaGo won against Lee Sedol in March 2016, "a five-game match with a final score of four games to one"; AlphaZero (2017) "replaces the simulation step with an evaluation based on a neural network". **Documented** ([Wikipedia, Monte Carlo tree search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search))
- Silver and Hassabis, 27 January 2016: the search space of Go is "more than a googol times larger than chess"; a policy network proposes moves and a value network judges positions; the policy network was trained on 30 million moves from expert games "until it could predict the human move 57% of the time" (the previous record was 44%); AlphaGo "won all but one of its 500 games" against other Go programs and beat the European champion Fan Hui "by 5 games to 0"; a match against Lee Sedol was set for "this March in Seoul, South Korea". **Documented** ([Google Research blog](https://research.google/blog/alphago-mastering-the-ancient-game-of-go-with-machine-learning/))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [AlphaGo - The Movie \| Full award-winning documentary](https://www.youtube.com/watch?v=WXuK6gekU1Y) | Google DeepMind | The Lee Sedol match, on DeepMind's own channel |
| Deeper | [Monte Carlo Tree Search](https://www.youtube.com/watch?v=UXW2yZndl7U) | John Levine | The four steps and UCT, worked on a whiteboard |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [AlphaGo: Mastering the ancient game of Go with Machine Learning](https://research.google/blog/alphago-mastering-the-ancient-game-of-go-with-machine-learning/) | D. Silver, D. Hassabis, Google Research blog (2016) | The announcement |
| Deeper | [Monte Carlo tree search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search) | Wikipedia | History from 1987, the four steps and UCT |

**Original sources**

No primary paper could be opened (see **Gaps**).

**Gaps:** the *Nature* paper, Coulom's paper and Kocsis and Szepesvári's paper were not opened; the opened Wikipedia text describes the UCT formula without printing it, so the page states the standard UCB1 form without quoting it. The program plays Connect Four with plain UCT and random playouts, and checks it against exhaustive search on tic-tac-toe; it has no neural networks.

## 9. The Transformer

**When / where:** Dzmitry Bahdanau (Jacobs University Bremen), KyungHyun Cho and Yoshua Bengio (Université de Montréal), attention for translation (arXiv 2014; ICLR 2015); Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser and Illia Polosukhin, Google Brain, Google Research and University of Toronto, "Attention Is All You Need" (arXiv 12 June 2017; NIPS 2017).
**Atlas:** to be mapped · **Code:** [`Transformer.java`](../../code/era-09-learning-at-scale/09-transformer/) · **Page:** [topic 9](09-transformer/README.md)

> **Field note.** A recurrent network (Era 7; the LSTM of Era 8) reads a sentence one word at a time and must squeeze everything into one vector before it writes a word of the translation. In 2014 Bahdanau, Cho and Bengio let the translator look back: at each output word it scores every input word and takes a weighted average, attending to the ones that matter. Three years later eight researchers at Google removed the recurrence altogether. Every word asks a question (a query), every word offers a key and a value; a softmax over query-key scores decides how much of each value to take. All the words are processed at once, which suits graphics processors, and any word can reach any other in one step. They called it the Transformer.

**What hurt:** recurrent networks process words one after another, which is slow to train and makes distant words hard to connect; the fixed-length summary was a bottleneck.
**The step forward:** scaled dot-product attention, many heads in parallel, positional encodings, and no recurrence at all.

**Evidence and certainty**

- Bahdanau, Cho and Bengio ("Published as a conference paper at ICLR 2015"): "the use of a fixed-length vector is a bottleneck in improving the performance"; the fix is "allowing a model to automatically (soft-)search for parts of a source sentence that are relevant to predicting a target word". **Documented** ([arXiv:1409.0473 (PDF)](https://arxiv.org/pdf/1409.0473))
- Vaswani and colleagues, submitted 12 June 2017: a network "based solely on attention mechanisms, dispensing with recurrence and convolutions entirely"; "Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task"; on English-to-French, a single-model state of the art of 41.8 BLEU "after training for 3.5 days on eight GPUs". **Documented** ([arXiv:1706.03762](https://arxiv.org/abs/1706.03762v3))
- The paper (Google Brain, Google Research, University of Toronto; "Equal contribution. Listing order is random."): "Attention(Q, K, V) = softmax(QKᵀ/√dk)V"; the scaling because for large dk the dot products grow large, "pushing the softmax function into regions where it has extremely small gradients"; "h = 8 parallel attention layers, or heads", with dk = dv = dmodel/h = 64 and dmodel = 512; "each dimension of the positional encoding corresponds to a sinusoid"; a self-attention layer costs O(n² · d) with O(1) sequential operations and O(1) maximum path length. **Documented** ([Vaswani et al. 2017 (PDF)](https://arxiv.org/pdf/1706.03762))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [Attention in transformers, step-by-step \| Deep Learning Chapter 6](https://www.youtube.com/watch?v=eMlx5fFNoYc) | 3Blue1Brown | Queries, keys and values, drawn |
| Deeper | [Let's build GPT: from scratch, in code, spelled out.](https://www.youtube.com/watch?v=kCc8FmEb1nY) | Andrej Karpathy | A small transformer written and trained live |

**Read**

No secondary page was opened for this topic; the two papers below are short and readable.

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Attention Is All You Need](https://arxiv.org/pdf/1706.03762) | A. Vaswani and seven co-authors (2017) | The Transformer |
| Scholar | [Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/pdf/1409.0473) | D. Bahdanau, K. Cho, Y. Bengio (2014; ICLR 2015) | Attention, before the Transformer |

**Gaps:** the NIPS 2017 proceedings page was not opened. The program trains a one-layer, one-head attention model on a small task (find the value stored under a key) with its gradients written out by hand, and checks the gradients numerically; it is not a language model.

## 10. Lattice cryptography and ML-KEM

**When / where:** Oded Regev's learning with errors (2005); the CRYSTALS-Kyber team, submitted to NIST's post-quantum competition in 2017; NIST, FIPS 203, *Module-Lattice-Based Key-Encapsulation Mechanism Standard* (ML-KEM), published 13 August 2024.
**Atlas:** to be mapped · **Code:** [`LatticeKem.java`](../../code/era-09-learning-at-scale/10-lattice-cryptography/) · **Page:** [topic 10](10-lattice-cryptography/README.md)

> **Field note.** RSA and Diffie–Hellman (Era 6) rest on factoring and discrete logarithms, and Shor's algorithm (Era 7) would solve both on a large quantum computer. No such computer existed, but an encrypted message recorded today could be read once one did, so the species began replacing its public-key methods in advance. The replacement that won rests on a different hard problem: solve a system of linear equations modulo a prime when every equation has been nudged by a small random error. Without the errors, Gaussian elimination (the fangcheng of Era 2) solves it at once; with them, nobody knows how, on any computer. Kyber packs the equations into polynomials so that the keys stay small and the arithmetic fast, using the number-theoretic transform, the fast Fourier transform's cousin in modular arithmetic. In August 2024 the United States standardized it as ML-KEM.

**What hurt:** a large quantum computer would break RSA and elliptic-curve key exchange, and data recorded now could be decrypted later.
**The step forward:** key exchange from module learning with errors: public keys t = A·s + e, messages hidden in the high bits, and noise small enough that the receiver can round it away.

**Evidence and certainty**

- NIST, FIPS 203, "Published August 13, 2024": "ML-KEM is derived from the round-three version of the CRYSTALS-KYBER KEM"; "The security of ML-KEM is related to the computational difficulty of the Module Learning with Errors problem"; n = 256 and q, "the prime integer 3329"; "𝜁 = 17 ∈ ℤ𝑞 is a primitive 256-th root of unity modulo 𝑞" (the number-theoretic transform); Compress and Decompress round between ℤq and d-bit integers; decapsulation failure probabilities 2^−138.8 (ML-KEM-512), 2^−164.8 (ML-KEM-768) and 2^−174.8 (ML-KEM-1024); each parameter set fixes k, η₁, η₂, d_u and d_v. **Documented** ([NIST FIPS 203 (PDF)](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf))
- The parameter sets: k = 2, 3, 4; η₁ = 3, 2, 2; η₂ = 2; (d_u, d_v) = (10, 4), (10, 4), (11, 5); public keys 800, 1,184 and 1,568 bytes, ciphertexts 768, 1,088 and 1,568 bytes. **Documented** ([*Elements of Cryptanalysis*, chapter 41, ML-KEM (Kyber)](https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part14_lattice_crypto/ch41_ml_kem_kyber.html); the page names no author); the ML-KEM-768 sizes agree with Wikipedia's.
- Kyber was submitted to NIST in 2017 and was "the first key encapsulation mechanism that has been selected for standardization"; "The system is based on the module learning with errors (M-LWE) problem, in conjunction with cyclotomic rings", "derived from a method published in 2005 by Oded Regev"; ML-KEM-768 keys of 2,400 (secret) and 1,184 (public) bytes and ciphertexts of 1,088 bytes; Signal adopted the Kyber-based PQXDH protocol in 2023. **Documented** ([Wikipedia, ML-KEM](https://en.wikipedia.org/wiki/ML-KEM))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [Learning with errors: Encrypting with unsolvable equations](https://www.youtube.com/watch?v=K026C5YaB3A) | Chalk Talk | Equations with errors, and why they hide a secret |
| Deeper | [Learning With Errors (LWE) and Public Key Encryption \|\| @ CMU \|\| Lecture 25d of CS Theory Toolkit](https://www.youtube.com/watch?v=QcVns57MTxg) | Ryan O'Donnell | Regev's public-key scheme, in a Carnegie Mellon course |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [ML-KEM](https://en.wikipedia.org/wiki/ML-KEM) | Wikipedia | From Regev to the standard |
| Deeper | [ML-KEM (Kyber) – Design and Implementation](https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part14_lattice_crypto/ch41_ml_kem_kyber.html) | *Elements of Cryptanalysis*, chapter 41 | The parameter sets, worked through |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf) | NIST (13 August 2024) | The standard |

**Gaps:** Regev's 2005 paper and the Kyber submission documents were not opened; the opened FIPS text did not include its parameter table, which is taken from the book chapter and checked by the program against the byte sizes. The program implements the encryption at ML-KEM's sizes (n = 256, q = 3329, the transform with ζ = 17, compression), but not the hashing and the Fujisaki–Okamoto transform that turn it into the standardized KEM; it is not a validated implementation and must not be used to protect anything.

## 11. Diffusion models

**When / where:** Jascha Sohl-Dickstein, Eric A. Weiss, Niru Maheswaranathan and Surya Ganguli, "Deep Unsupervised Learning using Nonequilibrium Thermodynamics" (arXiv 12 March 2015); Jonathan Ho, Ajay Jain and Pieter Abbeel, UC Berkeley, "Denoising Diffusion Probabilistic Models" (arXiv June 2020; NeurIPS 2020).
**Atlas:** to be mapped · **Code:** [`Diffusion.java`](../../code/era-09-learning-at-scale/11-diffusion-models/) · **Page:** [topic 11](11-diffusion-models/README.md)

> **Field note.** Destroying a picture is easy: add a little noise, then a little more, a thousand times, and any picture becomes static. In 2015 Sohl-Dickstein and three colleagues, borrowing an idea from the physics of systems out of equilibrium, proposed generating pictures by learning to run that process backwards. Each backward step only has to remove a little noise, which a network can learn from examples, since the forward step is known exactly. The idea waited five years for its moment: in 2020 Ho, Jain and Abbeel simplified the training to a single instruction (here is a noisy picture; guess the noise that was added) and produced images as good as the best of the competing methods. Start from pure static, subtract the predicted noise step by step, and a picture appears that was never in the training set.

**What hurt:** generative models were hard to train (adversarial networks were unstable) or produced blurry samples; sampling from a complicated distribution of images had no simple recipe.
**The step forward:** a fixed forward process that adds Gaussian noise in many small steps, with a closed form for any step, and a network trained to predict the added noise; sampling runs the steps in reverse.

**Evidence and certainty**

- Sohl-Dickstein, Weiss, Maheswaranathan and Ganguli (submitted 12 March 2015): the idea "is to systematically and slowly destroy structure in a data distribution through an iterative forward diffusion process", then to "learn a reverse diffusion process that restores structure in data". **Documented** ([arXiv:1503.03585](https://arxiv.org/abs/1503.03585v1))
- Ho, Jain and Abbeel (UC Berkeley): diffusion models are "a class of latent variable models inspired by considerations from nonequilibrium thermodynamics", "straightforward to define and efficient to train"; on unconditional CIFAR10, "an Inception score of 9.46 and a state-of-the-art FID score of 3.17"; their parameterization "reveals an equivalence with denoising score matching over multiple noise levels during training" and with annealed Langevin dynamics when sampling. **Documented** ([arXiv:2006.11239, ar5iv edition](https://ar5iv.arxiv.org/html/2006.11239))
- The paper: the forward process "is fixed to a Markov chain that gradually adds Gaussian noise to the data according to a variance schedule" and "admits sampling xt at an arbitrary timestep t in closed form", q(xₜ | x₀) = N(√ᾱₜ x₀, (1 − ᾱₜ) I) with αₜ = 1 − βₜ and ᾱₜ their product; "We set T = 1000 for all experiments", with variances increasing linearly from β₁ = 10⁻⁴ to β_T = 0.02; the training objective is the squared error between the added noise and its prediction, with t uniform between 1 and T; sampling runs "for t = T, . . . , 1", adding fresh noise "if t > 1, else z = 0". **Documented** ([Ho, Jain and Abbeel 2020 (PDF)](https://arxiv.org/pdf/2006.11239v2))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [But how do AI images and videos actually work? \| Guest video by Welch Labs](https://www.youtube.com/watch?v=iv-5mZ_9CPY) | 3Blue1Brown | Diffusion from the ground up, a guest video on 3Blue1Brown's channel |
| Deeper | [Diffusion Models \| Paper Explanation \| Math Explained](https://www.youtube.com/watch?v=HoKDTa5jHvg) | Outlier | The mathematics of the 2020 paper |

**Read**

No secondary page was opened for this topic.

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Deep Unsupervised Learning using Nonequilibrium Thermodynamics](https://arxiv.org/abs/1503.03585v1) | J. Sohl-Dickstein, E. A. Weiss, N. Maheswaranathan, S. Ganguli (2015) | The idea |
| Scholar | [Denoising Diffusion Probabilistic Models](https://arxiv.org/pdf/2006.11239v2) | J. Ho, A. Jain, P. Abbeel (2020) | The simplified training and sampling |

**Gaps:** score-based models (Song and Ermon) and later work were not opened. The program uses the paper's noise schedule on two-dimensional points rather than images, and trains a small network to predict the noise.

## 12. FlashAttention

**When / where:** Maxim Milakov and Natalia Gimelshein, "Online normalizer calculation for softmax" (2018); Tri Dao, Daniel Y. Fu, Stefano Ermon and Christopher Ré (Stanford University) and Atri Rudra (University at Buffalo, SUNY), "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness" (arXiv:2205.14135, May 2022; NeurIPS 2022).
**Atlas:** to be mapped · **Code:** [`FlashAttention.java`](../../code/era-09-learning-at-scale/12-flashattention/) · **Page:** [topic 12](12-flashattention/README.md)

> **Field note.** Attention (topic 9) compares every word with every other word, so a text of n words needs a table of n × n scores, and the softmax seems to need the whole row at once. On a graphics processor the arithmetic is cheap; what is slow is moving numbers between the large main memory and the small fast memory beside the arithmetic units. The standard method wrote the whole n × n table out and read it back, several times. Dao and his colleagues at Stanford computed exactly the same answer without ever storing the table: cut the queries, keys and values into tiles that fit in the fast memory, and keep, for each row, a running maximum and a running sum, rescaling the partial result whenever a new maximum appears. The result is not an approximation; it is the same numbers, in a different order, with far less traffic.

**What hurt:** attention's memory grows with the square of the sequence length, and the time went into reading and writing that table in slow memory, not into arithmetic.
**The step forward:** an IO-aware exact algorithm: tiling with an online softmax (running maximum and sum), so attention is computed block by block in fast memory, with memory linear in the sequence length.

**Evidence and certainty**

- Dao, Fu, Ermon, Rudra and Ré (Stanford University; University at Buffalo, SUNY): an "IO-aware exact attention algorithm" that "uses tiling to reduce the number of memory reads/writes between GPU high bandwidth memory (HBM)" and on-chip SRAM; "15% end-to-end wall-clock speedup on BERT-large (seq. length 512)", "3× speedup on GPT-2 (seq. length 1K)", "2.4× speedup on long-range arena (seq. length 1K-4K)"; "less memory—linear in sequence length—than standard attention"; with a running maximum m(x) and sum ℓ(x), "we can compute softmax one block at a time"; an A100 has 40–80 GB of HBM at about 1.5–2.0 TB/s and "192KB of on-chip SRAM per each of 108 streaming multiprocessors" at about 19 TB/s; FlashAttention makes Θ(N²d²M⁻¹) accesses to HBM against Θ(Nd + N²) for standard attention (N the sequence length, d the head dimension, M the SRAM size); the softmax rescaling is credited to Milakov and Gimelshein (2018). **Documented** ([Dao et al., arXiv:2205.14135 (PDF)](https://arxiv.org/pdf/2205.14135))
- Published at NeurIPS 2022: "Transformers are slow and memory-hungry on long sequences, since the time and memory complexity of self-attention are" quadratic in the sequence length. **Documented** ([NeurIPS 2022 proceedings](https://proceedings.neurips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Deeper | [Flash Attention derived and coded from first principles with Triton (Python)](https://www.youtube.com/watch?v=zy8ChVd_oTM) | Umar Jamil | The online softmax derived, then coded |
| Scholar | [FlashAttention - Tri Dao \| Stanford MLSys #67](https://www.youtube.com/watch?v=gMOAud7hZg4) | Stanford MLSys Seminars | The first author, at Stanford's systems seminar |

**Read**

No secondary page was opened for this topic.

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/pdf/2205.14135) | T. Dao, D. Y. Fu, S. Ermon, A. Rudra, C. Ré (2022) | Tiling, the online softmax and the IO analysis |
| Scholar | [NeurIPS 2022 proceedings page](https://proceedings.neurips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html) | NeurIPS | Venue |

**Gaps:** Milakov and Gimelshein's paper and the later FlashAttention-2 and -3 were not opened. The program runs on a CPU, where the memory hierarchy is simulated by counting reads and writes of a "slow" array; it shows the exactness and the traffic, not GPU speed.

## 13. Algorithms that find algorithms

**When / where:** Alhussein Fawzi and colleagues, DeepMind, AlphaTensor, "Discovering faster matrix multiplication algorithms with reinforcement learning", *Nature*, 5 October 2022; Manuel Kauers and Jakob Moosbauer, Institute for Algebra, J. Kepler University Linz, "Flip Graphs for Matrix Multiplication" (arXiv, 2 December 2022); Google DeepMind, AlphaEvolve, 14 May 2025.
**Atlas:** to be mapped · **Code:** [`AlgorithmDiscovery.java`](../../code/era-09-learning-at-scale/13-algorithms-that-find-algorithms/) · **Page:** [topic 13](13-algorithms-that-find-algorithms/README.md)

> **Field note.** Strassen (Era 6) multiplied two 2 × 2 matrices with seven multiplications instead of eight, and for half a century people searched by hand and by computer for more such tricks. Every such algorithm is a way of writing one fixed three-dimensional table of zeros and ones, the matrix multiplication tensor, as a sum of simple pieces; the number of pieces is the number of multiplications. In 2022 DeepMind turned the search into a game for a version of AlphaZero (topic 8), and it found, among thousands of algorithms, one that multiplies 4 × 4 matrices with 47 multiplications when the arithmetic is modulo 2, where two levels of Strassen need 49. Two months later two mathematicians in Linz reached the same 47, and improved other records, with a far simpler method: start from the schoolbook algorithm and take random steps that rewrite two pieces at a time, keeping the sum unchanged, until a piece can be removed. In 2025 a system that evolves programs with a language model found 48 for 4 × 4 complex matrices. The algorithms these searches find can be checked by anyone, exactly, in a fraction of a second.

**What hurt:** the search space of matrix multiplication algorithms is astronomically large, and hand search had stalled for most sizes since the 1970s.
**The step forward:** cast algorithm design as finding a low-rank decomposition of a tensor, then search: by reinforcement learning (AlphaTensor), by random walks on a flip graph (Kauers and Moosbauer), or by evolving programs with automatic checks (AlphaEvolve). Every result is verified exactly.

**Evidence and certainty**

- DeepMind, 5 October 2022 (*Nature*): AlphaTensor is "the first artificial intelligence (AI) system for discovering novel, efficient, and provably correct algorithms"; the problem is cast as a "single-player game" played on a three-dimensional tensor; it "builds upon AlphaZero"; "AlphaTensor's algorithm improves on Strassen's two-level algorithm in a finite field for the first time since its discovery 50 years ago"; it finds "up to thousands of matrix multiplication algorithms for each size"; the algorithms found "multiply large matrices 10-20% faster than the commonly used algorithms on the same hardware". **Documented** ([Google DeepMind blog](https://deepmind.google/blog/discovering-novel-algorithms-with-alphatensor/))
- For 4 × 4 matrices over the two-element field, "47 multiplication operations, improving on the 49 operations" of Strassen applied twice; the paper is Fawzi et al., *Nature*, October 2022. **Documented** ([Wikipedia, AlphaTensor](https://en.wikipedia.org/wiki/AlphaTensor)); "AlphaTensor unexpectedly discovered a solution with 47 multiplication steps", "albeit restricted to mod 2 arithmetic", and other researchers "separately tweaked Deepmind's 96-step 5×5 algorithm down to 95 steps in mod 2 arithmetic". **Documented** ([Wikipedia, Matrix multiplication algorithm](https://en.wikipedia.org/wiki/Matrix_multiplication_algorithm))
- Kauers and Moosbauer (Institute for Algebra, J. Kepler University Linz; submitted 2 December 2022): a graph whose vertices are multiplication schemes and whose edges are flips (rewriting two rank-one terms; "This can be done for any two rank-one tensors that share a common factor") and reductions ("a reduction always leads to a vertex belonging to a lower level"); "Starting from the standard algorithm we easily find schemes of rank 23, matching the record set by Laderman in 1976" for 3 × 3; 4 × 4 over ℤ₂ at rank 47, matching Fawzi et al.; 5 × 5 over ℤ₂ at rank 95, from 96, "within seconds". **Documented** ([arXiv:2212.01175](https://arxiv.org/abs/2212.01175); [ar5iv edition](https://ar5iv.labs.arxiv.org/html/2212.01175))
- Google DeepMind, 14 May 2025: AlphaEvolve is "an evolutionary coding agent powered by large language models for general-purpose algorithm discovery and optimization", pairing Gemini models with "automated evaluators that verify answers"; it found a way to multiply 4 × 4 complex-valued matrices with "48 scalar multiplications", improving on Strassen's 1969 algorithm; a scheduling heuristic it found recovers "on average, 0.7% of Google's worldwide compute resources"; on "over 50 open problems" it matched the best known solutions in about 75% and improved them in 20%; in 11 dimensions it found "593 outer spheres", a new lower bound for the kissing number. **Documented** ([Google DeepMind blog](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/))
- The 47-multiplication algorithm itself is published as data: the file `factorizations_f2.npz` in DeepMind's AlphaTensor repository (code under Apache 2.0, other materials under CC BY 4.0), key `4,4,4`, three 16 × 47 factor matrices. The program embeds it and checks it. **Documented** (the repository, [github.com/google-deepmind/alphatensor](https://github.com/google-deepmind/alphatensor))

**Watch**

| Level | Video | Channel | Why |
|---|---|---|---|
| Start | [How AI Discovered a Faster Matrix Multiplication Algorithm](https://www.youtube.com/watch?v=fDAPJ7rvcUw) | Quanta Magazine | The story of AlphaTensor and the Linz response |
| Scholar | [Matej Balog - AlphaTensor: Discover faster matrix multiplication algorithms with RL - IPAM at UCLA](https://www.youtube.com/watch?v=QJT3LszR2pA) | Institute for Pure & Applied Mathematics (IPAM) | A talk by one of AlphaTensor's authors |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Discovering novel algorithms with AlphaTensor](https://deepmind.google/blog/discovering-novel-algorithms-with-alphatensor/) | Google DeepMind (2022) | The announcement |
| Start | [AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) | Google DeepMind (2025) | The 2025 system |
| Deeper | [Matrix multiplication algorithm](https://en.wikipedia.org/wiki/Matrix_multiplication_algorithm) | Wikipedia | Where AlphaTensor's results sit among the records |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Flip Graphs for Matrix Multiplication](https://arxiv.org/abs/2212.01175) | M. Kauers, J. Moosbauer (2022) | The random-walk method the program uses |
| Scholar | [AlphaTensor repository](https://github.com/google-deepmind/alphatensor) | Google DeepMind | The discovered algorithms, as data |

**Gaps:** the *Nature* paper and AlphaEvolve's technical report were not opened; the 2026 work that lowered the exponent of matrix multiplication with AlphaEvolve's help is recorded in Era 6's catalog (topic 5). The program verifies AlphaTensor's 47-term algorithm and runs a flip-graph search on 2 × 2 and 3 × 3 matrices; it does not reproduce the 4 × 4 search or any reinforcement learning.

## What the era leaves behind

- **Old ideas at a new scale.** Convolutional networks (2), backpropagation and gradient descent (5), Monte Carlo playouts (8) and Markov chains of noise (11) were all decades old; graphics processors and large datasets made them work.
- **Making depth trainable.** Rectified units and dropout (2), adaptive steps (5) and residual connections (7) are what let a gradient pass through a hundred layers.
- **Text as numbers.** Word vectors (3) give words a geometry; byte-pair encoding (6) cuts text into tokens; attention (9) lets every token consult every other; FlashAttention (12) makes that affordable.
- **Agreement made teachable.** Raft (4) is Paxos (Era 8) redesigned to be understood.
- **Cryptography for the next computer.** Computing on encrypted data (1) and key exchange that a quantum computer should not break (10) both rest on noisy linear algebra.
- **The tool turns on itself.** Searches guided by learning and by random walks find algorithms that people had not (13), and every one of them can be checked exactly.
