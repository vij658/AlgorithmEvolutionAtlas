"""Era 8 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=8,
    folder="era-08-the-web-the-genome-and-the-ledger",
    title="The Web, the Genome and the Ledger",
    span="1995 to 2008",
    lede="In the seventh era, the species learned to use chance, to keep networks working and to make machines that "
         "learn. In this one its network becomes a Web of tens of millions of pages, its laboratories read its own "
         "genome in fragments, and its data arrives faster than it can be kept, so it learns to rank, sketch, split "
         "and agree at a scale no earlier method was built for.",
    intro="Thirteen steps, from support vector machines in 1995 to Bitcoin in 2008. Along the way, a classifier "
          "finds the widest street between two kinds of examples, a hard problem gets a provable 88%, a few "
          "kilobytes summarize a stream of millions, servers join and leave without reshuffling the Web, near-copies "
          "are found by their smallest hashes, a network learns to remember, links rank pages, a part-time "
          "parliament agrees, a genome is read as an Eulerian path, primality is settled without chance, thousands of "
          "computers share one job, a signal is rebuilt from a handful of measurements, and strangers keep one "
          "ledger by doing work.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "support-vector-machines", "Support Vector Machines", "1992–1995", "Support vector machines", "e8_01_svm", "SupportVectorMachines"),
    (2, "max-cut", "Approximation by Semidefinite Programming", "1994–1995", "Goemans–Williamson", "e8_02_maxcut", "GoemansWilliamson"),
    (3, "streaming-sketches", "Streaming Sketches", "1996", "Streaming sketches", "e8_03_sketches", "StreamingSketches"),
    (4, "consistent-hashing", "Consistent Hashing", "1997", "Consistent hashing", "e8_04_consistent", "ConsistentHashing"),
    (5, "minhash", "MinHash and Locality-Sensitive Hashing", "1997–1998", "MinHash", "e8_05_minhash", "MinHashLsh"),
    (6, "lstm", "Long Short-Term Memory", "1997", "LSTM", "e8_06_lstm", "LongShortTermMemory"),
    (7, "pagerank", "PageRank", "1998", "PageRank", "e8_07_pagerank", "PageRank"),
    (8, "paxos", "Paxos", "1989–1998", "Paxos", "e8_08_paxos", "Paxos"),
    (9, "genome-assembly", "Genome Assembly with de Bruijn Graphs", "1995–2001", "Genome assembly", "e8_09_assembly", "GenomeAssembly"),
    (10, "primes-is-in-p", "PRIMES is in P", "2002", "AKS primality", "e8_10_aks", "AksPrimality"),
    (11, "mapreduce", "MapReduce", "2004", "MapReduce", "e8_11_mapreduce", "MapReduce"),
    (12, "compressed-sensing", "Compressed Sensing", "2004–2006", "Compressed sensing", "e8_12_cs", "CompressedSensing"),
    (13, "bitcoin", "Bitcoin's Proof-of-Work Ledger", "2008", "Bitcoin", "e8_13_bitcoin", "Bitcoin"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim of a documented line of descent.
_C = [30, 395, 760]
MAP = dict(
    w=1000, h=840, bw=210, bh=76,
    at={1: (_C[0], 20), 2: (_C[1], 20), 3: (_C[2], 20),
        6: (_C[0], 200), 12: (_C[1], 200), 5: (_C[2], 200),
        4: (_C[0], 380), 7: (_C[1], 380), 9: (_C[2], 380),
        11: (_C[0], 560), 8: (_C[1], 560), 10: (_C[2], 560),
        13: (_C[1], 740)},
    color={7: "red", 13: "red"},
    edges=[
        (1, 6, "both learn from examples", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (2, 12, "a convex relaxation", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (3, 5, "small random summaries", dict(ports=("bottom", "top"), dashed=True, dx=-8, anchor="end")),
        (5, 9, "texts cut into k-letter words", dict(ports=("bottom", "top"), dashed=True, dx=-8, anchor="end")),
        (4, 11, "spread over machines", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (7, 11, "PageRank in rounds of map and reduce", dict(ports=("bottom:0.1", "top:0.9"), dashed=True, at=0.2, dx=26, anchor="start")),
        (8, 13, "agreeing on one history", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
    ],
    caption="Dashed lines join related developments; none of them is a claim that one inventor learned from the other. "
            "Most boxes build on earlier eras: support vector machines and LSTM on the perceptron and backpropagation "
            "(Eras 5 and 7); Goemans and Williamson on NP-completeness (Era 6) and linear programming (Era 7); "
            "sketches, consistent hashing and MinHash on hashing (Era 5) and fingerprints (Era 7); PageRank on Markov "
            "chains (Era 4); Paxos on the Byzantine generals and logical clocks (Eras 6 and 7); genome assembly on "
            "Euler's bridges (Era 3); PRIMES in P on the randomized primality tests of Era 6; compressed sensing on "
            "linear programming (Era 7); Bitcoin on Merkle's trees and Byzantine agreement (Era 7).",
)


def timeline_events():
    return [(t[3], t[4]) for t in TOPICS]
