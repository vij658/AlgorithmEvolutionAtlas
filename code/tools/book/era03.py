"""Era 3 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=3,
    folder="era-03-tables-and-machines",
    title="Tables and Machines",
    span="1545 to 1890 CE",
    lede="In the second era, procedures travelled. In this one they are made to run without a thinking person: printed "
         "as tables, built into wheels, turned into rules that correct themselves, and at last written as instructions "
         "for a machine.",
    intro="Thirteen steps, from a cubic equation solved in secret in Renaissance Italy to the 1890 census counted by "
          "electricity. Along the way, logic becomes arithmetic and arithmetic becomes binary.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "cardanos-cubic", "Cardano's Cubic", "1545 CE", "Cardano's cubic", "e3_01_cardano", "CardanoCubic"),
    (2, "logarithms", "Logarithms", "1614–1624", "Napier and Briggs's logarithms", "e3_02_logarithms", "Logarithms"),
    (3, "mechanical-carry", "The Carry, Mechanized", "1623–1694", "Schickard, Pascal, Leibniz", "e3_03_carry", "MechanicalCarry"),
    (4, "problem-of-points", "The Problem of Points", "1654", "Pascal and Fermat's points", "e3_04_points", "ProblemOfPoints"),
    (5, "newtons-method", "Newton's Method", "1669–1740", "Newton's method", "e3_05_newton", "NewtonsMethod"),
    (6, "binary-arithmetic", "Binary Arithmetic", "1703", "Leibniz's binary", "e3_06_binary", "BinaryArithmetic"),
    (7, "konigsberg-bridges", "The Bridges of Königsberg", "1736", "Euler's bridges", "e3_07_bridges", "KonigsbergBridges"),
    (8, "least-squares", "Least Squares, and the Lost Planet", "1801–1809", "Least squares", "e3_08_least_squares", "LeastSquares"),
    (9, "gauss-fft", "Gauss's Fast Fourier Transform", "1805", "Gauss's FFT", "e3_09_fft", "GaussFFT"),
    (10, "difference-engine", "Babbage's Difference Engine", "1822", "Babbage's difference engine", "e3_10_difference_engine", "DifferenceEngine"),
    (11, "note-g", "Lovelace's Note G", "1843", "Lovelace's Note G", "e3_11_note_g", "NoteG"),
    (12, "boolean-algebra", "Boole's Algebra of Logic", "1847–1854", "Boole's algebra", "e3_12_boole", "BooleanAlgebra"),
    (13, "hollerith-tabulator", "Hollerith's Tabulator", "1890", "Hollerith's tabulator", "e3_13_hollerith", "HollerithTabulator"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim of a documented line of descent.
_C = [30, 395, 760]
MAP = dict(
    w=1000, h=840, bw=210, bh=76,
    at={2: (_C[0], 20), 3: (_C[1], 20), 6: (_C[2], 20),
        10: (_C[0], 200), 13: (_C[1], 200), 12: (_C[2], 200),
        11: (_C[0], 380), 4: (_C[1], 380), 1: (_C[2], 380),
        5: (_C[0], 560), 8: (_C[1], 560), 9: (_C[2], 560),
        7: (_C[1], 740)},
    color={11: "red"},
    edges=[
        (2, 10, "⊕ printed tables", dict(ports=("bottom", "top"), dx=-8, anchor="end")),
        (3, 10, "⊕ wheels that carry", dict(ports=("bottom:0.2", "top:0.8"), at=0.6, dx=-12, dy=14, anchor="end")),
        (3, 13, "⊕ counting dials", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (3, 6, "both Leibniz", dict(ports=("right", "left"), dashed=True, dy=-10)),
        (6, 12, "⊕ two values", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (10, 11, "⊕ cards and a store", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (4, 8, "⊕ probability of errors", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (8, 9, "⊕ fitting observations", dict(ports=("right", "left"), dy=-10)),
    ],
    caption="An arrow means the later development reuses the earlier idea; it is not a claim that one inventor learned "
            "from the other. The dashed line joins two developments by the same person. Boxes without arrows build on "
            "earlier eras: Cardano on al-jabr, Newton on digit-by-digit roots, Euler on nothing but counting.",
)


def timeline_events():
    return [(t[3], t[4]) for t in TOPICS]
