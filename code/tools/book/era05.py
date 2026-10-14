"""Era 5 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=5,
    folder="era-05-the-programmers-craft",
    title="The Programmer's Craft",
    span="1949 to 1965",
    lede="In the fourth era, the species learned what a procedure is and built machines that keep procedures in "
         "memory. In this one, they learn how to write procedures well, and invent the tools of a new craft.",
    intro="Thirteen steps, from the subroutine of 1949 to Edmonds's \"good\" algorithms of 1965. Along the way, "
          "programs are built from shared parts and translated by the machine itself, memory is organised into lists, "
          "tables, trees and heaps, a machine learns from examples, and efficiency gets a definition.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "the-subroutine", "The Subroutine", "1949–1952", "Wheeler's subroutine", "e5_01_subroutine", "Subroutines"),
    (2, "regular-expressions", "Regular Expressions", "1951", "Kleene's regular events", "e5_02_regex", "RegularExpressions"),
    (3, "huffman-codes", "Huffman's Codes", "1951–1952", "Huffman's codes", "e5_03_huffman", "HuffmanCodes"),
    (4, "hashing", "Hashing", "1953–1957", "Hashing", "e5_04_hashing", "Hashing"),
    (5, "dynamic-programming", "Dynamic Programming", "1952–1957", "Bellman's dynamic programming", "e5_05_dynamic", "DynamicProgramming"),
    (6, "linked-lists", "Linked Lists and Garbage Collection", "1956–1960", "Lists and garbage collection", "e5_06_lists", "ListsAndGarbage"),
    (7, "shortest-paths", "Dijkstra's Shortest Paths", "1956–1959", "Dijkstra's shortest paths", "e5_07_dijkstra", "ShortestPaths"),
    (8, "the-compiler", "The Compiler, and a Grammar for Languages", "1954–1960", "FORTRAN and BNF", "e5_08_compiler", "Compiler"),
    (9, "perceptron", "Rosenblatt's Perceptron", "1957–1958", "The perceptron", "e5_09_perceptron", "Perceptron"),
    (10, "quicksort", "Hoare's Quicksort", "1959–1962", "Quicksort", "e5_10_quicksort", "Quicksort"),
    (11, "avl-trees", "AVL Trees", "1962", "AVL trees", "e5_11_avl", "AvlTrees"),
    (12, "heapsort", "Heapsort and the Heap", "1964", "Heapsort", "e5_12_heapsort", "Heapsort"),
    (13, "matching", "Edmonds's Matching", "1965", "Edmonds's matching", "e5_13_matching", "Matching"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim of a documented line of descent.
_C = [30, 395, 760]
MAP = dict(
    w=1000, h=840, bw=210, bh=76,
    at={1: (_C[0], 20), 2: (_C[1], 20), 3: (_C[2], 20),
        8: (_C[0], 200), 9: (_C[1], 200), 4: (_C[2], 200),
        5: (_C[0], 380), 10: (_C[1], 380), 6: (_C[2], 380),
        7: (_C[0], 560), 12: (_C[1], 560), 11: (_C[2], 560),
        13: (_C[1], 740)},
    color={13: "red"},
    edges=[
        (1, 8, "⊕ routines called by name", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (2, 9, "both from McCulloch and Pitts", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (4, 6, "Luhn's chains", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (5, 7, "⊕ the principle of optimality", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (10, 12, "same task, no bad cases", dict(ports=("bottom", "top"), dashed=True, dx=8, anchor="start")),
        (7, 12, "a heap holds set B", dict(ports=("right", "left"), dashed=True, dy=-10)),
        (6, 11, "⊕ nodes with two links", dict(ports=("bottom", "top"), dx=8, anchor="start")),
    ],
    caption="An arrow means the later development reuses the earlier idea; it is not a claim that one inventor learned "
            "from the other. Dashed lines join related developments: two that start from the same model of the neuron, "
            "Luhn's chained buckets and the lists of cells, two sorting methods for the same task, and the heap that "
            "later kept Dijkstra's set B. Boxes without arrows build on earlier eras: Huffman on Shannon's entropy, "
            "Dijkstra's tree problem on Jarník, and Edmonds's matching on the search for paths in graphs.",
)


def timeline_events():
    return [(t[3], t[4]) for t in TOPICS]
