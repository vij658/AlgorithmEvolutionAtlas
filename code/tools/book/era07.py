"""Era 7 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=7,
    folder="era-07-randomness-networks-and-learning",
    title="Randomness, Networks and Learning",
    span="1979 to 1995",
    lede="In the sixth era, the species learned that some problems may have no fast method. In this one, it learns to "
         "use chance on purpose, to keep networks of computers working when parts fail or lie, and to make machines "
         "that learn from examples.",
    intro="Thirteen steps, from Khachiyan's polynomial-time linear programming of 1979 to AdaBoost in 1995. Along the "
          "way, one short hash vouches for a mountain of data, computers agree despite traitors, a search cools like "
          "metal, a tree rearranges itself as it is used, a proof convinces without revealing, networks of simple "
          "units learn, stars are grouped by a tree of cubes, text is searched by fingerprints and sorted by its "
          "rotations, the Internet learns to share its links, and a quantum computer is shown to factor quickly, "
          "on paper.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "linear-programming", "Linear Programming in Polynomial Time", "1979–1984", "Khachiyan and Karmarkar", "e7_01_lp", "LinearProgramming"),
    (2, "merkle-trees", "Merkle's Hash Trees", "1979", "Merkle trees", "e7_02_merkle", "MerkleTrees"),
    (3, "byzantine-generals", "The Byzantine Generals", "1980–1982", "Byzantine agreement", "e7_03_byzantine", "ByzantineGenerals"),
    (4, "simulated-annealing", "Simulated Annealing", "1983–1985", "Simulated annealing", "e7_04_annealing", "SimulatedAnnealing"),
    (5, "splay-trees", "Splay Trees and Amortized Analysis", "1985", "Splay trees", "e7_05_splay", "SplayTrees"),
    (6, "zero-knowledge", "Zero-Knowledge Proofs", "1985–1986", "Zero knowledge", "e7_06_zk", "ZeroKnowledge"),
    (7, "backpropagation", "Backpropagation", "1970–1986", "Backpropagation", "e7_07_backprop", "Backpropagation"),
    (8, "barnes-hut", "The Barnes–Hut Tree Code", "1986", "Barnes–Hut", "e7_08_barneshut", "BarnesHut"),
    (9, "karp-rabin", "Karp–Rabin Fingerprints", "1985–1987", "Karp–Rabin", "e7_09_karprabin", "KarpRabin"),
    (10, "tcp-congestion-control", "TCP Congestion Control", "1986–1989", "Congestion control", "e7_10_tcp", "TcpCongestion"),
    (11, "shor-factoring", "Shor's Factoring Algorithm", "1994", "Shor's algorithm", "e7_11_shor", "ShorFactoring"),
    (12, "burrows-wheeler", "The Burrows–Wheeler Transform", "1983–1994", "Burrows–Wheeler", "e7_12_bwt", "BurrowsWheeler"),
    (13, "adaboost", "AdaBoost", "1995–1997", "AdaBoost", "e7_13_adaboost", "AdaBoost"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim of a documented line of descent.
_C = [30, 395, 760]
MAP = dict(
    w=1000, h=840, bw=210, bh=76,
    at={1: (_C[0], 20), 2: (_C[1], 20), 3: (_C[2], 20),
        4: (_C[0], 200), 9: (_C[1], 200), 10: (_C[2], 200),
        7: (_C[0], 380), 12: (_C[1], 380), 5: (_C[2], 380),
        13: (_C[0], 560), 6: (_C[1], 560), 8: (_C[2], 560),
        11: (_C[1], 740)},
    color={7: "red", 11: "red"},
    edges=[
        (1, 4, "lowering a cost: exact, then by chance", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (2, 9, "short hashes for long data", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (3, 10, "surviving bad parts", dict(ports=("bottom", "top"), dashed=True, dx=-8, anchor="end")),
        (4, 7, "both descend a cost", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (9, 12, "both find patterns in text", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (5, 8, "trees shaped by the data", dict(ports=("bottom", "top"), dashed=True, dx=-8, anchor="end")),
        (7, 13, "both learn from examples", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (6, 11, "both turn on what is hard to compute", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
    ],
    caption="Dashed lines join related developments; none of them is a claim that one inventor learned from the other. "
            "Most boxes build on earlier eras: polynomial-time linear programming on the simplex method (Era 4); "
            "Merkle's trees and zero-knowledge proofs on public keys and NP-completeness (Era 6); the Byzantine "
            "generals on logical clocks (Era 6); annealing on Monte Carlo (Era 4); splay trees on balanced trees "
            "(Era 5); backpropagation and AdaBoost on the perceptron (Era 5); Karp and Rabin on fast string searching "
            "(Era 6); Shor on the fast Fourier transform and RSA (Era 6); Burrows and Wheeler on Huffman (Era 5) and "
            "Lempel and Ziv (Era 6).",
)


def timeline_events():
    return [(t[3], t[4]) for t in TOPICS]
