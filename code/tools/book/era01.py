"""Era 1 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=1,
    folder="era-01-the-first-algorithms",
    title="The First Algorithms",
    span="c. 44,000 years ago to c. 240 BCE",
    lede="Before writing, people cut notches in bone. By the time they built libraries, they had written down procedures that work for any number.",
    intro="Nine steps, from a notched bone to a method for listing primes. Each one answered a pain the step before it "
          "left behind. Several still run, almost unchanged, inside the machines of 2026.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "tally-marks", "Tally Marks", "c. 44,000–20,000 years ago", "Notched bones", "t01_tally", "TallyMarks"),
    (2, "grouping-and-the-first-carry", "Grouping and the First Carry", "c. 3000 BCE", "Written numerals and the first carry", "t02_grouping", "GroupingAndCarry"),
    (3, "babylonian-place-value", "Babylonian Place Value", "c. 1800 BCE", "Babylonian place value and tables", "t03_babylon", "BabylonianPlaceValue"),
    (4, "square-root-of-two", "The Square Root of Two", "c. 1800–1600 BCE", "√2 on the tablet YBC 7289", "t04_sqrt2", "SquareRootOfTwo"),
    (5, "egyptian-doubling", "Egyptian Doubling", "c. 1550 BCE", "Egyptian multiplication by doubling", "t05_doubling", "EgyptianDoubling"),
    (6, "counting-boards", "Counting Boards", "c. 300 BCE", "Counting boards and the abacus", "t06_boards", "CountingBoard"),
    (7, "euclids-algorithm", "Euclid's Algorithm", "c. 300 BCE", "Euclid's algorithm", "t07_euclid", "EuclidsAlgorithm"),
    (8, "archimedes-pi", "Archimedes Squeezes Pi", "c. 250 BCE", "Archimedes squeezes π", "t08_archimedes", "ArchimedesPi"),
    (9, "sieve-of-eratosthenes", "The Sieve of Eratosthenes", "c. 240 BCE", "The sieve of Eratosthenes", "t09_sieve", "SieveOfEratosthenes"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim that one culture learned it from another.
_L, _M, _R = 30, 395, 760
MAP = dict(
    w=1000, h=716, bw=210, bh=76,
    at={1: (_M, 20), 2: (_M, 150), 3: (_L, 300), 5: (_M, 300), 6: (_R, 300),
        4: (_L, 460), 7: (_M, 460), 9: (_R, 460), 8: (212, 620)},
    color={7: "red"},
    edges=[
        (1, 2, "⊕ bundle the marks", dict(ports=("bottom", "top"), dx=10, dy=5, anchor="start")),
        (2, 3, "⊕ position carries the group", dict(ports=("bottom", "top"), at=0.62)),
        (2, 5, "⊕ double and add", dict(ports=("bottom", "top"), dx=10, dy=5, anchor="start")),
        (2, 6, "⊕ counters in columns", dict(ports=("bottom", "top"), at=0.72)),
        (3, 4, "⊕ base-60 fractions", dict(ports=("bottom", "top"), dx=10, dy=5, anchor="start")),
        (5, 7, "⊕ how many times does one fit?", dict(ports=("bottom", "top"), dx=10, dy=5, anchor="start")),
        (7, 9, "⊕ primes, Elements VII", dict(ports=("right", "left"), dy=-10, dashed=True)),
        (4, 8, "⊕ roots trapped both ways", dict(ports=("bottom", "top"), dx=-8, dy=5, anchor="end")),
        (7, 8, "⊕ exhaustion, Elements XII", dict(ports=("bottom", "top"), dx=8, dy=5, anchor="start")),
    ],
    caption="An arrow means the later development reuses the earlier idea. It does not claim one culture learned it "
            "from another; where a borrowing is documented, the topic page says so. The dashed arrow is a shared "
            "source (Euclid's Elements), not a shared procedure.",
)


def timeline_events():
    return [(t[3].replace("–20,000 years ago", " years ago"), t[4]) for t in TOPICS]
