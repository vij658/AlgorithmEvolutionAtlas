"""Era 6 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=6,
    folder="era-06-hard-problems-and-public-keys",
    title="Hard Problems and Public Keys",
    span="1965 to 1978",
    lede="In the fifth era, the species learned to write programs well. In this one, programs run side by side, "
         "talk across networks and keep secrets, and the species learns that some problems may have no fast method at all.",
    intro="Thirteen steps, from the fast Fourier transform of 1965 to Lamport's clocks of 1978. Along the way, programs "
          "share memory safely, are built from objects, search with an estimate, store data in tables and trees made "
          "for disks, find that a whole family of problems stands or falls together, exchange keys in public, search "
          "and compress text without a model, and agree on what \"before\" means.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "fast-fourier-transform", "The Fast Fourier Transform", "1964–1965", "Cooley and Tukey's FFT", "e6_01_fft", "FastFourier"),
    (2, "semaphores", "Mutual Exclusion and the Semaphore", "1962–1965", "Dijkstra's semaphore", "e6_02_semaphores", "Semaphores"),
    (3, "objects", "Objects, Classes and Subclasses", "1961–1967", "Simula's objects", "e6_03_objects", "Objects"),
    (4, "a-star", "A*: Search Guided by an Estimate", "1968", "A* search", "e6_04_astar", "AStar"),
    (5, "strassen", "Fast Matrix Multiplication", "1969", "Strassen's seven products", "e6_05_strassen", "Strassen"),
    (6, "relational-model", "The Relational Model of Data", "1970", "Codd's relations", "e6_06_relational", "Relational"),
    (7, "b-trees", "B-Trees", "1969–1972", "B-trees", "e6_07_btrees", "BTrees"),
    (8, "np-completeness", "NP-Completeness", "1971–1973", "NP-completeness", "e6_08_np", "NpComplete"),
    (9, "depth-first-search", "Depth-First Search", "1970–1974", "Depth-first search", "e6_09_dfs", "DepthFirst"),
    (10, "public-key-cryptography", "Public-Key Cryptography", "1976–1977", "Public keys", "e6_10_publickey", "PublicKey"),
    (11, "string-search", "Fast String Searching", "1969–1977", "KMP and Boyer–Moore", "e6_11_strings", "StringSearch"),
    (12, "lempel-ziv", "Universal Compression", "1977–1978", "Lempel–Ziv", "e6_12_lz", "LempelZiv"),
    (13, "logical-clocks", "Logical Clocks", "1978", "Lamport's clocks", "e6_13_clocks", "LogicalClocks"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim of a documented line of descent.
_C = [30, 395, 760]
MAP = dict(
    w=1000, h=840, bw=210, bh=76,
    at={1: (_C[0], 20), 2: (_C[1], 20), 3: (_C[2], 20),
        5: (_C[0], 200), 13: (_C[1], 200), 4: (_C[2], 200),
        10: (_C[0], 380), 8: (_C[1], 380), 9: (_C[2], 380),
        6: (_C[0], 560), 7: (_C[1], 560), 11: (_C[2], 560),
        12: (_C[2], 740)},
    color={8: "red", 10: "red"},
    edges=[
        (1, 5, "both beat the obvious count", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (2, 13, "⊕ mutual exclusion by messages", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (4, 9, "both search a graph", dict(ports=("bottom", "top"), dashed=True, dx=-8, anchor="end")),
        (5, 10, "Strassen's prime test makes keys", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (8, 10, "hardness as security", dict(ports=("left", "right"), dashed=True, dy=-10)),
        (7, 6, "B-trees index the tables", dict(ports=("left", "right"), dashed=True, dy=-10)),
        (11, 12, "⊕ search for the longest match", dict(ports=("bottom", "top"), dx=-8, anchor="end")),
    ],
    caption="An arrow means the later development reuses the earlier idea; it is not a claim that one inventor learned "
            "from the other. Dashed lines join related developments: two ways of beating the obvious operation count, "
            "two graph searches, the RSA paper's use of Solovay and Strassen's primality test, public keys that rely on "
            "problems believed hard, and the B-tree as the index under relational tables. Several boxes build on earlier "
            "eras: the FFT on Gauss (Era 3), objects on the subroutine (Era 5), A* on Dijkstra's shortest paths (Era 5), "
            "NP-completeness on Turing machines (Era 4) and Edmonds's \"good\" algorithms (Era 5), and Lempel and Ziv on "
            "Shannon (Era 4) and Huffman (Era 5).",
)


def timeline_events():
    return [(t[3], t[4]) for t in TOPICS]
