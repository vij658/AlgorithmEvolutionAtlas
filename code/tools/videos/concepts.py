"""Every concept the video list looks for, in the book's order: era by era, topic by topic, and inside each topic from
the simplest idea to the most advanced. Each string is also the search phrase. Edit freely: a concept's id is its
topic plus its position, so append new concepts at the end of a topic's list to keep earlier ids stable."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "book"))

CHAPTER_1 = ["adding two numbers", "carrying in column addition", "why the addition algorithm works place value", "binary adder circuit full adder"]

TOPICS = {
    # Era 1
    "tally-marks": ["one-to-one correspondence counting", "tally marks", "Ishango bone", "Lebombo bone"],
    "grouping-and-the-first-carry": ["Egyptian hieroglyphic numerals", "Sumerian cuneiform numbers", "grouping and carrying in ancient addition"],
    "babylonian-place-value": ["Babylonian base 60 numbers", "place value number system", "Babylonian reciprocal tables division"],
    "square-root-of-two": ["square root of 2 irrational", "YBC 7289 Babylonian tablet", "Babylonian method square root", "Heron's method square root"],
    "egyptian-doubling": ["Egyptian multiplication doubling", "Rhind mathematical papyrus", "Russian peasant multiplication", "exponentiation by squaring"],
    "counting-boards": ["how to use an abacus", "Roman abacus counting board", "Salamis tablet"],
    "euclids-algorithm": ["greatest common divisor", "Euclidean algorithm", "Euclid's Elements", "Euclidean algorithm running time Lamé"],
    "archimedes-pi": ["what is pi", "Archimedes approximation of pi polygons", "Archimedes Measurement of a Circle"],
    "sieve-of-eratosthenes": ["prime numbers explained", "sieve of Eratosthenes", "sieve of Eratosthenes time complexity"],
    # Era 2
    "fangcheng": ["Nine Chapters on the Mathematical Art", "Gaussian elimination", "fangcheng counting rods matrix"],
    "ptolemys-chords": ["chord trigonometry", "Ptolemy's table of chords Almagest", "Ptolemy's theorem"],
    "chinese-remainder-problem": ["modular arithmetic clock", "Chinese remainder theorem", "Sunzi Suanjing remainder problem"],
    "zero-becomes-a-number": ["history of zero", "Brahmagupta rules for zero", "Hindu-Arabic numeral system"],
    "chakravala": ["Pell's equation", "Brahmagupta identity composition", "chakravala method Bhaskara"],
    "algorism-and-al-jabr": ["al-Khwarizmi and the word algorithm", "al-jabr completing the square", "al-Khwarizmi Hindu numerals book algorism"],
    "frequency-analysis": ["Caesar cipher", "frequency analysis cryptography", "Al-Kindi cryptanalysis"],
    "liber-abaci": ["Fibonacci sequence rabbits", "Fibonacci Liber Abaci Hindu-Arabic numerals Europe", "Fibonacci numbers golden ratio"],
    "qin-jiushao": ["Horner's method polynomial evaluation", "Qin Jiushao mathematics", "Ruffini Horner root finding digit by digit"],
    "madhava-series": ["infinite series for pi", "Madhava Leibniz series", "Kerala school of mathematics"],
    "al-kashi-pi": ["Jamshid al-Kashi pi", "al-Kashi decimal fractions", "computing pi with polygons by hand"],
    # Era 3
    "cardanos-cubic": ["solving cubic equations", "Cardano's formula", "Tartaglia del Ferro cubic history", "imaginary numbers casus irreducibilis"],
    "logarithms": ["what are logarithms", "John Napier logarithms", "Henry Briggs logarithm tables", "how a slide rule works"],
    "mechanical-carry": ["Pascaline calculator", "Schickard calculating clock", "Leibniz stepped reckoner"],
    "problem-of-points": ["problem of points", "Pascal Fermat letters probability", "Pascal's triangle", "expected value"],
    "newtons-method": ["Newton's method root finding", "Newton-Raphson method", "Newton fractal"],
    "binary-arithmetic": ["binary numbers", "binary addition", "Leibniz binary I Ching"],
    "konigsberg-bridges": ["seven bridges of Königsberg", "Euler path graph theory", "Hierholzer algorithm Euler circuit"],
    "least-squares": ["least squares regression", "Gauss orbit of Ceres", "Legendre Gauss least squares priority", "normal equations least squares"],
    "gauss-fft": ["Fourier series", "discrete Fourier transform", "Gauss and the history of the FFT"],
    "difference-engine": ["method of finite differences", "Babbage difference engine", "Difference Engine No. 2 Science Museum"],
    "note-g": ["Ada Lovelace", "Babbage Analytical Engine", "Bernoulli numbers Note G"],
    "boolean-algebra": ["Boolean algebra", "truth tables logic gates", "George Boole Laws of Thought"],
    "hollerith-tabulator": ["punched cards", "Hollerith tabulating machine", "1890 United States census tabulation"],
    # Era 4
    "hilberts-questions": ["Hilbert's problems", "Entscheidungsproblem", "Hilbert's tenth problem"],
    "runge-kutta": ["Euler method differential equations", "Runge-Kutta method", "RK4 explained"],
    "markov-chains": ["Markov chains", "Markov Eugene Onegin letters", "stationary distribution Markov chain"],
    "cheapest-network": ["minimum spanning tree", "Borůvka's algorithm", "Prim Jarník algorithm"],
    "godel-numbering": ["Gödel numbering", "Gödel's incompleteness theorems", "self-reference paradox logic"],
    "lambda-calculus": ["lambda calculus", "Church numerals", "Y combinator"],
    "turing-machines": ["Turing machine", "halting problem", "universal Turing machine"],
    "breaking-enigma": ["Enigma machine", "Rejewski Polish cipher bureau Enigma", "Turing Bombe"],
    "stored-program": ["von Neumann architecture", "EDVAC stored program", "merge sort"],
    "monte-carlo": ["Monte Carlo method", "Ulam von Neumann Monte Carlo ENIAC", "middle square random number generator"],
    "simplex-method": ["linear programming", "simplex method", "George Dantzig"],
    "information-theory": ["information entropy", "Shannon information theory", "Shannon master's thesis switching circuits"],
    "hamming-codes": ["error correcting codes", "Hamming code", "parity bit"],
    # Era 5
    "the-subroutine": ["functions in programming", "call stack", "EDSAC Wheeler jump subroutine"],
    "regular-expressions": ["regular expressions", "finite automata", "Thompson construction NFA", "Kleene star regular languages"],
    "huffman-codes": ["data compression basics", "Huffman coding", "prefix codes"],
    "hashing": ["hash tables", "hash function", "linear probing collisions"],
    "dynamic-programming": ["dynamic programming", "memoization", "Bellman equation"],
    "linked-lists": ["linked lists", "garbage collection", "mark and sweep McCarthy Lisp"],
    "shortest-paths": ["shortest path problem graphs", "Dijkstra's algorithm", "Edsger Dijkstra interview"],
    "the-compiler": ["how compilers work", "FORTRAN history John Backus", "Backus-Naur form grammar", "parsing expressions"],
    "perceptron": ["perceptron", "Rosenblatt Mark I perceptron", "perceptron convergence theorem"],
    "quicksort": ["quicksort", "Hoare partition scheme", "Tony Hoare quicksort story"],
    "avl-trees": ["binary search trees", "AVL tree rotations", "self-balancing binary search tree"],
    "heapsort": ["binary heap", "heapsort", "priority queue"],
    "matching": ["bipartite matching", "Edmonds blossom algorithm", "Edmonds paths trees and flowers polynomial time"],
    # Era 6
    "fast-fourier-transform": ["fast Fourier transform", "Cooley-Tukey FFT", "FFT butterfly diagram"],
    "semaphores": ["race condition", "mutual exclusion", "semaphores Dijkstra", "dining philosophers problem"],
    "objects": ["object-oriented programming", "Simula programming language", "inheritance classes subclasses"],
    "a-star": ["A* search algorithm", "admissible heuristic", "Shakey the robot"],
    "strassen": ["matrix multiplication", "Strassen algorithm", "matrix multiplication exponent omega"],
    "relational-model": ["relational database", "Codd relational model", "relational algebra SQL joins"],
    "b-trees": ["B-tree", "B-tree insertion node split", "database index"],
    "np-completeness": ["P vs NP", "NP-completeness", "Cook-Levin theorem", "Karp's 21 NP-complete problems"],
    "depth-first-search": ["depth-first search", "Tarjan strongly connected components", "articulation points biconnected components"],
    "public-key-cryptography": ["public key cryptography", "Diffie-Hellman key exchange", "RSA encryption", "probabilistic primality test"],
    "string-search": ["string matching", "Knuth-Morris-Pratt algorithm", "Boyer-Moore algorithm"],
    "lempel-ziv": ["LZ77 compression", "LZW compression", "DEFLATE gzip"],
    "logical-clocks": ["Lamport clocks", "happened-before relation", "vector clocks"],
    # Era 7
    "linear-programming": ["linear programming", "ellipsoid method", "interior point method Karmarkar"],
    "merkle-trees": ["SHA-256 hash function", "Merkle tree", "Merkle proof"],
    "byzantine-generals": ["Byzantine generals problem", "Byzantine fault tolerance", "Lamport Shostak Pease"],
    "simulated-annealing": ["traveling salesman problem", "simulated annealing", "Metropolis algorithm"],
    "splay-trees": ["amortized analysis", "splay trees", "Sleator Tarjan dynamic optimality"],
    "zero-knowledge": ["zero-knowledge proof", "graph coloring zero knowledge proof", "Goldwasser Micali interactive proofs"],
    "backpropagation": ["neural networks", "gradient descent", "backpropagation", "chain rule calculus"],
    "barnes-hut": ["n-body simulation", "Barnes-Hut algorithm", "quadtree octree"],
    "karp-rabin": ["rolling hash", "Rabin-Karp algorithm", "fingerprinting hashing"],
    "tcp-congestion-control": ["how TCP works", "TCP congestion control", "TCP slow start AIMD"],
    "shor-factoring": ["quantum computing basics", "Shor's algorithm", "quantum Fourier transform", "period finding factoring"],
    "burrows-wheeler": ["Burrows-Wheeler transform", "move-to-front transform", "FM-index"],
    "adaboost": ["ensemble learning", "AdaBoost", "boosting weak learners"],
    # Era 8
    "support-vector-machines": ["support vector machine", "maximum margin classifier", "kernel trick", "soft margin SVM"],
    "max-cut": ["approximation algorithms", "max cut problem", "semidefinite programming", "Goemans-Williamson algorithm"],
    "streaming-sketches": ["streaming algorithms", "Count-Min sketch", "HyperLogLog", "AMS sketch frequency moments"],
    "consistent-hashing": ["consistent hashing", "distributed hash table", "Akamai consistent hashing"],
    "minhash": ["Jaccard similarity", "MinHash", "locality-sensitive hashing"],
    "lstm": ["recurrent neural network", "vanishing gradient problem", "LSTM"],
    "pagerank": ["PageRank", "random surfer Markov chain", "power iteration eigenvector"],
    "paxos": ["distributed consensus", "Paxos algorithm", "Lamport Part-Time Parliament"],
    "genome-assembly": ["DNA sequencing", "genome assembly", "de Bruijn graph", "Human Genome Project"],
    "primes-is-in-p": ["primality testing", "Fermat's little theorem Carmichael numbers", "AKS primality test"],
    "mapreduce": ["distributed computing", "MapReduce", "Hadoop"],
    "compressed-sensing": ["sparsity signal processing", "compressed sensing", "L1 minimization"],
    "bitcoin": ["how bitcoin works", "double spending", "proof of work", "blockchain"],
}


def principles():
    root = Path(__file__).resolve().parents[2] / "principles"
    out = []
    for part in sorted(root.iterdir()):
        if part.is_dir():
            for d in sorted(part.iterdir()):
                if d.is_dir() and d.name[:2].isdigit():
                    out.append((int(d.name[:2]), d.name[3:].replace("-", " ")))
    return out


def all_concepts():
    """[(cid, group, group_title, topic_num, slug, topic_title, folder, concept)] in reading order."""
    import eras
    rows = []
    for i, c in enumerate(CHAPTER_1, 1):
        rows.append((f"ch1-c{i}", "ch1", "Chapter 1: Two numbers, one answer", 0, "chapter-01-adding-two-numbers", "Adding two numbers",
                     "era-01-the-first-algorithms/chapter-01-adding-two-numbers", c))
    for e in eras.ERAS:
        n = e.ERA["num"]
        for t in e.TOPICS:
            num, slug, title = t[0], t[1], t[2]
            concepts = TOPICS.get(slug)
            if not concepts:
                raise SystemExit(f"no concepts for {slug}")
            for i, c in enumerate(concepts, 1):
                rows.append((f"e{n}-{num:02d}-c{i}", f"e{n}", f"Era {n}: {e.ERA['title']}", num, slug, title,
                             f"{e.ERA['folder']}/{num:02d}-{slug}", c))
    for num, name in principles():
        rows.append((f"p-{num:02d}", "p", "The principles catalog", num, name.replace(" ", "-"), name[:1].upper() + name[1:], None, name))
    return rows
