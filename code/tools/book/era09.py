"""Era 9 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=9,
    folder="era-09-learning-at-scale",
    title="Learning at Scale",
    span="2009 to 2026",
    lede="In the eighth era, the species built a Web, read its genome and agreed on a ledger. In this one an old idea, "
         "the network that learns from examples, suddenly works at scale, and much of the era's algorithmic work goes "
         "into making that learning possible; alongside it the species learns to compute on data it cannot read, "
         "prepares its cryptography for quantum computers, and sets its machines to search for algorithms.",
    intro="Thirteen steps, from fully homomorphic encryption in 2009 to algorithms found by machines in 2022 and 2025. "
          "Along the way, a computer adds and multiplies numbers it cannot see, a network learns to recognize "
          "photographs, words become vectors, a consensus algorithm is designed to be understood, an optimizer sets "
          "its own step sizes, text is cut into tokens, a shortcut lets a signal through a hundred layers, random "
          "games beat the best Go players, attention replaces recurrence, a key exchange is built to survive quantum "
          "computers, pictures are drawn out of noise, attention is computed without its table, and a search finds a "
          "matrix multiplication with 47 products where people had found 49.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "homomorphic-encryption", "Fully Homomorphic Encryption", "2009–2010", "Homomorphic encryption", "e9_01_fhe", "FullyHomomorphic"),
    (2, "deep-convolutional-networks", "Deep Convolutional Networks", "2012", "AlexNet", "e9_02_convnet", "ConvNet"),
    (3, "word-embeddings", "Word Embeddings", "2013", "word2vec", "e9_03_word2vec", "WordEmbeddings"),
    (4, "raft", "Raft", "2014", "Raft", "e9_04_raft", "Raft"),
    (5, "adam", "Adam", "2014", "Adam", "e9_05_adam", "Adam"),
    (6, "byte-pair-encoding", "Byte-Pair Encoding for Words", "2015", "Byte-pair encoding", "e9_06_bpe", "BytePairEncoding"),
    (7, "residual-networks", "Residual Networks", "2015", "ResNet", "e9_07_resnet", "ResidualNetworks"),
    (8, "monte-carlo-tree-search", "Monte Carlo Tree Search and AlphaGo", "2006–2016", "AlphaGo", "e9_08_mcts", "MonteCarloTreeSearch"),
    (9, "transformer", "The Transformer", "2017", "Transformer", "e9_09_transformer", "Transformer"),
    (10, "lattice-cryptography", "Lattice Cryptography and ML-KEM", "2017–2024", "ML-KEM", "e9_10_mlkem", "LatticeKem"),
    (11, "diffusion-models", "Diffusion Models", "2015–2020", "Diffusion models", "e9_11_diffusion", "Diffusion"),
    (12, "flashattention", "FlashAttention", "2022", "FlashAttention", "e9_12_flash", "FlashAttention"),
    (13, "algorithms-that-find-algorithms", "Algorithms That Find Algorithms", "2022–2025", "AlphaTensor", "e9_13_discovery", "AlgorithmDiscovery"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim of a documented line of descent.
_C = [30, 395, 760]
MAP = dict(
    w=1000, h=1020, bw=210, bh=76,
    at={1: (_C[0], 20), 2: (_C[1], 20), 6: (_C[2], 20),
        10: (_C[0], 200), 7: (_C[1], 200), 3: (_C[2], 200),
        4: (_C[0], 380), 5: (_C[1], 380), 9: (_C[2], 380),
        8: (_C[0], 560), 11: (_C[1], 560), 12: (_C[2], 560),
        13: (_C[0], 740)},
    color={9: "red", 13: "red"},
    edges=[
        (1, 10, "noisy linear algebra", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (2, 7, "deeper networks", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (6, 3, "tokens become vectors", dict(ports=("bottom", "top"), dashed=True, dx=-8, anchor="end")),
        (3, 9, "each token a vector", dict(ports=("bottom", "top"), dashed=True, dx=-8, anchor="end")),
        (7, 9, "a residual around every block", dict(ports=("right", "top:0.15"), dashed=True, at=0.35, dy=-8, anchor="start")),
        (9, 12, "the same attention, less traffic", dict(ports=("bottom", "top"), dashed=True, dx=-8, anchor="end")),
        (8, 13, "AlphaZero, playing a new game", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
    ],
    caption="Dashed lines join related developments; none of them is a claim that one inventor learned from the other. "
            "Most boxes build on earlier eras: homomorphic encryption and ML-KEM on public-key cryptography (Era 6) "
            "and learning with errors; AlexNet, Adam and residual networks on backpropagation (Era 7) and the LSTM "
            "(Era 8); word vectors on Huffman's codes (Era 5) for their hierarchical softmax; Raft on Paxos (Era 8); "
            "byte-pair encoding on universal compression (Era 6); Monte Carlo tree search on Monte Carlo (Era 4); "
            "diffusion models on Markov chains (Era 4); the search for matrix multiplication algorithms on Strassen "
            "(Era 6).",
)


def timeline_events():
    return [(t[3], t[4]) for t in TOPICS]
