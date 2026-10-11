"""Era 4 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=4,
    folder="era-04-what-can-be-computed",
    title="What Can Be Computed",
    span="1895 to 1950",
    lede="In the third era, procedures were put into tables and machines. In this one, mathematicians ask what a "
         "procedure is, prove that some questions have none, and build the first computers that keep their programs "
         "in memory.",
    intro="Thirteen steps, from Hilbert's questions of 1900 to Hamming's error-correcting codes of 1950. Along the way, "
          "computation gets a definition, programs become numbers, and machines are set to work on chance, planning, "
          "secrecy and their own mistakes.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "hilberts-questions", "Hilbert's Questions", "1900–1928", "Hilbert's questions", "e4_01_hilbert", "HilbertsQuestions"),
    (2, "runge-kutta", "Runge–Kutta", "1895–1901", "Runge and Kutta", "e4_02_runge_kutta", "RungeKutta"),
    (3, "markov-chains", "Markov Chains", "1906–1913", "Markov's chains", "e4_03_markov", "MarkovChains"),
    (4, "cheapest-network", "The Cheapest Network", "1926–1930", "Borůvka and Jarník", "e4_04_network", "CheapestNetwork"),
    (5, "godel-numbering", "Gödel's Numbering", "1931", "Gödel's numbering", "e4_05_godel", "GodelNumbering"),
    (6, "lambda-calculus", "Church's Lambda Calculus", "1936", "Church's λ-calculus", "e4_06_lambda", "LambdaCalculus"),
    (7, "turing-machines", "Turing's Machines", "1936", "Turing's machines", "e4_07_turing", "TuringMachines"),
    (8, "breaking-enigma", "Breaking Enigma", "1932–1940", "Breaking Enigma", "e4_08_enigma", "Enigma"),
    (9, "stored-program", "The Stored Program, and Merge Sort", "1945–1948", "The stored program", "e4_09_stored_program", "StoredProgram"),
    (10, "monte-carlo", "Monte Carlo", "1946–1949", "Monte Carlo", "e4_10_monte_carlo", "MonteCarlo"),
    (11, "simplex-method", "The Simplex Method", "1947", "Dantzig's simplex", "e4_11_simplex", "SimplexMethod"),
    (12, "information-theory", "Shannon's Bits", "1937–1948", "Shannon's bits", "e4_12_shannon", "InformationTheory"),
    (13, "hamming-codes", "Hamming's Codes", "1950", "Hamming's codes", "e4_13_hamming", "HammingCodes"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim of a documented line of descent.
_C = [30, 395, 760]
MAP = dict(
    w=1000, h=840, bw=210, bh=76,
    at={2: (_C[0], 20), 1: (_C[1], 20), 3: (_C[2], 20),
        6: (_C[0], 200), 5: (_C[1], 200), 12: (_C[2], 200),
        8: (_C[0], 380), 7: (_C[1], 380), 13: (_C[2], 380),
        4: (_C[0], 560), 9: (_C[1], 560), 10: (_C[2], 560),
        11: (_C[1], 740)},
    color={7: "red"},
    edges=[
        (1, 5, "⊕ formulas as numbers", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (1, 6, "⊕ a definition of process", dict(ports=("bottom:0.15", "top:0.8"), at=0.45, dx=-10, anchor="end")),
        (5, 7, "⊕ the diagonal argument", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (6, 7, "same functions", dict(ports=("right", "left"), dashed=True, dy=-10)),
        (7, 8, "both Turing", dict(ports=("left", "right"), dashed=True, dy=-10)),
        (7, 9, "⊕ the table as data", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (3, 12, "⊕ letter statistics", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (12, 13, "⊕ redundancy", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (9, 10, "both von Neumann", dict(ports=("right", "left"), dashed=True, dy=-10)),
    ],
    caption="An arrow means the later development reuses the earlier idea; it is not a claim that one inventor learned "
            "from the other. Dashed lines join developments by the same person, or (Church and Turing) two definitions "
            "that turned out to describe the same functions. Boxes without arrows build on earlier eras: Runge–Kutta on "
            "Euler's steps, Borůvka on counting structure like Euler's bridges, Shannon also on Boole's algebra, and "
            "the simplex method on elimination.",
)


def timeline_events():
    return [(t[3], t[4]) for t in TOPICS]
